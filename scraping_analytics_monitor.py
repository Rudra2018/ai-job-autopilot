#!/usr/bin/env python3
"""
Scraping Analytics & Monitoring System
Real-time monitoring, analytics, and performance tracking for job scraping pipeline
"""

import asyncio
import json
import os
import sqlite3
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict, deque
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests
import psutil

@dataclass
class ScrapingMetrics:
    session_id: str
    timestamp: str
    platform: str
    jobs_found: int
    jobs_processed: int
    success_rate: float
    avg_response_time: float
    errors_count: int
    blocked_count: int
    captcha_count: int
    proxy_rotations: int
    memory_usage_mb: float
    cpu_usage_percent: float

@dataclass
class ApplicationMetrics:
    session_id: str
    timestamp: str
    jobs_applied: int
    applications_successful: int
    applications_failed: int
    forms_filled: int
    files_uploaded: int
    avg_form_fill_time: float
    success_rate: float

@dataclass
class SystemAlert:
    alert_id: str
    timestamp: str
    severity: str  # info, warning, error, critical
    category: str  # performance, error, detection, system
    message: str
    platform: Optional[str] = None
    resolved: bool = False
    resolution_time: Optional[str] = None

class ScrapingAnalyticsMonitor:
    """Comprehensive monitoring and analytics system"""
    
    def __init__(self, db_path: str = "data/analytics/scraping_analytics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Metrics storage
        self.scraping_metrics_buffer = deque(maxlen=1000)
        self.application_metrics_buffer = deque(maxlen=1000)
        self.alerts_buffer = deque(maxlen=500)
        
        # Performance tracking
        self.platform_stats = defaultdict(lambda: {
            'total_jobs': 0,
            'success_count': 0,
            'error_count': 0,
            'avg_response_time': 0,
            'last_success': None
        })
        
        # Real-time monitoring
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Alert thresholds
        self.alert_thresholds = {
            'error_rate': 0.3,  # 30% error rate
            'response_time': 10.0,  # 10 seconds
            'memory_usage': 80.0,  # 80% memory usage
            'cpu_usage': 90.0,  # 90% CPU usage
            'blocked_rate': 0.2,  # 20% blocked requests
            'success_rate_min': 0.5  # Minimum 50% success rate
        }
        
        # Notification settings
        self.notification_config = self._load_notification_config()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _init_database(self):
        """Initialize SQLite database for analytics"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.execute('PRAGMA journal_mode=WAL')  # Better concurrency
        
        # Create tables
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS scraping_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                platform TEXT NOT NULL,
                jobs_found INTEGER NOT NULL,
                jobs_processed INTEGER NOT NULL,
                success_rate REAL NOT NULL,
                avg_response_time REAL NOT NULL,
                errors_count INTEGER NOT NULL,
                blocked_count INTEGER NOT NULL,
                captcha_count INTEGER NOT NULL,
                proxy_rotations INTEGER NOT NULL,
                memory_usage_mb REAL NOT NULL,
                cpu_usage_percent REAL NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS application_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                jobs_applied INTEGER NOT NULL,
                applications_successful INTEGER NOT NULL,
                applications_failed INTEGER NOT NULL,
                forms_filled INTEGER NOT NULL,
                files_uploaded INTEGER NOT NULL,
                avg_form_fill_time REAL NOT NULL,
                success_rate REAL NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS system_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL UNIQUE,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                message TEXT NOT NULL,
                platform TEXT,
                resolved INTEGER DEFAULT 0,
                resolution_time TEXT
            );
            
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                total_jobs_scraped INTEGER NOT NULL,
                total_applications INTEGER NOT NULL,
                platforms_active INTEGER NOT NULL,
                avg_success_rate REAL NOT NULL,
                total_errors INTEGER NOT NULL,
                avg_response_time REAL NOT NULL
            );
            
            CREATE INDEX IF NOT EXISTS idx_scraping_timestamp ON scraping_metrics(timestamp);
            CREATE INDEX IF NOT EXISTS idx_scraping_platform ON scraping_metrics(platform);
            CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON system_alerts(timestamp);
            CREATE INDEX IF NOT EXISTS idx_alerts_severity ON system_alerts(severity);
        """)
        
        self.conn.commit()
        self.logger.info("✅ Analytics database initialized")
    
    def _load_notification_config(self) -> Dict:
        """Load notification configuration"""
        config_path = Path("config/notification_config.json")
        
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        
        # Default configuration
        return {
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'recipients': []
            },
            'slack': {
                'enabled': False,
                'webhook_url': ''
            },
            'desktop': {
                'enabled': True
            }
        }
    
    def record_scraping_metrics(self, metrics: ScrapingMetrics):
        """Record scraping metrics"""
        # Add to buffer
        self.scraping_metrics_buffer.append(metrics)
        
        # Update platform stats
        platform = metrics.platform
        stats = self.platform_stats[platform]
        
        stats['total_jobs'] += metrics.jobs_found
        stats['success_count'] += metrics.jobs_processed
        stats['error_count'] += metrics.errors_count
        
        # Update average response time
        if stats['avg_response_time'] == 0:
            stats['avg_response_time'] = metrics.avg_response_time
        else:
            stats['avg_response_time'] = (stats['avg_response_time'] + metrics.avg_response_time) / 2
        
        stats['last_success'] = metrics.timestamp
        
        # Insert into database
        try:
            self.conn.execute("""
                INSERT INTO scraping_metrics (
                    session_id, timestamp, platform, jobs_found, jobs_processed,
                    success_rate, avg_response_time, errors_count, blocked_count,
                    captcha_count, proxy_rotations, memory_usage_mb, cpu_usage_percent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.session_id, metrics.timestamp, metrics.platform,
                metrics.jobs_found, metrics.jobs_processed, metrics.success_rate,
                metrics.avg_response_time, metrics.errors_count, metrics.blocked_count,
                metrics.captcha_count, metrics.proxy_rotations, metrics.memory_usage_mb,
                metrics.cpu_usage_percent
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error recording scraping metrics: {e}")
        
        # Check for alerts
        self._check_scraping_alerts(metrics)
    
    def record_application_metrics(self, metrics: ApplicationMetrics):
        """Record application metrics"""
        # Add to buffer
        self.application_metrics_buffer.append(metrics)
        
        # Insert into database
        try:
            self.conn.execute("""
                INSERT INTO application_metrics (
                    session_id, timestamp, jobs_applied, applications_successful,
                    applications_failed, forms_filled, files_uploaded,
                    avg_form_fill_time, success_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.session_id, metrics.timestamp, metrics.jobs_applied,
                metrics.applications_successful, metrics.applications_failed,
                metrics.forms_filled, metrics.files_uploaded,
                metrics.avg_form_fill_time, metrics.success_rate
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error recording application metrics: {e}")
        
        # Check for alerts
        self._check_application_alerts(metrics)
    
    def _check_scraping_alerts(self, metrics: ScrapingMetrics):
        """Check scraping metrics for alert conditions"""
        alerts = []
        
        # High error rate
        if metrics.success_rate < self.alert_thresholds['success_rate_min']:
            alerts.append(SystemAlert(
                alert_id=f"low_success_{metrics.platform}_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity="warning",
                category="performance",
                message=f"Low success rate on {metrics.platform}: {metrics.success_rate:.1%}",
                platform=metrics.platform
            ))
        
        # High response time
        if metrics.avg_response_time > self.alert_thresholds['response_time']:
            alerts.append(SystemAlert(
                alert_id=f"slow_response_{metrics.platform}_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity="warning",
                category="performance",
                message=f"Slow response time on {metrics.platform}: {metrics.avg_response_time:.1f}s",
                platform=metrics.platform
            ))
        
        # High blocked rate
        if metrics.jobs_processed > 0:
            blocked_rate = metrics.blocked_count / metrics.jobs_processed
            if blocked_rate > self.alert_thresholds['blocked_rate']:
                alerts.append(SystemAlert(
                    alert_id=f"blocked_requests_{metrics.platform}_{int(time.time())}",
                    timestamp=metrics.timestamp,
                    severity="error",
                    category="detection",
                    message=f"High blocked rate on {metrics.platform}: {blocked_rate:.1%}",
                    platform=metrics.platform
                ))
        
        # High system resource usage
        if metrics.memory_usage_mb > self.alert_thresholds['memory_usage']:
            alerts.append(SystemAlert(
                alert_id=f"high_memory_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity="warning",
                category="system",
                message=f"High memory usage: {metrics.memory_usage_mb:.1f}MB"
            ))
        
        if metrics.cpu_usage_percent > self.alert_thresholds['cpu_usage']:
            alerts.append(SystemAlert(
                alert_id=f"high_cpu_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity="warning",
                category="system",
                message=f"High CPU usage: {metrics.cpu_usage_percent:.1f}%"
            ))
        
        # Record alerts
        for alert in alerts:
            self._record_alert(alert)
    
    def _check_application_alerts(self, metrics: ApplicationMetrics):
        """Check application metrics for alert conditions"""
        if metrics.success_rate < 0.5 and metrics.jobs_applied > 5:
            alert = SystemAlert(
                alert_id=f"app_low_success_{int(time.time())}",
                timestamp=metrics.timestamp,
                severity="warning",
                category="performance",
                message=f"Low application success rate: {metrics.success_rate:.1%}"
            )
            self._record_alert(alert)
    
    def _record_alert(self, alert: SystemAlert):
        """Record a system alert"""
        self.alerts_buffer.append(alert)
        
        # Insert into database
        try:
            self.conn.execute("""
                INSERT OR IGNORE INTO system_alerts (
                    alert_id, timestamp, severity, category, message, platform
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_id, alert.timestamp, alert.severity,
                alert.category, alert.message, alert.platform
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error recording alert: {e}")
        
        # Send notifications
        asyncio.create_task(self._send_alert_notification(alert))
        
        self.logger.warning(f"🚨 ALERT: {alert.message}")
    
    async def _send_alert_notification(self, alert: SystemAlert):
        """Send alert notifications"""
        try:
            # Desktop notification
            if self.notification_config['desktop']['enabled']:
                self._send_desktop_notification(alert)
            
            # Email notification
            if self.notification_config['email']['enabled']:
                await self._send_email_notification(alert)
            
            # Slack notification
            if self.notification_config['slack']['enabled']:
                await self._send_slack_notification(alert)
                
        except Exception as e:
            self.logger.error(f"Error sending alert notification: {e}")
    
    def _send_desktop_notification(self, alert: SystemAlert):
        """Send desktop notification"""
        try:
            import plyer
            plyer.notification.notify(
                title=f"Job Scraper Alert - {alert.severity.upper()}",
                message=alert.message,
                timeout=10
            )
        except ImportError:
            # Fallback to system notification
            try:
                os.system(f'notify-send "Job Scraper Alert" "{alert.message}"')
            except:
                pass
    
    async def _send_email_notification(self, alert: SystemAlert):
        """Send email notification"""
        try:
            config = self.notification_config['email']
            
            msg = MimeMultipart()
            msg['From'] = config['username']
            msg['To'] = ', '.join(config['recipients'])
            msg['Subject'] = f"Job Scraper Alert - {alert.severity.upper()}"
            
            body = f"""
            Alert Details:
            - Time: {alert.timestamp}
            - Severity: {alert.severity.upper()}
            - Category: {alert.category}
            - Platform: {alert.platform or 'System'}
            - Message: {alert.message}
            
            This is an automated alert from the Job Application Scraper.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"Error sending email notification: {e}")
    
    async def _send_slack_notification(self, alert: SystemAlert):
        """Send Slack notification"""
        try:
            webhook_url = self.notification_config['slack']['webhook_url']
            
            # Color mapping for severity
            colors = {
                'info': '#36a64f',
                'warning': '#ff9500',
                'error': '#ff0000',
                'critical': '#8b0000'
            }
            
            payload = {
                'attachments': [
                    {
                        'color': colors.get(alert.severity, '#36a64f'),
                        'title': f"Job Scraper Alert - {alert.severity.upper()}",
                        'fields': [
                            {'title': 'Message', 'value': alert.message, 'short': False},
                            {'title': 'Platform', 'value': alert.platform or 'System', 'short': True},
                            {'title': 'Category', 'value': alert.category, 'short': True},
                            {'title': 'Time', 'value': alert.timestamp, 'short': True}
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                await session.post(webhook_url, json=payload)
                
        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {e}")
    
    def start_real_time_monitoring(self):
        """Start real-time monitoring thread"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("🔍 Real-time monitoring started")
    
    def stop_real_time_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("⏹️ Real-time monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                
                # Check for system alerts
                self._check_system_health(system_metrics)
                
                # Generate periodic summaries
                self._generate_periodic_summary()
                
                # Sleep for monitoring interval
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _collect_system_metrics(self) -> Dict:
        """Collect current system metrics"""
        return {
            'memory_usage_mb': psutil.virtual_memory().used / (1024 * 1024),
            'memory_percent': psutil.virtual_memory().percent,
            'cpu_percent': psutil.cpu_percent(interval=1),
            'disk_usage': psutil.disk_usage('/').percent,
            'active_connections': len(psutil.net_connections()),
            'timestamp': datetime.now().isoformat()
        }
    
    def _check_system_health(self, metrics: Dict):
        """Check system health and generate alerts"""
        # Memory usage
        if metrics['memory_percent'] > 85:
            alert = SystemAlert(
                alert_id=f"system_memory_{int(time.time())}",
                timestamp=metrics['timestamp'],
                severity="warning",
                category="system",
                message=f"High system memory usage: {metrics['memory_percent']:.1f}%"
            )
            self._record_alert(alert)
        
        # CPU usage
        if metrics['cpu_percent'] > 90:
            alert = SystemAlert(
                alert_id=f"system_cpu_{int(time.time())}",
                timestamp=metrics['timestamp'],
                severity="warning",
                category="system",
                message=f"High system CPU usage: {metrics['cpu_percent']:.1f}%"
            )
            self._record_alert(alert)
    
    def _generate_periodic_summary(self):
        """Generate periodic summary of activities"""
        # This runs every monitoring cycle, but only generates summaries periodically
        now = datetime.now()
        
        # Generate daily summary if it's a new day
        today = now.strftime('%Y-%m-%d')
        
        # Check if we already have today's summary
        cursor = self.conn.execute(
            "SELECT COUNT(*) FROM daily_summaries WHERE date = ?",
            (today,)
        )
        
        if cursor.fetchone()[0] == 0:  # No summary for today yet
            self._generate_daily_summary(today)
    
    def _generate_daily_summary(self, date: str):
        """Generate daily summary"""
        try:
            # Get metrics for the day
            cursor = self.conn.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    SUM(jobs_found) as total_jobs,
                    AVG(success_rate) as avg_success_rate,
                    SUM(errors_count) as total_errors,
                    AVG(avg_response_time) as avg_response_time,
                    COUNT(DISTINCT platform) as platforms_active
                FROM scraping_metrics 
                WHERE DATE(timestamp) = ?
            """, (date,))
            
            scraping_data = cursor.fetchone()
            
            cursor = self.conn.execute("""
                SELECT SUM(jobs_applied) as total_applications
                FROM application_metrics 
                WHERE DATE(timestamp) = ?
            """, (date,))
            
            app_data = cursor.fetchone()
            
            if scraping_data and scraping_data[0] > 0:  # Have data for the day
                self.conn.execute("""
                    INSERT INTO daily_summaries (
                        date, total_jobs_scraped, total_applications, platforms_active,
                        avg_success_rate, total_errors, avg_response_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    date,
                    scraping_data[1] or 0,  # total_jobs
                    app_data[0] or 0,       # total_applications
                    scraping_data[5] or 0,  # platforms_active
                    scraping_data[2] or 0,  # avg_success_rate
                    scraping_data[4] or 0,  # total_errors
                    scraping_data[3] or 0   # avg_response_time
                ))
                
                self.conn.commit()
                self.logger.info(f"📊 Generated daily summary for {date}")
                
        except Exception as e:
            self.logger.error(f"Error generating daily summary: {e}")
    
    def generate_analytics_report(self, days: int = 7) -> Dict:
        """Generate comprehensive analytics report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'scraping_summary': {},
            'application_summary': {},
            'platform_performance': {},
            'alerts_summary': {},
            'trends': {}
        }
        
        try:
            # Scraping summary
            cursor = self.conn.execute("""
                SELECT 
                    COUNT(*) as sessions,
                    SUM(jobs_found) as total_jobs_found,
                    SUM(jobs_processed) as total_jobs_processed,
                    AVG(success_rate) as avg_success_rate,
                    AVG(avg_response_time) as avg_response_time,
                    SUM(errors_count) as total_errors
                FROM scraping_metrics
                WHERE timestamp >= ?
            """, (start_date.isoformat(),))
            
            scraping_data = cursor.fetchone()
            
            report['scraping_summary'] = {
                'sessions': scraping_data[0] or 0,
                'jobs_found': scraping_data[1] or 0,
                'jobs_processed': scraping_data[2] or 0,
                'success_rate': round((scraping_data[3] or 0), 3),
                'avg_response_time': round((scraping_data[4] or 0), 2),
                'total_errors': scraping_data[5] or 0
            }
            
            # Application summary
            cursor = self.conn.execute("""
                SELECT 
                    COUNT(*) as sessions,
                    SUM(jobs_applied) as total_applied,
                    SUM(applications_successful) as total_successful,
                    AVG(success_rate) as avg_success_rate
                FROM application_metrics
                WHERE timestamp >= ?
            """, (start_date.isoformat(),))
            
            app_data = cursor.fetchone()
            
            report['application_summary'] = {
                'sessions': app_data[0] or 0,
                'jobs_applied': app_data[1] or 0,
                'applications_successful': app_data[2] or 0,
                'success_rate': round((app_data[3] or 0), 3)
            }
            
            # Platform performance
            cursor = self.conn.execute("""
                SELECT 
                    platform,
                    COUNT(*) as sessions,
                    SUM(jobs_found) as jobs_found,
                    AVG(success_rate) as success_rate,
                    AVG(avg_response_time) as response_time
                FROM scraping_metrics
                WHERE timestamp >= ?
                GROUP BY platform
                ORDER BY jobs_found DESC
            """, (start_date.isoformat(),))
            
            platform_data = cursor.fetchall()
            
            report['platform_performance'] = {}
            for row in platform_data:
                report['platform_performance'][row[0]] = {
                    'sessions': row[1],
                    'jobs_found': row[2] or 0,
                    'success_rate': round((row[3] or 0), 3),
                    'avg_response_time': round((row[4] or 0), 2)
                }
            
            # Alerts summary
            cursor = self.conn.execute("""
                SELECT 
                    severity,
                    category,
                    COUNT(*) as count
                FROM system_alerts
                WHERE timestamp >= ?
                GROUP BY severity, category
            """, (start_date.isoformat(),))
            
            alert_data = cursor.fetchall()
            
            report['alerts_summary'] = {}
            for row in alert_data:
                key = f"{row[0]}_{row[1]}"
                report['alerts_summary'][key] = row[2]
            
        except Exception as e:
            self.logger.error(f"Error generating analytics report: {e}")
        
        return report
    
    def create_performance_dashboard(self, days: int = 7) -> str:
        """Create HTML performance dashboard"""
        report = self.generate_analytics_report(days)
        
        # Get time series data for charts
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Scraping performance over time
        cursor = self.conn.execute("""
            SELECT 
                DATE(timestamp) as date,
                SUM(jobs_found) as jobs,
                AVG(success_rate) as success_rate,
                AVG(avg_response_time) as response_time
            FROM scraping_metrics
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (start_date.isoformat(),))
        
        daily_data = cursor.fetchall()
        
        # Create plots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Jobs Scraped Daily', 'Success Rate', 'Response Time', 'Platform Distribution'),
            specs=[[{'secondary_y': False}, {'secondary_y': False}],
                   [{'secondary_y': False}, {'type': 'pie'}]]
        )
        
        if daily_data:
            dates = [row[0] for row in daily_data]
            jobs = [row[1] or 0 for row in daily_data]
            success_rates = [row[2] or 0 for row in daily_data]
            response_times = [row[3] or 0 for row in daily_data]
            
            # Jobs scraped
            fig.add_trace(
                go.Scatter(x=dates, y=jobs, mode='lines+markers', name='Jobs Scraped'),
                row=1, col=1
            )
            
            # Success rate
            fig.add_trace(
                go.Scatter(x=dates, y=success_rates, mode='lines+markers', name='Success Rate'),
                row=1, col=2
            )
            
            # Response time
            fig.add_trace(
                go.Scatter(x=dates, y=response_times, mode='lines+markers', name='Response Time'),
                row=2, col=1
            )
        
        # Platform distribution
        if report['platform_performance']:
            platforms = list(report['platform_performance'].keys())
            jobs_by_platform = [report['platform_performance'][p]['jobs_found'] for p in platforms]
            
            fig.add_trace(
                go.Pie(labels=platforms, values=jobs_by_platform, name='Platform Distribution'),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text=f"Job Scraping Analytics Dashboard - Last {days} Days",
            height=800,
            showlegend=False
        )
        
        # Save to HTML file
        output_dir = Path("data/analytics/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = output_dir / f"performance_dashboard_{timestamp}.html"
        
        fig.write_html(str(report_file))
        
        self.logger.info(f"📊 Performance dashboard saved to: {report_file}")
        return str(report_file)
    
    def get_real_time_stats(self) -> Dict:
        """Get real-time statistics"""
        # Recent metrics (last hour)
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as active_sessions,
                SUM(jobs_found) as jobs_in_last_hour,
                AVG(success_rate) as current_success_rate,
                AVG(avg_response_time) as current_response_time
            FROM scraping_metrics
            WHERE timestamp >= ?
        """, (one_hour_ago,))
        
        recent_data = cursor.fetchone()
        
        # Active alerts
        cursor = self.conn.execute("""
            SELECT COUNT(*) FROM system_alerts 
            WHERE resolved = 0
        """)
        
        active_alerts = cursor.fetchone()[0]
        
        # System resources
        system_metrics = self._collect_system_metrics()
        
        return {
            'active_sessions': recent_data[0] or 0,
            'jobs_last_hour': recent_data[1] or 0,
            'current_success_rate': round((recent_data[2] or 0), 3),
            'current_response_time': round((recent_data[3] or 0), 2),
            'active_alerts': active_alerts,
            'system_memory_percent': system_metrics['memory_percent'],
            'system_cpu_percent': system_metrics['cpu_percent'],
            'timestamp': datetime.now().isoformat()
        }
    
    def close(self):
        """Close the monitoring system"""
        self.stop_real_time_monitoring()
        
        if hasattr(self, 'conn'):
            self.conn.close()
        
        self.logger.info("📊 Analytics monitor closed")

async def main():
    """Demo function"""
    print("📊 SCRAPING ANALYTICS & MONITORING SYSTEM")
    print("📈 Real-time monitoring and performance analytics")
    print("="*60)
    
    # Initialize monitor
    monitor = ScrapingAnalyticsMonitor()
    
    # Start real-time monitoring
    monitor.start_real_time_monitoring()
    
    # Generate sample metrics for demo
    sample_metrics = ScrapingMetrics(
        session_id="demo_session_001",
        timestamp=datetime.now().isoformat(),
        platform="linkedin",
        jobs_found=25,
        jobs_processed=20,
        success_rate=0.8,
        avg_response_time=2.5,
        errors_count=2,
        blocked_count=1,
        captcha_count=0,
        proxy_rotations=3,
        memory_usage_mb=450.5,
        cpu_usage_percent=65.2
    )
    
    monitor.record_scraping_metrics(sample_metrics)
    
    # Generate analytics report
    report = monitor.generate_analytics_report(days=1)
    
    print(f"📊 Analytics Report Generated:")
    print(f"   🔍 Scraping sessions: {report['scraping_summary']['sessions']}")
    print(f"   📝 Jobs found: {report['scraping_summary']['jobs_found']}")
    print(f"   📈 Success rate: {report['scraping_summary']['success_rate']:.1%}")
    print(f"   ⏱️  Avg response time: {report['scraping_summary']['avg_response_time']:.2f}s")
    
    # Get real-time stats
    stats = monitor.get_real_time_stats()
    
    print(f"\n⚡ Real-time Stats:")
    print(f"   🔄 Active sessions: {stats['active_sessions']}")
    print(f"   📊 Jobs last hour: {stats['jobs_last_hour']}")
    print(f"   🚨 Active alerts: {stats['active_alerts']}")
    print(f"   💾 Memory usage: {stats['system_memory_percent']:.1f}%")
    print(f"   🖥️  CPU usage: {stats['system_cpu_percent']:.1f}%")
    
    # Create performance dashboard
    dashboard_file = monitor.create_performance_dashboard(days=7)
    print(f"\n📊 Performance dashboard created: {dashboard_file}")
    
    print(f"\n✅ Monitoring system is running!")
    print(f"💡 Features available:")
    print(f"   • Real-time performance monitoring")
    print(f"   • Automatic alert system")
    print(f"   • Analytics reports and dashboards")
    print(f"   • Multi-channel notifications")
    print(f"   • Historical data tracking")
    
    # Cleanup
    monitor.close()

if __name__ == "__main__":
    asyncio.run(main())