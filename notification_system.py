#!/usr/bin/env python3
"""
🤖 AI Job Autopilot - Real-Time Notifications System
Multi-channel notification system with email, desktop, and webhook support
"""

import os
import smtplib
import json
import logging
import requests
import asyncio
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import threading
import queue
import time
from abc import ABC, abstractmethod
import platform

# Desktop notifications
try:
    if platform.system() == "Windows":
        import win10toast
    elif platform.system() == "Darwin":  # macOS
        import pync
    elif platform.system() == "Linux":
        import plyer
    DESKTOP_NOTIFICATIONS_AVAILABLE = True
except ImportError:
    DESKTOP_NOTIFICATIONS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Notification:
    id: str
    title: str
    message: str
    level: str  # info, success, warning, error, critical
    timestamp: datetime
    channel: str = "all"
    data: Dict[str, Any] = None
    read: bool = False
    persistent: bool = False
    action_url: str = ""
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class NotificationChannel:
    name: str
    enabled: bool
    config: Dict[str, Any]
    rate_limit: int = 10  # max notifications per minute
    last_sent: List[datetime] = None

class NotificationHandler(ABC):
    """Abstract base class for notification handlers"""
    
    @abstractmethod
    async def send_notification(self, notification: Notification) -> bool:
        """Send notification through this handler"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this handler is available"""
        pass

class EmailNotificationHandler(NotificationHandler):
    """Email notification handler with HTML templates"""
    
    def __init__(self, config: Dict[str, Any]):
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.email = config.get("email")
        self.password = config.get("password")
        self.sender_name = config.get("sender_name", "AI Job Autopilot")
        self.recipients = config.get("recipients", [])
        
        # Email templates
        self.templates = {
            "session_started": self._get_session_started_template(),
            "session_completed": self._get_session_completed_template(),
            "application_success": self._get_application_success_template(),
            "application_failed": self._get_application_failed_template(),
            "duplicate_detected": self._get_duplicate_detected_template(),
            "error": self._get_error_template(),
            "daily_summary": self._get_daily_summary_template()
        }
    
    def is_available(self) -> bool:
        return bool(self.email and self.password)
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send email notification"""
        if not self.is_available():
            return False
        
        try:
            # Create message
            msg = MimeMultipart()
            msg['From'] = f"{self.sender_name} <{self.email}>"
            msg['Subject'] = f"🤖 {notification.title}"
            
            # Determine recipients
            recipients = self.recipients if self.recipients else [self.email]
            msg['To'] = ", ".join(recipients)
            
            # Get appropriate template
            template_name = notification.data.get("template", "default") if notification.data else "default"
            html_body = self._render_template(template_name, notification)
            
            # Attach body
            msg.attach(MimeText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent: {notification.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _render_template(self, template_name: str, notification: Notification) -> str:
        """Render email template with notification data"""
        
        # Base template
        base_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .level-{level} {{ border-left: 4px solid {level_color}; padding-left: 15px; }}
                .timestamp {{ color: #666; font-size: 12px; margin-top: 10px; }}
                .data {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🤖 AI Job Autopilot</h2>
                    <h3>{title}</h3>
                </div>
                
                <div class="level-{level}">
                    <div class="message">{message}</div>
                    <div class="timestamp">📅 {timestamp}</div>
                    {data_section}
                </div>
                
                <div class="footer">
                    <p>This notification was sent by AI Job Autopilot</p>
                    <p>Powered by Advanced AI • Built for Job Seekers</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Level colors
        level_colors = {
            "info": "#17a2b8",
            "success": "#28a745", 
            "warning": "#ffc107",
            "error": "#dc3545",
            "critical": "#6f42c1"
        }
        
        # Data section
        data_section = ""
        if notification.data:
            data_items = []
            for key, value in notification.data.items():
                if key != "template":
                    data_items.append(f"<strong>{key.replace('_', ' ').title()}:</strong> {value}")
            
            if data_items:
                data_section = f"""
                <div class="data">
                    <h4>📊 Details:</h4>
                    <ul>{''.join(f'<li>{item}</li>' for item in data_items)}</ul>
                </div>
                """
        
        return base_template.format(
            title=notification.title,
            message=notification.message,
            level=notification.level,
            level_color=level_colors.get(notification.level, "#17a2b8"),
            timestamp=notification.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            data_section=data_section
        )
    
    def _get_session_started_template(self) -> str:
        return "session_started"
    
    def _get_session_completed_template(self) -> str:
        return "session_completed"
    
    def _get_application_success_template(self) -> str:
        return "application_success"
    
    def _get_application_failed_template(self) -> str:
        return "application_failed"
    
    def _get_duplicate_detected_template(self) -> str:
        return "duplicate_detected"
    
    def _get_error_template(self) -> str:
        return "error"
    
    def _get_daily_summary_template(self) -> str:
        return "daily_summary"

class DesktopNotificationHandler(NotificationHandler):
    """Desktop notification handler for different OS"""
    
    def __init__(self, config: Dict[str, Any]):
        self.app_name = config.get("app_name", "AI Job Autopilot")
        self.icon_path = config.get("icon_path", "")
    
    def is_available(self) -> bool:
        return DESKTOP_NOTIFICATIONS_AVAILABLE
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send desktop notification"""
        if not self.is_available():
            return False
        
        try:
            system = platform.system()
            
            if system == "Windows":
                return self._send_windows_notification(notification)
            elif system == "Darwin":  # macOS
                return self._send_macos_notification(notification)
            elif system == "Linux":
                return self._send_linux_notification(notification)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
            return False
    
    def _send_windows_notification(self, notification: Notification) -> bool:
        """Send Windows notification"""
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()
            
            # Map levels to icons
            level_icons = {
                "success": "✅",
                "error": "❌", 
                "warning": "⚠️",
                "info": "ℹ️",
                "critical": "🚨"
            }
            
            icon = level_icons.get(notification.level, "📱")
            title = f"{icon} {notification.title}"
            
            toaster.show_toast(
                title=title,
                msg=notification.message,
                duration=10,
                icon_path=self.icon_path if self.icon_path else None
            )
            return True
            
        except Exception as e:
            logger.error(f"Windows notification error: {e}")
            return False
    
    def _send_macos_notification(self, notification: Notification) -> bool:
        """Send macOS notification"""
        try:
            import pync
            
            level_icons = {
                "success": "✅",
                "error": "❌",
                "warning": "⚠️", 
                "info": "ℹ️",
                "critical": "🚨"
            }
            
            icon = level_icons.get(notification.level, "📱")
            title = f"{icon} {notification.title}"
            
            pync.notify(
                notification.message,
                title=title,
                appIcon=self.icon_path if self.icon_path else None,
                sound="default" if notification.level in ["error", "critical"] else None
            )
            return True
            
        except Exception as e:
            logger.error(f"macOS notification error: {e}")
            return False
    
    def _send_linux_notification(self, notification: Notification) -> bool:
        """Send Linux notification"""
        try:
            from plyer import notification as plyer_notification
            
            level_icons = {
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️", 
                "critical": "🚨"
            }
            
            icon = level_icons.get(notification.level, "📱")
            title = f"{icon} {notification.title}"
            
            plyer_notification.notify(
                title=title,
                message=notification.message,
                timeout=10
            )
            return True
            
        except Exception as e:
            logger.error(f"Linux notification error: {e}")
            return False

class WebhookNotificationHandler(NotificationHandler):
    """Webhook notification handler for Slack, Discord, Teams, etc."""
    
    def __init__(self, config: Dict[str, Any]):
        self.webhook_url = config.get("webhook_url")
        self.webhook_type = config.get("type", "generic")  # slack, discord, teams, generic
        self.timeout = config.get("timeout", 10)
    
    def is_available(self) -> bool:
        return bool(self.webhook_url)
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send webhook notification"""
        if not self.is_available():
            return False
        
        try:
            payload = self._create_payload(notification)
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook notification sent: {notification.title}")
                return True
            else:
                logger.error(f"Webhook notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    def _create_payload(self, notification: Notification) -> Dict[str, Any]:
        """Create webhook payload based on type"""
        
        # Level colors and emojis
        level_config = {
            "info": {"color": "#17a2b8", "emoji": "ℹ️"},
            "success": {"color": "#28a745", "emoji": "✅"},
            "warning": {"color": "#ffc107", "emoji": "⚠️"}, 
            "error": {"color": "#dc3545", "emoji": "❌"},
            "critical": {"color": "#6f42c1", "emoji": "🚨"}
        }
        
        config = level_config.get(notification.level, level_config["info"])
        
        if self.webhook_type == "slack":
            return self._create_slack_payload(notification, config)
        elif self.webhook_type == "discord":
            return self._create_discord_payload(notification, config)
        elif self.webhook_type == "teams":
            return self._create_teams_payload(notification, config)
        else:
            return self._create_generic_payload(notification, config)
    
    def _create_slack_payload(self, notification: Notification, config: Dict) -> Dict:
        """Create Slack webhook payload"""
        
        fields = []
        if notification.data:
            for key, value in notification.data.items():
                if key != "template":
                    fields.append({
                        "title": key.replace("_", " ").title(),
                        "value": str(value),
                        "short": len(str(value)) < 30
                    })
        
        return {
            "username": "AI Job Autopilot",
            "icon_emoji": ":robot_face:",
            "attachments": [{
                "color": config["color"],
                "title": f"{config['emoji']} {notification.title}",
                "text": notification.message,
                "fields": fields,
                "footer": "AI Job Autopilot",
                "ts": int(notification.timestamp.timestamp())
            }]
        }
    
    def _create_discord_payload(self, notification: Notification, config: Dict) -> Dict:
        """Create Discord webhook payload"""
        
        fields = []
        if notification.data:
            for key, value in notification.data.items():
                if key != "template":
                    fields.append({
                        "name": key.replace("_", " ").title(),
                        "value": str(value),
                        "inline": len(str(value)) < 30
                    })
        
        return {
            "username": "AI Job Autopilot",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/4712/4712035.png",
            "embeds": [{
                "title": f"{config['emoji']} {notification.title}",
                "description": notification.message,
                "color": int(config["color"].replace("#", ""), 16),
                "fields": fields,
                "footer": {
                    "text": "AI Job Autopilot"
                },
                "timestamp": notification.timestamp.isoformat()
            }]
        }
    
    def _create_teams_payload(self, notification: Notification, config: Dict) -> Dict:
        """Create Microsoft Teams webhook payload"""
        
        facts = []
        if notification.data:
            for key, value in notification.data.items():
                if key != "template":
                    facts.append({
                        "name": key.replace("_", " ").title(),
                        "value": str(value)
                    })
        
        return {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": notification.title,
            "themeColor": config["color"].replace("#", ""),
            "sections": [{
                "activityTitle": f"{config['emoji']} {notification.title}",
                "activitySubtitle": "AI Job Autopilot",
                "text": notification.message,
                "facts": facts
            }]
        }
    
    def _create_generic_payload(self, notification: Notification, config: Dict) -> Dict:
        """Create generic webhook payload"""
        return {
            "title": notification.title,
            "message": notification.message,
            "level": notification.level,
            "timestamp": notification.timestamp.isoformat(),
            "data": notification.data or {},
            "emoji": config["emoji"],
            "color": config["color"]
        }

class TelegramNotificationHandler(NotificationHandler):
    """Telegram bot notification handler"""
    
    def __init__(self, config: Dict[str, Any]):
        self.bot_token = config.get("bot_token")
        self.chat_id = config.get("chat_id")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def is_available(self) -> bool:
        return bool(self.bot_token and self.chat_id)
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send Telegram notification"""
        if not self.is_available():
            return False
        
        try:
            # Level emojis
            level_emojis = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌", 
                "critical": "🚨"
            }
            
            emoji = level_emojis.get(notification.level, "📱")
            
            # Format message
            message = f"{emoji} *{notification.title}*\n\n{notification.message}"
            
            # Add data if present
            if notification.data:
                message += "\n\n📊 *Details:*"
                for key, value in notification.data.items():
                    if key != "template":
                        message += f"\n• *{key.replace('_', ' ').title()}:* {value}"
            
            message += f"\n\n🕐 {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Send message
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Telegram notification sent: {notification.title}")
                return True
            else:
                logger.error(f"Telegram notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

class RealtimeNotificationSystem:
    """Comprehensive real-time notification system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Notification queue
        self.notification_queue = queue.Queue()
        self.notification_history: List[Notification] = []
        
        # Handlers
        self.handlers: Dict[str, NotificationHandler] = {}
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # Worker thread
        self.worker_thread = None
        self.running = False
        
        # Initialize handlers
        self._initialize_handlers()
        
        # Start worker
        self.start_worker()
    
    def _initialize_handlers(self):
        """Initialize notification handlers based on config"""
        
        # Email handler
        email_config = self.config.get("email", {})
        if email_config.get("enabled", False):
            self.handlers["email"] = EmailNotificationHandler(email_config)
        
        # Desktop handler
        desktop_config = self.config.get("desktop", {})
        if desktop_config.get("enabled", True):  # Enabled by default
            self.handlers["desktop"] = DesktopNotificationHandler(desktop_config)
        
        # Webhook handlers
        webhooks = self.config.get("webhooks", [])
        for webhook_config in webhooks:
            if webhook_config.get("enabled", False):
                name = webhook_config.get("name", f"webhook_{len(self.handlers)}")
                self.handlers[name] = WebhookNotificationHandler(webhook_config)
        
        # Telegram handler
        telegram_config = self.config.get("telegram", {})
        if telegram_config.get("enabled", False):
            self.handlers["telegram"] = TelegramNotificationHandler(telegram_config)
        
        logger.info(f"Initialized {len(self.handlers)} notification handlers")
    
    def start_worker(self):
        """Start notification worker thread"""
        if not self.worker_thread or not self.worker_thread.is_alive():
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop)
            self.worker_thread.daemon = True
            self.worker_thread.start()
            logger.info("Notification worker started")
    
    def stop_worker(self):
        """Stop notification worker thread"""
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        logger.info("Notification worker stopped")
    
    def _worker_loop(self):
        """Worker thread main loop"""
        while self.running:
            try:
                # Get notification from queue (with timeout)
                try:
                    notification = self.notification_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process notification
                asyncio.run(self._process_notification(notification))
                
                # Mark as done
                self.notification_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in notification worker: {e}")
    
    async def _process_notification(self, notification: Notification):
        """Process a single notification through all handlers"""
        
        # Add to history
        self.notification_history.append(notification)
        
        # Keep only last 1000 notifications
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
        
        # Send through enabled handlers
        for handler_name, handler in self.handlers.items():
            try:
                # Check rate limit
                if not self._check_rate_limit(handler_name):
                    logger.warning(f"Rate limit exceeded for handler: {handler_name}")
                    continue
                
                # Check if handler is available
                if not handler.is_available():
                    continue
                
                # Send notification
                success = await handler.send_notification(notification)
                
                if success:
                    self._update_rate_limit(handler_name)
                else:
                    # Retry logic
                    notification.retry_count += 1
                    if notification.retry_count < notification.max_retries:
                        # Re-queue for retry after delay
                        threading.Timer(30.0, lambda: self.notification_queue.put(notification)).start()
                
            except Exception as e:
                logger.error(f"Error sending notification through {handler_name}: {e}")
    
    def _check_rate_limit(self, handler_name: str) -> bool:
        """Check if handler is within rate limit"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        if handler_name not in self.rate_limits:
            self.rate_limits[handler_name] = []
        
        # Clean old entries
        self.rate_limits[handler_name] = [
            timestamp for timestamp in self.rate_limits[handler_name]
            if timestamp > minute_ago
        ]
        
        # Check limit (default 10 per minute)
        rate_limit = 10  # Could be configurable per handler
        return len(self.rate_limits[handler_name]) < rate_limit
    
    def _update_rate_limit(self, handler_name: str):
        """Update rate limit tracking"""
        now = datetime.now()
        if handler_name not in self.rate_limits:
            self.rate_limits[handler_name] = []
        self.rate_limits[handler_name].append(now)
    
    def send_notification(self,
                         title: str,
                         message: str,
                         level: str = "info",
                         data: Dict[str, Any] = None,
                         channel: str = "all",
                         persistent: bool = False) -> str:
        """Send notification through the system"""
        
        notification = Notification(
            id=f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            title=title,
            message=message,
            level=level,
            timestamp=datetime.now(),
            channel=channel,
            data=data or {},
            persistent=persistent
        )
        
        # Add to queue
        self.notification_queue.put(notification)
        
        logger.info(f"Notification queued: {title}")
        return notification.id
    
    def send_session_started(self, session_data: Dict[str, Any]) -> str:
        """Send session started notification"""
        return self.send_notification(
            title="Automation Session Started",
            message=f"Started job application session with {session_data.get('max_applications', 0)} max applications",
            level="info",
            data={
                **session_data,
                "template": "session_started"
            }
        )
    
    def send_session_completed(self, session_data: Dict[str, Any]) -> str:
        """Send session completed notification"""
        success_rate = (session_data.get("applications_completed", 0) / 
                       max(session_data.get("applications_attempted", 1), 1)) * 100
        
        return self.send_notification(
            title="Session Completed Successfully",
            message=f"Completed {session_data.get('applications_completed', 0)} applications with {success_rate:.1f}% success rate",
            level="success",
            data={
                **session_data,
                "success_rate": f"{success_rate:.1f}%",
                "template": "session_completed"
            }
        )
    
    def send_application_success(self, job_data: Dict[str, Any]) -> str:
        """Send application success notification"""
        return self.send_notification(
            title="Application Submitted Successfully",
            message=f"Successfully applied to {job_data.get('title', 'Unknown')} at {job_data.get('company', 'Unknown')}",
            level="success",
            data={
                **job_data,
                "template": "application_success"
            }
        )
    
    def send_duplicate_detected(self, job_data: Dict[str, Any], similarity: float) -> str:
        """Send duplicate detected notification"""
        return self.send_notification(
            title="Duplicate Job Detected",
            message=f"Skipped duplicate application: {job_data.get('title', 'Unknown')} (Similarity: {similarity:.1%})",
            level="warning",
            data={
                **job_data,
                "similarity_score": f"{similarity:.1%}",
                "template": "duplicate_detected"
            }
        )
    
    def send_error(self, error_message: str, context: Dict[str, Any] = None) -> str:
        """Send error notification"""
        return self.send_notification(
            title="System Error",
            message=error_message,
            level="error",
            data={
                **(context or {}),
                "template": "error"
            },
            persistent=True
        )
    
    def send_daily_summary(self, summary_data: Dict[str, Any]) -> str:
        """Send daily summary notification"""
        return self.send_notification(
            title="Daily Summary Report",
            message=f"Today: {summary_data.get('total_applications', 0)} applications, {summary_data.get('success_rate', 0):.1f}% success rate",
            level="info",
            data={
                **summary_data,
                "template": "daily_summary"
            }
        )
    
    def get_notification_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent notification history"""
        recent_notifications = self.notification_history[-limit:]
        return [asdict(notification) for notification in recent_notifications]
    
    def get_handler_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all handlers"""
        status = {}
        
        for name, handler in self.handlers.items():
            status[name] = {
                "available": handler.is_available(),
                "type": handler.__class__.__name__,
                "recent_sends": len(self.rate_limits.get(name, [])),
                "rate_limit_remaining": 10 - len(self.rate_limits.get(name, []))
            }
        
        return status
    
    def cleanup(self):
        """Cleanup notification system"""
        self.stop_worker()
        logger.info("Notification system cleanup completed")


def main():
    """Demo the Real-Time Notification System"""
    print("🤖 Real-Time Notification System Demo")
    print("=" * 50)
    
    # Configuration
    config = {
        "desktop": {"enabled": True},
        "email": {
            "enabled": False,  # Set to True and add credentials for testing
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email": "your-email@gmail.com",
            "password": "your-app-password",
            "recipients": ["your-email@gmail.com"]
        },
        "webhooks": [
            {
                "enabled": False,  # Set to True and add webhook URL for testing
                "name": "slack",
                "type": "slack",
                "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
            }
        ],
        "telegram": {
            "enabled": False,  # Set to True and add credentials for testing
            "bot_token": "YOUR_BOT_TOKEN",
            "chat_id": "YOUR_CHAT_ID"
        }
    }
    
    # Initialize notification system
    notification_system = RealtimeNotificationSystem(config)
    
    # Test notifications
    print("\\n📱 Sending test notifications...")
    
    # Test different notification types
    notification_system.send_notification(
        title="System Started",
        message="AI Job Autopilot notification system is now running",
        level="info"
    )
    
    notification_system.send_session_started({
        "session_id": "demo_session",
        "max_applications": 10,
        "job_titles": ["Software Engineer", "Python Developer"]
    })
    
    notification_system.send_application_success({
        "title": "Senior Software Engineer",
        "company": "Google",
        "platform": "LinkedIn"
    })
    
    notification_system.send_duplicate_detected({
        "title": "Software Developer",
        "company": "Microsoft"
    }, 0.95)
    
    notification_system.send_session_completed({
        "session_id": "demo_session",
        "applications_completed": 8,
        "applications_attempted": 10,
        "duration": "25 minutes"
    })
    
    # Wait for notifications to be processed
    time.sleep(5)
    
    # Show handler status
    print("\\n📊 Handler Status:")
    handler_status = notification_system.get_handler_status()
    for handler, status in handler_status.items():
        available = "✅" if status["available"] else "❌"
        print(f"   {available} {handler}: {status['type']}")
    
    # Show notification history
    print("\\n📜 Recent Notifications:")
    history = notification_system.get_notification_history(5)
    for notification in history:
        level_emoji = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        emoji = level_emoji.get(notification["level"], "📝")
        print(f"   {emoji} {notification['title']} ({notification['timestamp']})")
    
    print("\\n🧹 Cleaning up...")
    notification_system.cleanup()
    
    print("✅ Demo completed!")


if __name__ == "__main__":
    main()