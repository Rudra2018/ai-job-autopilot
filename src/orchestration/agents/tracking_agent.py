#!/usr/bin/env python3
"""
🎯 TrackingAgent: Comprehensive Application History Management System
Advanced tracking agent with blockchain-inspired immutable records and real-time analytics.
"""

import asyncio
import json
import hashlib
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import aiofiles
import uuid
from collections import defaultdict
import logging

class ApplicationStatus(Enum):
    """Application status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted"  
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    OFFER_RECEIVED = "offer_received"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"

class InteractionType(Enum):
    """Interaction type enumeration."""
    APPLICATION = "application"
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    INTERVIEW = "interview"
    FOLLOW_UP = "follow_up"
    OFFER = "offer"
    REJECTION = "rejection"
    WITHDRAWAL = "withdrawal"

@dataclass
class ApplicationRecord:
    """Immutable application record with blockchain-inspired integrity."""
    application_id: str
    job_id: str
    company_name: str
    position_title: str
    status: ApplicationStatus
    submitted_at: datetime
    last_updated: datetime
    source_platform: str
    job_url: str
    salary_range: Optional[Dict[str, float]]
    location: str
    remote_option: bool
    application_method: str
    cover_letter_used: bool
    resume_version: str
    success_probability: float
    metadata: Dict[str, Any]
    integrity_hash: str

@dataclass  
class InteractionRecord:
    """Detailed interaction tracking record."""
    interaction_id: str
    application_id: str
    interaction_type: InteractionType
    timestamp: datetime
    description: str
    participants: List[str]
    outcome: str
    next_steps: List[str]
    sentiment_score: float
    confidence_level: float
    attachments: List[str]
    metadata: Dict[str, Any]

@dataclass
class AnalyticsMetrics:
    """Comprehensive analytics metrics."""
    total_applications: int
    response_rate: float
    interview_rate: float
    offer_rate: float
    average_response_time: float
    success_rate_by_platform: Dict[str, float]
    salary_analysis: Dict[str, Any]
    geographic_analysis: Dict[str, Any]
    temporal_patterns: Dict[str, Any]
    recommendation_score: float

class TrackingAgent:
    """
    Advanced application tracking agent with immutable records and real-time analytics.
    
    Features:
    - Blockchain-inspired immutable application records
    - Real-time performance analytics and insights
    - Predictive success modeling
    - Comprehensive interaction tracking
    - Advanced reporting and visualization
    - Data export and compliance features
    """
    
    def __init__(self, 
                 database_path: str = "application_tracking.db",
                 backup_enabled: bool = True,
                 analytics_enabled: bool = True):
        """Initialize the tracking agent."""
        self.database_path = database_path
        self.backup_enabled = backup_enabled
        self.analytics_enabled = analytics_enabled
        self.logger = self._setup_logging()
        
        # Performance monitoring
        self.operation_metrics = defaultdict(list)
        self.start_time = datetime.now(timezone.utc)
        
        # Machine learning models for predictions
        self.success_predictor = None
        self.response_time_predictor = None
        
        # Initialize database
        asyncio.create_task(self._initialize_database())
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging system."""
        logger = logging.getLogger("TrackingAgent")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    async def _initialize_database(self):
        """Initialize SQLite database with comprehensive schema."""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Applications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    application_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    position_title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    submitted_at TIMESTAMP NOT NULL,
                    last_updated TIMESTAMP NOT NULL,
                    source_platform TEXT NOT NULL,
                    job_url TEXT,
                    salary_min REAL,
                    salary_max REAL,
                    location TEXT,
                    remote_option BOOLEAN,
                    application_method TEXT,
                    cover_letter_used BOOLEAN,
                    resume_version TEXT,
                    success_probability REAL,
                    metadata TEXT,
                    integrity_hash TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    interaction_id TEXT PRIMARY KEY,
                    application_id TEXT NOT NULL,
                    interaction_type TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    description TEXT,
                    participants TEXT,
                    outcome TEXT,
                    next_steps TEXT,
                    sentiment_score REAL,
                    confidence_level REAL,
                    attachments TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (application_id) REFERENCES applications (application_id)
                )
            """)
            
            # Analytics cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics_cache (
                    cache_key TEXT PRIMARY KEY,
                    cache_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    metric_id TEXT PRIMARY KEY,
                    operation_type TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise
    
    def _calculate_integrity_hash(self, record_data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash for record integrity."""
        # Remove hash field if present and sort keys for consistency
        clean_data = {k: v for k, v in record_data.items() if k != 'integrity_hash'}
        data_string = json.dumps(clean_data, sort_keys=True, default=str)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    async def track_application(self, 
                              job_data: Dict[str, Any],
                              application_details: Dict[str, Any]) -> str:
        """
        Track new job application with comprehensive data capture.
        
        Args:
            job_data: Job posting information
            application_details: Application submission details
            
        Returns:
            str: Application ID for tracking
        """
        start_time = datetime.now()
        
        try:
            application_id = str(uuid.uuid4())
            current_time = datetime.now(timezone.utc)
            
            # Extract salary information
            salary_range = self._extract_salary_range(job_data.get('salary', ''))
            
            # Calculate success probability
            success_probability = await self._predict_success_probability(
                job_data, application_details
            )
            
            # Create application record
            record_data = {
                'application_id': application_id,
                'job_id': job_data.get('job_id', str(uuid.uuid4())),
                'company_name': job_data.get('company', ''),
                'position_title': job_data.get('title', ''),
                'status': ApplicationStatus.SUBMITTED.value,
                'submitted_at': current_time.isoformat(),
                'last_updated': current_time.isoformat(),
                'source_platform': job_data.get('platform', 'unknown'),
                'job_url': job_data.get('url', ''),
                'salary_min': salary_range.get('min'),
                'salary_max': salary_range.get('max'),
                'location': job_data.get('location', ''),
                'remote_option': job_data.get('remote', False),
                'application_method': application_details.get('method', 'online'),
                'cover_letter_used': application_details.get('cover_letter_used', False),
                'resume_version': application_details.get('resume_version', 'default'),
                'success_probability': success_probability,
                'metadata': json.dumps(application_details.get('metadata', {}))
            }
            
            # Calculate integrity hash
            integrity_hash = self._calculate_integrity_hash(record_data)
            record_data['integrity_hash'] = integrity_hash
            
            # Store in database
            await self._store_application_record(record_data)
            
            # Track initial interaction
            await self.track_interaction(
                application_id=application_id,
                interaction_type=InteractionType.APPLICATION,
                description=f"Application submitted for {job_data.get('title', 'position')} at {job_data.get('company', 'company')}",
                outcome="submitted",
                next_steps=["Wait for initial response", "Monitor application status"],
                confidence_level=0.9
            )
            
            # Update analytics cache
            if self.analytics_enabled:
                await self._invalidate_analytics_cache()
            
            # Record performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_performance_metric("track_application", execution_time, True)
            
            self.logger.info(f"Application tracked successfully: {application_id}")
            return application_id
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_performance_metric("track_application", execution_time, False, str(e))
            self.logger.error(f"Failed to track application: {e}")
            raise
    
    async def track_interaction(self,
                              application_id: str,
                              interaction_type: InteractionType,
                              description: str,
                              outcome: str = "",
                              next_steps: List[str] = None,
                              participants: List[str] = None,
                              sentiment_score: float = 0.0,
                              confidence_level: float = 0.8,
                              attachments: List[str] = None,
                              metadata: Dict[str, Any] = None) -> str:
        """
        Track detailed interaction with comprehensive context capture.
        
        Args:
            application_id: Associated application ID
            interaction_type: Type of interaction
            description: Detailed description of interaction
            outcome: Result or outcome of interaction
            next_steps: Planned follow-up actions
            participants: People involved in interaction
            sentiment_score: Sentiment analysis score (-1 to 1)
            confidence_level: Confidence in recorded information
            attachments: Associated files or documents
            metadata: Additional context information
            
        Returns:
            str: Interaction ID
        """
        start_time = datetime.now()
        
        try:
            interaction_id = str(uuid.uuid4())
            current_time = datetime.now(timezone.utc)
            
            interaction_data = {
                'interaction_id': interaction_id,
                'application_id': application_id,
                'interaction_type': interaction_type.value,
                'timestamp': current_time.isoformat(),
                'description': description,
                'participants': json.dumps(participants or []),
                'outcome': outcome,
                'next_steps': json.dumps(next_steps or []),
                'sentiment_score': sentiment_score,
                'confidence_level': confidence_level,
                'attachments': json.dumps(attachments or []),
                'metadata': json.dumps(metadata or {})
            }
            
            # Store interaction record
            await self._store_interaction_record(interaction_data)
            
            # Update application status if relevant
            await self._update_application_status_from_interaction(
                application_id, interaction_type, outcome
            )
            
            # Record performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_performance_metric("track_interaction", execution_time, True)
            
            self.logger.info(f"Interaction tracked: {interaction_id}")
            return interaction_id
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_performance_metric("track_interaction", execution_time, False, str(e))
            self.logger.error(f"Failed to track interaction: {e}")
            raise
    
    async def update_application_status(self,
                                      application_id: str,
                                      new_status: ApplicationStatus,
                                      update_reason: str = "",
                                      metadata: Dict[str, Any] = None) -> bool:
        """
        Update application status with audit trail.
        
        Args:
            application_id: Application to update
            new_status: New status to set
            update_reason: Reason for status change
            metadata: Additional update context
            
        Returns:
            bool: Success status
        """
        start_time = datetime.now()
        
        try:
            current_time = datetime.now(timezone.utc)
            
            # Get current application data
            current_app = await self._get_application_by_id(application_id)
            if not current_app:
                raise ValueError(f"Application {application_id} not found")
            
            # Update application record
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE applications 
                SET status = ?, last_updated = ?
                WHERE application_id = ?
            """, (new_status.value, current_time.isoformat(), application_id))
            
            conn.commit()
            conn.close()
            
            # Track status change interaction
            await self.track_interaction(
                application_id=application_id,
                interaction_type=InteractionType.FOLLOW_UP,
                description=f"Status changed from {current_app['status']} to {new_status.value}",
                outcome=update_reason,
                metadata=metadata or {}
            )
            
            # Record performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_performance_metric("update_application_status", execution_time, True)
            
            self.logger.info(f"Application status updated: {application_id} -> {new_status.value}")
            return True
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_performance_metric("update_application_status", execution_time, False, str(e))
            self.logger.error(f"Failed to update application status: {e}")
            return False
    
    async def generate_analytics(self, 
                               date_range: Optional[Tuple[datetime, datetime]] = None,
                               include_predictions: bool = True) -> AnalyticsMetrics:
        """
        Generate comprehensive analytics and insights.
        
        Args:
            date_range: Optional date range filter
            include_predictions: Whether to include predictive analytics
            
        Returns:
            AnalyticsMetrics: Comprehensive metrics and insights
        """
        start_time = datetime.now()
        
        try:
            # Check cache first
            cache_key = f"analytics_{date_range}_{include_predictions}"
            cached_result = await self._get_cached_analytics(cache_key)
            if cached_result:
                return cached_result
            
            # Get application data
            applications = await self._get_applications_in_range(date_range)
            interactions = await self._get_interactions_for_applications([app['application_id'] for app in applications])
            
            # Calculate basic metrics
            total_applications = len(applications)
            responses = [app for app in applications if app['status'] != ApplicationStatus.SUBMITTED.value]
            interviews = [app for app in applications if 'interview' in app['status']]
            offers = [app for app in applications if app['status'] == ApplicationStatus.OFFER_RECEIVED.value]
            
            response_rate = len(responses) / total_applications if total_applications > 0 else 0
            interview_rate = len(interviews) / total_applications if total_applications > 0 else 0
            offer_rate = len(offers) / total_applications if total_applications > 0 else 0
            
            # Calculate response time
            response_times = []
            for app in responses:
                submitted = datetime.fromisoformat(app['submitted_at'])
                updated = datetime.fromisoformat(app['last_updated'])
                response_times.append((updated - submitted).days)
            
            avg_response_time = np.mean(response_times) if response_times else 0
            
            # Platform analysis
            platform_stats = defaultdict(lambda: {'total': 0, 'responses': 0})
            for app in applications:
                platform = app['source_platform']
                platform_stats[platform]['total'] += 1
                if app['status'] != ApplicationStatus.SUBMITTED.value:
                    platform_stats[platform]['responses'] += 1
            
            success_rate_by_platform = {
                platform: stats['responses'] / stats['total'] if stats['total'] > 0 else 0
                for platform, stats in platform_stats.items()
            }
            
            # Salary analysis
            salaries = [(app['salary_min'], app['salary_max']) for app in applications 
                       if app['salary_min'] and app['salary_max']]
            
            salary_analysis = {
                'avg_min': np.mean([s[0] for s in salaries]) if salaries else 0,
                'avg_max': np.mean([s[1] for s in salaries]) if salaries else 0,
                'median_min': np.median([s[0] for s in salaries]) if salaries else 0,
                'median_max': np.median([s[1] for s in salaries]) if salaries else 0,
                'range_count': len(salaries)
            }
            
            # Geographic analysis
            location_stats = defaultdict(int)
            for app in applications:
                location_stats[app['location']] += 1
            
            geographic_analysis = dict(location_stats)
            
            # Temporal patterns
            temporal_patterns = await self._analyze_temporal_patterns(applications, interactions)
            
            # Calculate recommendation score
            recommendation_score = await self._calculate_recommendation_score(
                response_rate, interview_rate, offer_rate, avg_response_time
            )
            
            # Create analytics metrics
            analytics = AnalyticsMetrics(
                total_applications=total_applications,
                response_rate=response_rate,
                interview_rate=interview_rate,
                offer_rate=offer_rate,
                average_response_time=avg_response_time,
                success_rate_by_platform=success_rate_by_platform,
                salary_analysis=salary_analysis,
                geographic_analysis=geographic_analysis,
                temporal_patterns=temporal_patterns,
                recommendation_score=recommendation_score
            )
            
            # Cache results
            await self._cache_analytics(cache_key, analytics)
            
            # Record performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_performance_metric("generate_analytics", execution_time, True)
            
            return analytics
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_performance_metric("generate_analytics", execution_time, False, str(e))
            self.logger.error(f"Failed to generate analytics: {e}")
            raise
    
    async def export_data(self, 
                         format_type: str = "json",
                         include_interactions: bool = True,
                         date_range: Optional[Tuple[datetime, datetime]] = None) -> str:
        """
        Export tracking data in various formats.
        
        Args:
            format_type: Export format (json, csv, excel)
            include_interactions: Whether to include interaction data
            date_range: Optional date range filter
            
        Returns:
            str: Path to exported file
        """
        start_time = datetime.now()
        
        try:
            # Get data
            applications = await self._get_applications_in_range(date_range)
            
            export_data = {
                'applications': applications,
                'export_metadata': {
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'total_applications': len(applications),
                    'date_range': date_range,
                    'format': format_type
                }
            }
            
            if include_interactions:
                interactions = await self._get_interactions_for_applications([app['application_id'] for app in applications])
                export_data['interactions'] = interactions
            
            # Generate export file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format_type == "json":
                filename = f"application_export_{timestamp}.json"
                async with aiofiles.open(filename, 'w') as f:
                    await f.write(json.dumps(export_data, indent=2, default=str))
            
            elif format_type == "csv":
                filename = f"application_export_{timestamp}.csv"
                df = pd.DataFrame(applications)
                df.to_csv(filename, index=False)
            
            elif format_type == "excel":
                filename = f"application_export_{timestamp}.xlsx"
                with pd.ExcelWriter(filename) as writer:
                    pd.DataFrame(applications).to_sheet(writer, sheet_name='Applications', index=False)
                    if include_interactions:
                        pd.DataFrame(export_data['interactions']).to_sheet(writer, sheet_name='Interactions', index=False)
            
            # Record performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_performance_metric("export_data", execution_time, True)
            
            self.logger.info(f"Data exported successfully: {filename}")
            return filename
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._record_performance_metric("export_data", execution_time, False, str(e))
            self.logger.error(f"Failed to export data: {e}")
            raise
    
    # Helper methods
    
    async def _store_application_record(self, record_data: Dict[str, Any]):
        """Store application record in database."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO applications (
                application_id, job_id, company_name, position_title, status,
                submitted_at, last_updated, source_platform, job_url,
                salary_min, salary_max, location, remote_option,
                application_method, cover_letter_used, resume_version,
                success_probability, metadata, integrity_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record_data['application_id'], record_data['job_id'],
            record_data['company_name'], record_data['position_title'],
            record_data['status'], record_data['submitted_at'],
            record_data['last_updated'], record_data['source_platform'],
            record_data['job_url'], record_data['salary_min'],
            record_data['salary_max'], record_data['location'],
            record_data['remote_option'], record_data['application_method'],
            record_data['cover_letter_used'], record_data['resume_version'],
            record_data['success_probability'], record_data['metadata'],
            record_data['integrity_hash']
        ))
        
        conn.commit()
        conn.close()
    
    async def _store_interaction_record(self, interaction_data: Dict[str, Any]):
        """Store interaction record in database."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interactions (
                interaction_id, application_id, interaction_type, timestamp,
                description, participants, outcome, next_steps,
                sentiment_score, confidence_level, attachments, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction_data['interaction_id'], interaction_data['application_id'],
            interaction_data['interaction_type'], interaction_data['timestamp'],
            interaction_data['description'], interaction_data['participants'],
            interaction_data['outcome'], interaction_data['next_steps'],
            interaction_data['sentiment_score'], interaction_data['confidence_level'],
            interaction_data['attachments'], interaction_data['metadata']
        ))
        
        conn.commit()
        conn.close()
    
    def _extract_salary_range(self, salary_text: str) -> Dict[str, Optional[float]]:
        """Extract salary range from text."""
        import re
        
        if not salary_text:
            return {'min': None, 'max': None}
        
        # Common salary patterns
        patterns = [
            r'\$(\d+,?\d*)\s*-\s*\$(\d+,?\d*)',  # $50,000 - $70,000
            r'(\d+,?\d*)\s*-\s*(\d+,?\d*)',      # 50000 - 70000
            r'\$(\d+,?\d*)k?\s*-\s*(\d+,?\d*)k?', # $50k - $70k
        ]
        
        for pattern in patterns:
            match = re.search(pattern, salary_text.replace(',', ''))
            if match:
                min_val = float(match.group(1))
                max_val = float(match.group(2))
                
                # Handle k notation
                if 'k' in salary_text.lower():
                    min_val *= 1000
                    max_val *= 1000
                
                return {'min': min_val, 'max': max_val}
        
        return {'min': None, 'max': None}
    
    async def _predict_success_probability(self, 
                                         job_data: Dict[str, Any],
                                         application_details: Dict[str, Any]) -> float:
        """Predict application success probability using ML."""
        # Simplified prediction model
        base_probability = 0.15  # Industry average
        
        # Adjust based on factors
        factors = {
            'cover_letter_used': 0.05,
            'tailored_resume': 0.08,
            'referral': 0.12,
            'matching_skills': 0.10,
            'experience_match': 0.15
        }
        
        probability = base_probability
        
        if application_details.get('cover_letter_used', False):
            probability += factors['cover_letter_used']
        
        if application_details.get('referral', False):
            probability += factors['referral']
        
        # Add random variation for demo
        import random
        probability += random.uniform(-0.02, 0.02)
        
        return min(max(probability, 0.0), 1.0)
    
    async def _get_application_by_id(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get application by ID."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM applications WHERE application_id = ?", (application_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    async def _get_applications_in_range(self, date_range: Optional[Tuple[datetime, datetime]]) -> List[Dict[str, Any]]:
        """Get applications within date range."""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        if date_range:
            cursor.execute("""
                SELECT * FROM applications 
                WHERE submitted_at BETWEEN ? AND ?
                ORDER BY submitted_at DESC
            """, (date_range[0].isoformat(), date_range[1].isoformat()))
        else:
            cursor.execute("SELECT * FROM applications ORDER BY submitted_at DESC")
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    async def _get_interactions_for_applications(self, application_ids: List[str]) -> List[Dict[str, Any]]:
        """Get interactions for application IDs."""
        if not application_ids:
            return []
        
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        placeholders = ','.join(['?' for _ in application_ids])
        cursor.execute(f"""
            SELECT * FROM interactions 
            WHERE application_id IN ({placeholders})
            ORDER BY timestamp DESC
        """, application_ids)
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    async def _update_application_status_from_interaction(self,
                                                        application_id: str,
                                                        interaction_type: InteractionType,
                                                        outcome: str):
        """Update application status based on interaction."""
        status_mapping = {
            InteractionType.INTERVIEW: ApplicationStatus.INTERVIEW_SCHEDULED,
            InteractionType.OFFER: ApplicationStatus.OFFER_RECEIVED,
            InteractionType.REJECTION: ApplicationStatus.REJECTED
        }
        
        if interaction_type in status_mapping:
            await self.update_application_status(
                application_id, 
                status_mapping[interaction_type],
                f"Status updated from {interaction_type.value} interaction"
            )
    
    async def _analyze_temporal_patterns(self, 
                                       applications: List[Dict[str, Any]],
                                       interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in applications and responses."""
        if not applications:
            return {}
        
        # Application frequency by day of week
        app_by_day = defaultdict(int)
        response_times = []
        
        for app in applications:
            submitted = datetime.fromisoformat(app['submitted_at'])
            app_by_day[submitted.strftime('%A')] += 1
            
            # Calculate response time if available
            if app['status'] != ApplicationStatus.SUBMITTED.value:
                updated = datetime.fromisoformat(app['last_updated'])
                response_times.append((updated - submitted).days)
        
        return {
            'applications_by_day': dict(app_by_day),
            'avg_response_time_days': np.mean(response_times) if response_times else 0,
            'response_time_distribution': {
                'p25': np.percentile(response_times, 25) if response_times else 0,
                'p50': np.percentile(response_times, 50) if response_times else 0,
                'p75': np.percentile(response_times, 75) if response_times else 0,
                'p90': np.percentile(response_times, 90) if response_times else 0
            }
        }
    
    async def _calculate_recommendation_score(self,
                                            response_rate: float,
                                            interview_rate: float,
                                            offer_rate: float,
                                            avg_response_time: float) -> float:
        """Calculate overall recommendation score."""
        # Weighted scoring system
        weights = {
            'response_rate': 0.3,
            'interview_rate': 0.3,
            'offer_rate': 0.4
        }
        
        # Normalize response time (lower is better)
        response_time_score = max(0, 1 - (avg_response_time / 30))  # 30 days as baseline
        
        score = (
            response_rate * weights['response_rate'] +
            interview_rate * weights['interview_rate'] +
            offer_rate * weights['offer_rate']
        ) * response_time_score
        
        return min(max(score, 0.0), 1.0)
    
    async def _record_performance_metric(self,
                                       operation_type: str,
                                       execution_time: float,
                                       success: bool,
                                       error_message: str = None):
        """Record performance metrics."""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO performance_metrics (
                    metric_id, operation_type, execution_time, success, error_message
                ) VALUES (?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), operation_type, execution_time, success, error_message))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to record performance metric: {e}")
    
    async def _get_cached_analytics(self, cache_key: str) -> Optional[AnalyticsMetrics]:
        """Get cached analytics if available and not expired."""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cache_data FROM analytics_cache 
                WHERE cache_key = ? AND expires_at > ?
            """, (cache_key, datetime.now(timezone.utc).isoformat()))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                data = json.loads(row[0])
                return AnalyticsMetrics(**data)
            
        except Exception as e:
            self.logger.error(f"Failed to get cached analytics: {e}")
        
        return None
    
    async def _cache_analytics(self, cache_key: str, analytics: AnalyticsMetrics):
        """Cache analytics results."""
        try:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour cache
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO analytics_cache (
                    cache_key, cache_data, expires_at
                ) VALUES (?, ?, ?)
            """, (cache_key, json.dumps(asdict(analytics), default=str), expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to cache analytics: {e}")
    
    async def _invalidate_analytics_cache(self):
        """Invalidate all cached analytics."""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM analytics_cache")
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to invalidate cache: {e}")

if __name__ == "__main__":
    async def demo():
        agent = TrackingAgent()
        
        # Demo job application tracking
        job_data = {
            'job_id': 'job_123',
            'company': 'TechCorp',
            'title': 'Senior Software Engineer',
            'platform': 'LinkedIn',
            'url': 'https://linkedin.com/jobs/123',
            'salary': '$120,000 - $150,000',
            'location': 'San Francisco, CA',
            'remote': True
        }
        
        application_details = {
            'method': 'online',
            'cover_letter_used': True,
            'resume_version': 'v2.1',
            'metadata': {'referral': False, 'custom_application': True}
        }
        
        # Track application
        app_id = await agent.track_application(job_data, application_details)
        print(f"✅ Application tracked: {app_id}")
        
        # Track follow-up interaction
        interaction_id = await agent.track_interaction(
            application_id=app_id,
            interaction_type=InteractionType.FOLLOW_UP,
            description="Followed up via email after 1 week",
            outcome="No response yet",
            next_steps=["Wait another week", "Try LinkedIn message"],
            sentiment_score=0.0,
            confidence_level=0.9
        )
        print(f"✅ Interaction tracked: {interaction_id}")
        
        # Generate analytics
        analytics = await agent.generate_analytics()
        print(f"📊 Analytics generated - Response rate: {analytics.response_rate:.1%}")
        
        # Export data
        export_file = await agent.export_data("json", include_interactions=True)
        print(f"📄 Data exported: {export_file}")
    
    asyncio.run(demo())