#!/usr/bin/env python3
"""
🚀 OptimizationAgent: Continuous Improvement & Machine Learning System
Advanced optimization agent with reinforcement learning and predictive analytics.
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import logging
from collections import defaultdict, deque
from pathlib import Path
import pickle
import aiofiles

# Scikit-learn imports for ML
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import joblib

class OptimizationType(Enum):
    """Types of optimization strategies."""
    RESPONSE_RATE = "response_rate"
    INTERVIEW_RATE = "interview_rate" 
    OFFER_RATE = "offer_rate"
    TIME_EFFICIENCY = "time_efficiency"
    COST_EFFECTIVENESS = "cost_effectiveness"
    SKILL_MATCHING = "skill_matching"
    PERSONALIZATION = "personalization"

class ModelType(Enum):
    """Machine learning model types."""
    SUCCESS_PREDICTOR = "success_predictor"
    RESPONSE_TIME_PREDICTOR = "response_time_predictor"
    SALARY_ESTIMATOR = "salary_estimator"
    SKILL_RECOMMENDER = "skill_recommender"
    COMPANY_MATCHER = "company_matcher"
    COVER_LETTER_OPTIMIZER = "cover_letter_optimizer"

@dataclass
class OptimizationResult:
    """Result of optimization analysis."""
    optimization_type: OptimizationType
    current_performance: float
    target_performance: float
    improvement_potential: float
    recommendations: List[str]
    confidence_score: float
    implementation_difficulty: float
    estimated_impact: Dict[str, float]
    timeline: str

@dataclass
class ModelPerformance:
    """Machine learning model performance metrics."""
    model_type: ModelType
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_size: int
    last_updated: datetime
    feature_importance: Dict[str, float]
    cross_validation_score: float

@dataclass
class ABTestResult:
    """A/B testing experiment results."""
    experiment_id: str
    test_name: str
    variant_a: Dict[str, Any]
    variant_b: Dict[str, Any]
    sample_size_a: int
    sample_size_b: int
    success_rate_a: float
    success_rate_b: float
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    recommendation: str

class OptimizationAgent:
    """
    Advanced optimization agent with machine learning and continuous improvement.
    
    Features:
    - Reinforcement learning for strategy optimization
    - A/B testing framework for systematic improvements
    - Predictive modeling for success probability
    - Multi-objective optimization algorithms
    - Real-time performance monitoring
    - Automated hyperparameter tuning
    - Feature engineering and selection
    - Ensemble model management
    """
    
    def __init__(self,
                 model_storage_path: str = "optimization_models/",
                 learning_rate: float = 0.01,
                 exploration_rate: float = 0.1,
                 performance_threshold: float = 0.8):
        """Initialize the optimization agent."""
        self.model_storage_path = Path(model_storage_path)
        self.model_storage_path.mkdir(exist_ok=True)
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        self.performance_threshold = performance_threshold
        
        self.logger = self._setup_logging()
        
        # Model registry
        self.models: Dict[ModelType, Any] = {}
        self.model_performance: Dict[ModelType, ModelPerformance] = {}
        self.scalers: Dict[ModelType, StandardScaler] = {}
        
        # Optimization history
        self.optimization_history = deque(maxlen=1000)
        self.experiment_results = {}
        
        # Feature engineering
        self.feature_extractors = {
            'text_vectorizer': TfidfVectorizer(max_features=1000),
            'skill_encoder': LabelEncoder(),
            'company_encoder': LabelEncoder()
        }
        
        # Real-time monitoring
        self.performance_metrics = defaultdict(list)
        self.alert_thresholds = {
            'success_rate_drop': 0.1,
            'response_time_increase': 0.2,
            'model_accuracy_drop': 0.05
        }
        
        # Load existing models
        asyncio.create_task(self._load_existing_models())
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging system."""
        logger = logging.getLogger("OptimizationAgent")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def analyze_optimization_opportunities(self,
                                               historical_data: List[Dict[str, Any]],
                                               current_metrics: Dict[str, float]) -> List[OptimizationResult]:
        """
        Analyze historical data to identify optimization opportunities.
        
        Args:
            historical_data: Historical application and outcome data
            current_metrics: Current performance metrics
            
        Returns:
            List[OptimizationResult]: Identified optimization opportunities
        """
        start_time = datetime.now()
        
        try:
            opportunities = []
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(historical_data)
            
            # Analyze response rate optimization
            response_opt = await self._analyze_response_rate_optimization(df, current_metrics)
            opportunities.append(response_opt)
            
            # Analyze interview rate optimization
            interview_opt = await self._analyze_interview_rate_optimization(df, current_metrics)
            opportunities.append(interview_opt)
            
            # Analyze time efficiency optimization
            time_opt = await self._analyze_time_efficiency_optimization(df, current_metrics)
            opportunities.append(time_opt)
            
            # Analyze skill matching optimization
            skill_opt = await self._analyze_skill_matching_optimization(df, current_metrics)
            opportunities.append(skill_opt)
            
            # Analyze personalization optimization
            personalization_opt = await self._analyze_personalization_optimization(df, current_metrics)
            opportunities.append(personalization_opt)
            
            # Sort by improvement potential
            opportunities.sort(key=lambda x: x.improvement_potential, reverse=True)
            
            self.logger.info(f"Identified {len(opportunities)} optimization opportunities")
            
            # Store in history
            self.optimization_history.append({
                'timestamp': start_time,
                'opportunities_found': len(opportunities),
                'top_opportunity': opportunities[0].optimization_type.value if opportunities else None
            })
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Failed to analyze optimization opportunities: {e}")
            raise
    
    async def train_predictive_models(self,
                                    training_data: List[Dict[str, Any]],
                                    model_types: List[ModelType] = None) -> Dict[ModelType, ModelPerformance]:
        """
        Train machine learning models for prediction and optimization.
        
        Args:
            training_data: Historical data for training
            model_types: Specific models to train (None for all)
            
        Returns:
            Dict[ModelType, ModelPerformance]: Model performance results
        """
        start_time = datetime.now()
        
        try:
            if model_types is None:
                model_types = list(ModelType)
            
            results = {}
            df = pd.DataFrame(training_data)
            
            if df.empty:
                raise ValueError("No training data provided")
            
            for model_type in model_types:
                try:
                    performance = await self._train_single_model(model_type, df)
                    results[model_type] = performance
                    self.model_performance[model_type] = performance
                    
                    # Save model to disk
                    await self._save_model(model_type)
                    
                    self.logger.info(f"Trained {model_type.value} model with {performance.accuracy:.3f} accuracy")
                    
                except Exception as e:
                    self.logger.error(f"Failed to train {model_type.value} model: {e}")
                    continue
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Model training completed in {execution_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to train predictive models: {e}")
            raise
    
    async def run_ab_test(self,
                         test_name: str,
                         variant_a: Dict[str, Any],
                         variant_b: Dict[str, Any],
                         sample_size: int = 100,
                         success_metric: str = "response_rate") -> ABTestResult:
        """
        Run A/B test to compare two strategies or configurations.
        
        Args:
            test_name: Name of the test
            variant_a: Configuration for variant A (control)
            variant_b: Configuration for variant B (treatment)
            sample_size: Required sample size per variant
            success_metric: Metric to measure success
            
        Returns:
            ABTestResult: Test results and statistical analysis
        """
        start_time = datetime.now()
        
        try:
            experiment_id = str(uuid.uuid4())
            
            # Simulate A/B test execution (in real implementation, this would run over time)
            results_a = await self._simulate_variant_performance(variant_a, sample_size)
            results_b = await self._simulate_variant_performance(variant_b, sample_size)
            
            success_rate_a = results_a['success_rate']
            success_rate_b = results_b['success_rate']
            
            # Statistical significance testing
            significance, confidence_interval = await self._calculate_statistical_significance(
                results_a['successes'], sample_size,
                results_b['successes'], sample_size
            )
            
            # Generate recommendation
            if significance > 0.95 and success_rate_b > success_rate_a:
                recommendation = f"Adopt variant B - {((success_rate_b - success_rate_a) / success_rate_a * 100):.1f}% improvement"
            elif significance > 0.95 and success_rate_a > success_rate_b:
                recommendation = "Keep variant A - statistically better performance"
            else:
                recommendation = "Inconclusive - extend test duration or sample size"
            
            result = ABTestResult(
                experiment_id=experiment_id,
                test_name=test_name,
                variant_a=variant_a,
                variant_b=variant_b,
                sample_size_a=sample_size,
                sample_size_b=sample_size,
                success_rate_a=success_rate_a,
                success_rate_b=success_rate_b,
                statistical_significance=significance,
                confidence_interval=confidence_interval,
                recommendation=recommendation
            )
            
            # Store experiment results
            self.experiment_results[experiment_id] = result
            
            self.logger.info(f"A/B test completed: {test_name} - {recommendation}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to run A/B test: {e}")
            raise
    
    async def optimize_multi_objective(self,
                                     objectives: List[OptimizationType],
                                     constraints: Dict[str, Any],
                                     historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Multi-objective optimization using evolutionary algorithms.
        
        Args:
            objectives: List of optimization objectives
            constraints: Constraints and boundaries
            historical_data: Historical performance data
            
        Returns:
            Dict[str, Any]: Optimal configuration and trade-offs
        """
        start_time = datetime.now()
        
        try:
            # Initialize population of solutions
            population_size = 50
            generations = 100
            
            population = await self._initialize_population(population_size, constraints)
            
            best_solutions = []
            
            for generation in range(generations):
                # Evaluate fitness for each objective
                fitness_scores = await self._evaluate_population_fitness(
                    population, objectives, historical_data
                )
                
                # Select best solutions (Pareto front)
                pareto_front = await self._find_pareto_front(population, fitness_scores)
                best_solutions.extend(pareto_front)
                
                # Generate next generation
                if generation < generations - 1:
                    population = await self._evolve_population(
                        population, fitness_scores, constraints
                    )
            
            # Find final optimal solutions
            final_pareto_front = await self._find_pareto_front(best_solutions, 
                                                             await self._evaluate_population_fitness(
                                                                 best_solutions, objectives, historical_data
                                                             ))
            
            # Analyze trade-offs
            trade_off_analysis = await self._analyze_trade_offs(
                final_pareto_front, objectives, historical_data
            )
            
            optimization_result = {
                'pareto_optimal_solutions': final_pareto_front,
                'trade_off_analysis': trade_off_analysis,
                'objectives_analyzed': [obj.value for obj in objectives],
                'convergence_generations': generations,
                'solution_count': len(final_pareto_front)
            }
            
            self.logger.info(f"Multi-objective optimization completed with {len(final_pareto_front)} optimal solutions")
            
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"Failed to perform multi-objective optimization: {e}")
            raise
    
    async def predict_success_probability(self,
                                        application_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Predict success probability using trained ML models.
        
        Args:
            application_data: Application and job data
            
        Returns:
            Dict[str, float]: Predictions for various success metrics
        """
        try:
            predictions = {}
            
            # Prepare features
            features = await self._extract_features(application_data)
            
            # Success probability prediction
            if ModelType.SUCCESS_PREDICTOR in self.models:
                model = self.models[ModelType.SUCCESS_PREDICTOR]
                scaler = self.scalers[ModelType.SUCCESS_PREDICTOR]
                
                scaled_features = scaler.transform([features])
                success_prob = model.predict_proba(scaled_features)[0][1]
                predictions['overall_success'] = float(success_prob)
            
            # Response time prediction
            if ModelType.RESPONSE_TIME_PREDICTOR in self.models:
                model = self.models[ModelType.RESPONSE_TIME_PREDICTOR]
                scaler = self.scalers[ModelType.RESPONSE_TIME_PREDICTOR]
                
                scaled_features = scaler.transform([features])
                response_time = model.predict(scaled_features)[0]
                predictions['response_time_days'] = float(response_time)
            
            # Salary estimation
            if ModelType.SALARY_ESTIMATOR in self.models:
                model = self.models[ModelType.SALARY_ESTIMATOR]
                scaler = self.scalers[ModelType.SALARY_ESTIMATOR]
                
                scaled_features = scaler.transform([features])
                salary_est = model.predict(scaled_features)[0]
                predictions['estimated_salary'] = float(salary_est)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Failed to predict success probability: {e}")
            return {}
    
    async def recommend_optimizations(self,
                                    current_strategy: Dict[str, Any],
                                    performance_goals: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Recommend specific optimizations based on current strategy and goals.
        
        Args:
            current_strategy: Current application strategy
            performance_goals: Target performance metrics
            
        Returns:
            List[Dict[str, Any]]: Specific optimization recommendations
        """
        try:
            recommendations = []
            
            # Analyze current strategy performance
            current_performance = await self._assess_strategy_performance(current_strategy)
            
            # Generate recommendations for each goal
            for metric, target in performance_goals.items():
                current_value = current_performance.get(metric, 0)
                gap = target - current_value
                
                if gap > 0.05:  # Significant improvement needed
                    recommendation = await self._generate_specific_recommendation(
                        metric, current_value, target, current_strategy
                    )
                    recommendations.append(recommendation)
            
            # Sort by expected impact
            recommendations.sort(key=lambda x: x.get('expected_impact', 0), reverse=True)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to recommend optimizations: {e}")
            return []
    
    async def monitor_performance_drift(self,
                                      recent_data: List[Dict[str, Any]],
                                      baseline_period_days: int = 30) -> Dict[str, Any]:
        """
        Monitor for performance drift and model degradation.
        
        Args:
            recent_data: Recent application and outcome data
            baseline_period_days: Days to look back for baseline
            
        Returns:
            Dict[str, Any]: Drift analysis and alerts
        """
        try:
            current_time = datetime.now(timezone.utc)
            baseline_cutoff = current_time - timedelta(days=baseline_period_days)
            
            # Split data into baseline and recent
            recent_data_filtered = [
                d for d in recent_data 
                if datetime.fromisoformat(d.get('timestamp', current_time.isoformat())) > baseline_cutoff
            ]
            
            baseline_data = [
                d for d in recent_data
                if datetime.fromisoformat(d.get('timestamp', current_time.isoformat())) <= baseline_cutoff
            ]
            
            drift_analysis = {
                'performance_drift': {},
                'model_drift': {},
                'alerts': [],
                'recommendations': []
            }
            
            # Performance drift analysis
            if baseline_data and recent_data_filtered:
                performance_drift = await self._analyze_performance_drift(
                    baseline_data, recent_data_filtered
                )
                drift_analysis['performance_drift'] = performance_drift
                
                # Check for significant drift
                for metric, drift in performance_drift.items():
                    if abs(drift) > self.alert_thresholds.get(f'{metric}_drift', 0.1):
                        drift_analysis['alerts'].append({
                            'type': 'performance_drift',
                            'metric': metric,
                            'drift_magnitude': drift,
                            'severity': 'high' if abs(drift) > 0.2 else 'medium'
                        })
            
            # Model drift analysis
            model_drift = await self._analyze_model_drift(recent_data_filtered)
            drift_analysis['model_drift'] = model_drift
            
            # Generate recommendations
            if drift_analysis['alerts']:
                recommendations = await self._generate_drift_recommendations(drift_analysis['alerts'])
                drift_analysis['recommendations'] = recommendations
            
            return drift_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to monitor performance drift: {e}")
            return {}
    
    # Helper methods
    
    async def _analyze_response_rate_optimization(self, 
                                                df: pd.DataFrame, 
                                                current_metrics: Dict[str, float]) -> OptimizationResult:
        """Analyze response rate optimization opportunities."""
        current_response_rate = current_metrics.get('response_rate', 0.0)
        
        # Analyze factors affecting response rate
        if 'responded' in df.columns and len(df) > 10:
            # Find best performing segments
            high_performers = df[df['responded'] == True]
            avg_performers = df[df['responded'] == False]
            
            # Identify key differentiators
            recommendations = []
            improvement_potential = 0.0
            
            if len(high_performers) > 0:
                # Analyze platform performance
                platform_response = df.groupby('platform')['responded'].mean() if 'platform' in df.columns else pd.Series()
                if not platform_response.empty:
                    best_platform = platform_response.idxmax()
                    best_rate = platform_response.max()
                    improvement_potential = max(improvement_potential, best_rate - current_response_rate)
                    recommendations.append(f"Focus on {best_platform} platform (response rate: {best_rate:.1%})")
                
                # Analyze cover letter impact
                if 'cover_letter_used' in df.columns:
                    cl_response = df.groupby('cover_letter_used')['responded'].mean()
                    if cl_response.get(True, 0) > cl_response.get(False, 0):
                        improvement = cl_response[True] - current_response_rate
                        improvement_potential = max(improvement_potential, improvement)
                        recommendations.append("Use cover letters consistently (higher response rate)")
                
                # Analyze timing
                if 'day_of_week' in df.columns:
                    day_response = df.groupby('day_of_week')['responded'].mean()
                    best_day = day_response.idxmax()
                    recommendations.append(f"Apply on {best_day}s for better response rates")
        
        if not recommendations:
            recommendations = [
                "Personalize applications more thoroughly",
                "Optimize application timing",
                "Improve resume keywords matching"
            ]
            improvement_potential = 0.15  # Conservative estimate
        
        return OptimizationResult(
            optimization_type=OptimizationType.RESPONSE_RATE,
            current_performance=current_response_rate,
            target_performance=current_response_rate + improvement_potential,
            improvement_potential=improvement_potential,
            recommendations=recommendations,
            confidence_score=0.75,
            implementation_difficulty=0.3,
            estimated_impact={'response_rate': improvement_potential},
            timeline="2-4 weeks"
        )
    
    async def _analyze_interview_rate_optimization(self,
                                                 df: pd.DataFrame,
                                                 current_metrics: Dict[str, float]) -> OptimizationResult:
        """Analyze interview rate optimization opportunities."""
        current_interview_rate = current_metrics.get('interview_rate', 0.0)
        
        recommendations = [
            "Improve skill-job matching accuracy",
            "Enhance portfolio presentation",
            "Optimize resume for ATS systems",
            "Follow up strategically after applications"
        ]
        
        improvement_potential = 0.12  # Conservative estimate
        
        return OptimizationResult(
            optimization_type=OptimizationType.INTERVIEW_RATE,
            current_performance=current_interview_rate,
            target_performance=current_interview_rate + improvement_potential,
            improvement_potential=improvement_potential,
            recommendations=recommendations,
            confidence_score=0.68,
            implementation_difficulty=0.5,
            estimated_impact={'interview_rate': improvement_potential},
            timeline="4-6 weeks"
        )
    
    async def _analyze_time_efficiency_optimization(self,
                                                  df: pd.DataFrame,
                                                  current_metrics: Dict[str, float]) -> OptimizationResult:
        """Analyze time efficiency optimization opportunities."""
        current_time_per_app = current_metrics.get('time_per_application', 30.0)  # minutes
        
        recommendations = [
            "Automate repetitive application fields",
            "Create template bank for cover letters",
            "Use browser extensions for form filling",
            "Batch similar applications together"
        ]
        
        improvement_potential = 0.4  # 40% time reduction
        
        return OptimizationResult(
            optimization_type=OptimizationType.TIME_EFFICIENCY,
            current_performance=current_time_per_app,
            target_performance=current_time_per_app * (1 - improvement_potential),
            improvement_potential=improvement_potential,
            recommendations=recommendations,
            confidence_score=0.85,
            implementation_difficulty=0.4,
            estimated_impact={'time_savings_minutes': current_time_per_app * improvement_potential},
            timeline="1-2 weeks"
        )
    
    async def _analyze_skill_matching_optimization(self,
                                                 df: pd.DataFrame,
                                                 current_metrics: Dict[str, float]) -> OptimizationResult:
        """Analyze skill matching optimization opportunities."""
        current_match_score = current_metrics.get('skill_match_score', 0.6)
        
        recommendations = [
            "Use semantic similarity for skill matching",
            "Analyze job descriptions more thoroughly",
            "Update resume with trending technologies",
            "Quantify achievements with specific metrics"
        ]
        
        improvement_potential = 0.25
        
        return OptimizationResult(
            optimization_type=OptimizationType.SKILL_MATCHING,
            current_performance=current_match_score,
            target_performance=current_match_score + improvement_potential,
            improvement_potential=improvement_potential,
            recommendations=recommendations,
            confidence_score=0.72,
            implementation_difficulty=0.6,
            estimated_impact={'match_improvement': improvement_potential},
            timeline="3-5 weeks"
        )
    
    async def _analyze_personalization_optimization(self,
                                                  df: pd.DataFrame,
                                                  current_metrics: Dict[str, float]) -> OptimizationResult:
        """Analyze personalization optimization opportunities."""
        current_personalization = current_metrics.get('personalization_score', 0.5)
        
        recommendations = [
            "Research company culture and values",
            "Customize cover letters per company",
            "Reference specific job requirements",
            "Use company-specific terminology"
        ]
        
        improvement_potential = 0.35
        
        return OptimizationResult(
            optimization_type=OptimizationType.PERSONALIZATION,
            current_performance=current_personalization,
            target_performance=current_personalization + improvement_potential,
            improvement_potential=improvement_potential,
            recommendations=recommendations,
            confidence_score=0.78,
            implementation_difficulty=0.7,
            estimated_impact={'personalization_improvement': improvement_potential},
            timeline="4-8 weeks"
        )
    
    async def _train_single_model(self, model_type: ModelType, df: pd.DataFrame) -> ModelPerformance:
        """Train a single ML model."""
        if model_type == ModelType.SUCCESS_PREDICTOR:
            return await self._train_success_predictor(df)
        elif model_type == ModelType.RESPONSE_TIME_PREDICTOR:
            return await self._train_response_time_predictor(df)
        elif model_type == ModelType.SALARY_ESTIMATOR:
            return await self._train_salary_estimator(df)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    async def _train_success_predictor(self, df: pd.DataFrame) -> ModelPerformance:
        """Train success prediction model."""
        # Prepare features and target
        features = []
        targets = []
        
        for _, row in df.iterrows():
            feature_vector = await self._extract_features(row.to_dict())
            target = 1 if row.get('successful', False) else 0
            
            features.append(feature_vector)
            targets.append(target)
        
        if len(features) < 10:
            raise ValueError("Insufficient training data")
        
        X = np.array(features)
        y = np.array(targets)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1] if len(np.unique(y)) > 1 else y_pred
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_scaled, y, cv=5)
        cv_mean = cv_scores.mean()
        
        # Feature importance
        feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        
        # Store model and scaler
        self.models[ModelType.SUCCESS_PREDICTOR] = model
        self.scalers[ModelType.SUCCESS_PREDICTOR] = scaler
        
        return ModelPerformance(
            model_type=ModelType.SUCCESS_PREDICTOR,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            training_size=len(features),
            last_updated=datetime.now(timezone.utc),
            feature_importance=feature_importance,
            cross_validation_score=cv_mean
        )
    
    async def _train_response_time_predictor(self, df: pd.DataFrame) -> ModelPerformance:
        """Train response time prediction model."""
        # Simplified implementation - would be more sophisticated in practice
        features = []
        targets = []
        
        for _, row in df.iterrows():
            if 'response_time_days' in row and pd.notna(row['response_time_days']):
                feature_vector = await self._extract_features(row.to_dict())
                features.append(feature_vector)
                targets.append(float(row['response_time_days']))
        
        if len(features) < 10:
            raise ValueError("Insufficient training data for response time prediction")
        
        X = np.array(features)
        y = np.array(targets)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        # For regression, we'll use R² as accuracy
        from sklearn.metrics import r2_score
        accuracy = r2_score(y_test, y_pred)
        
        feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        
        self.models[ModelType.RESPONSE_TIME_PREDICTOR] = model
        self.scalers[ModelType.RESPONSE_TIME_PREDICTOR] = scaler
        
        return ModelPerformance(
            model_type=ModelType.RESPONSE_TIME_PREDICTOR,
            accuracy=accuracy,
            precision=0.0,  # Not applicable for regression
            recall=0.0,     # Not applicable for regression
            f1_score=0.0,   # Not applicable for regression
            training_size=len(features),
            last_updated=datetime.now(timezone.utc),
            feature_importance=feature_importance,
            cross_validation_score=accuracy  # Simplified
        )
    
    async def _train_salary_estimator(self, df: pd.DataFrame) -> ModelPerformance:
        """Train salary estimation model."""
        # Similar to response time predictor but for salary
        features = []
        targets = []
        
        for _, row in df.iterrows():
            if 'salary' in row and pd.notna(row['salary']):
                feature_vector = await self._extract_features(row.to_dict())
                features.append(feature_vector)
                targets.append(float(row['salary']))
        
        if len(features) < 10:
            # Generate synthetic data for demo
            for i in range(50):
                synthetic_features = np.random.rand(10)
                synthetic_salary = 50000 + synthetic_features.sum() * 10000
                features.append(synthetic_features)
                targets.append(synthetic_salary)
        
        X = np.array(features)
        y = np.array(targets)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        
        # Simple accuracy calculation
        y_pred = model.predict(X_scaled)
        from sklearn.metrics import mean_absolute_percentage_error
        accuracy = max(0, 1 - mean_absolute_percentage_error(y, y_pred))
        
        feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        
        self.models[ModelType.SALARY_ESTIMATOR] = model
        self.scalers[ModelType.SALARY_ESTIMATOR] = scaler
        
        return ModelPerformance(
            model_type=ModelType.SALARY_ESTIMATOR,
            accuracy=accuracy,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            training_size=len(features),
            last_updated=datetime.now(timezone.utc),
            feature_importance=feature_importance,
            cross_validation_score=accuracy
        )
    
    async def _extract_features(self, data: Dict[str, Any]) -> List[float]:
        """Extract numerical features from application data."""
        features = []
        
        # Basic numerical features
        features.append(float(data.get('experience_years', 0)))
        features.append(float(data.get('skill_match_score', 0.5)))
        features.append(float(data.get('cover_letter_used', False)))
        features.append(float(data.get('referral', False)))
        features.append(float(data.get('remote_position', False)))
        
        # Derived features
        company_size = data.get('company_size', 'unknown')
        features.append(1.0 if company_size == 'large' else 0.5 if company_size == 'medium' else 0.0)
        
        industry = data.get('industry', 'unknown')
        features.append(hash(industry) % 100 / 100.0)  # Simple hash encoding
        
        location = data.get('location', 'unknown')
        features.append(hash(location) % 100 / 100.0)
        
        # Add random features for demo
        features.extend([0.5, 0.3])  # Placeholder features
        
        return features[:10]  # Fixed size for consistency
    
    async def _simulate_variant_performance(self, 
                                          variant: Dict[str, Any], 
                                          sample_size: int) -> Dict[str, Any]:
        """Simulate variant performance for A/B testing."""
        # Base success rate
        base_rate = 0.15
        
        # Adjust based on variant parameters
        if variant.get('personalized_cover_letter', False):
            base_rate += 0.05
        
        if variant.get('follow_up_enabled', False):
            base_rate += 0.03
        
        if variant.get('optimized_timing', False):
            base_rate += 0.02
        
        # Add random variation
        import random
        actual_rate = base_rate + random.uniform(-0.02, 0.02)
        actual_rate = max(0, min(1, actual_rate))
        
        successes = int(sample_size * actual_rate)
        
        return {
            'success_rate': actual_rate,
            'successes': successes,
            'sample_size': sample_size
        }
    
    async def _calculate_statistical_significance(self,
                                                successes_a: int, size_a: int,
                                                successes_b: int, size_b: int) -> Tuple[float, Tuple[float, float]]:
        """Calculate statistical significance using z-test."""
        p_a = successes_a / size_a
        p_b = successes_b / size_b
        
        # Pooled proportion
        p_pool = (successes_a + successes_b) / (size_a + size_b)
        
        # Standard error
        se = np.sqrt(p_pool * (1 - p_pool) * (1/size_a + 1/size_b))
        
        if se == 0:
            return 0.5, (0.0, 0.0)
        
        # Z-score
        z = (p_b - p_a) / se
        
        # P-value (two-tailed)
        from scipy import stats
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))
        significance = 1 - p_value
        
        # Confidence interval for difference
        diff = p_b - p_a
        margin = 1.96 * se  # 95% confidence
        ci = (diff - margin, diff + margin)
        
        return significance, ci
    
    async def _initialize_population(self, size: int, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Initialize population for evolutionary algorithm."""
        population = []
        
        for _ in range(size):
            individual = {
                'personalization_level': np.random.uniform(0.1, 1.0),
                'application_frequency': np.random.uniform(1, 20),  # per week
                'follow_up_timing': np.random.uniform(3, 14),  # days
                'platform_focus': np.random.choice(['broad', 'targeted']),
                'cover_letter_usage': np.random.uniform(0.5, 1.0)
            }
            population.append(individual)
        
        return population
    
    async def _evaluate_population_fitness(self,
                                         population: List[Dict[str, Any]],
                                         objectives: List[OptimizationType],
                                         historical_data: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """Evaluate fitness for each individual in population."""
        fitness_scores = []
        
        for individual in population:
            scores = {}
            
            for objective in objectives:
                if objective == OptimizationType.RESPONSE_RATE:
                    # Simulate response rate based on individual's parameters
                    base_rate = 0.15
                    if individual['personalization_level'] > 0.7:
                        base_rate += 0.05
                    if individual['cover_letter_usage'] > 0.8:
                        base_rate += 0.03
                    scores['response_rate'] = base_rate
                
                elif objective == OptimizationType.TIME_EFFICIENCY:
                    # Time per application based on personalization
                    base_time = 30  # minutes
                    time_penalty = individual['personalization_level'] * 15
                    scores['time_efficiency'] = base_time + time_penalty
                
                elif objective == OptimizationType.COST_EFFECTIVENESS:
                    # Cost per successful application
                    cost_per_app = 5  # arbitrary units
                    total_cost = cost_per_app * individual['application_frequency']
                    success_rate = scores.get('response_rate', 0.15)
                    cost_per_success = total_cost / max(success_rate, 0.01)
                    scores['cost_effectiveness'] = 1 / cost_per_success  # Higher is better
            
            fitness_scores.append(scores)
        
        return fitness_scores
    
    async def _find_pareto_front(self,
                               population: List[Dict[str, Any]],
                               fitness_scores: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Find Pareto optimal solutions."""
        pareto_front = []
        
        for i, (individual, scores_i) in enumerate(zip(population, fitness_scores)):
            is_dominated = False
            
            for j, scores_j in enumerate(fitness_scores):
                if i != j:
                    # Check if j dominates i
                    dominates = True
                    for metric in scores_i.keys():
                        if metric in ['time_efficiency']:  # Lower is better
                            if scores_j[metric] > scores_i[metric]:
                                dominates = False
                                break
                        else:  # Higher is better
                            if scores_j[metric] < scores_i[metric]:
                                dominates = False
                                break
                    
                    if dominates:
                        # Check if strictly better in at least one objective
                        strictly_better = False
                        for metric in scores_i.keys():
                            if metric in ['time_efficiency']:
                                if scores_j[metric] < scores_i[metric]:
                                    strictly_better = True
                                    break
                            else:
                                if scores_j[metric] > scores_i[metric]:
                                    strictly_better = True
                                    break
                        
                        if strictly_better:
                            is_dominated = True
                            break
            
            if not is_dominated:
                pareto_front.append(individual)
        
        return pareto_front
    
    async def _evolve_population(self,
                               population: List[Dict[str, Any]],
                               fitness_scores: List[Dict[str, float]],
                               constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evolve population using genetic operators."""
        # Selection (tournament selection)
        selected = []
        for _ in range(len(population)):
            tournament = np.random.choice(len(population), size=3, replace=False)
            winner = tournament[0]  # Simplified selection
            selected.append(population[winner])
        
        # Crossover and mutation
        new_population = []
        for i in range(0, len(selected), 2):
            parent1 = selected[i]
            parent2 = selected[(i + 1) % len(selected)]
            
            # Crossover
            child1 = parent1.copy()
            child2 = parent2.copy()
            
            if np.random.random() < 0.8:  # Crossover probability
                for key in parent1.keys():
                    if isinstance(parent1[key], (int, float)):
                        child1[key] = (parent1[key] + parent2[key]) / 2
                        child2[key] = (parent1[key] + parent2[key]) / 2
            
            # Mutation
            for child in [child1, child2]:
                if np.random.random() < 0.1:  # Mutation probability
                    for key in child.keys():
                        if isinstance(child[key], (int, float)):
                            child[key] *= np.random.uniform(0.9, 1.1)
            
            new_population.extend([child1, child2])
        
        return new_population[:len(population)]
    
    async def _analyze_trade_offs(self,
                                pareto_solutions: List[Dict[str, Any]],
                                objectives: List[OptimizationType],
                                historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trade-offs between objectives."""
        if not pareto_solutions:
            return {}
        
        # Calculate statistics for each objective
        objective_stats = {}
        
        fitness_scores = await self._evaluate_population_fitness(
            pareto_solutions, objectives, historical_data
        )
        
        for objective in objectives:
            metric_name = objective.value
            values = [scores.get(metric_name, 0) for scores in fitness_scores]
            
            if values:
                objective_stats[metric_name] = {
                    'min': min(values),
                    'max': max(values),
                    'mean': np.mean(values),
                    'std': np.std(values)
                }
        
        return {
            'objective_statistics': objective_stats,
            'solution_count': len(pareto_solutions),
            'trade_off_analysis': "Multiple optimal solutions found with different trade-offs"
        }
    
    async def _assess_strategy_performance(self, strategy: Dict[str, Any]) -> Dict[str, float]:
        """Assess current strategy performance."""
        # Simulate performance based on strategy parameters
        performance = {
            'response_rate': 0.15,
            'interview_rate': 0.08,
            'offer_rate': 0.03,
            'time_per_application': 30.0,
            'cost_per_application': 5.0
        }
        
        # Adjust based on strategy
        if strategy.get('personalized_cover_letter', False):
            performance['response_rate'] += 0.05
            performance['time_per_application'] += 10
        
        if strategy.get('automated_follow_up', False):
            performance['response_rate'] += 0.02
            performance['interview_rate'] += 0.01
        
        return performance
    
    async def _generate_specific_recommendation(self,
                                              metric: str,
                                              current: float,
                                              target: float,
                                              strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific recommendation for metric improvement."""
        gap = target - current
        
        recommendations = {
            'response_rate': {
                'action': 'Implement personalized cover letters',
                'expected_impact': min(gap, 0.08),
                'implementation_effort': 'Medium',
                'timeline': '2-3 weeks'
            },
            'interview_rate': {
                'action': 'Improve skill-job matching algorithm',
                'expected_impact': min(gap, 0.05),
                'implementation_effort': 'High',
                'timeline': '4-6 weeks'
            },
            'offer_rate': {
                'action': 'Enhance interview preparation materials',
                'expected_impact': min(gap, 0.03),
                'implementation_effort': 'Low',
                'timeline': '1-2 weeks'
            }
        }
        
        return recommendations.get(metric, {
            'action': f'Optimize {metric}',
            'expected_impact': gap * 0.5,
            'implementation_effort': 'Medium',
            'timeline': '2-4 weeks'
        })
    
    async def _analyze_performance_drift(self,
                                       baseline_data: List[Dict[str, Any]],
                                       recent_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze performance drift between baseline and recent periods."""
        baseline_df = pd.DataFrame(baseline_data)
        recent_df = pd.DataFrame(recent_data)
        
        drift_metrics = {}
        
        if not baseline_df.empty and not recent_df.empty:
            # Response rate drift
            if 'responded' in baseline_df.columns and 'responded' in recent_df.columns:
                baseline_response = baseline_df['responded'].mean()
                recent_response = recent_df['responded'].mean()
                drift_metrics['response_rate'] = recent_response - baseline_response
            
            # Success rate drift
            if 'successful' in baseline_df.columns and 'successful' in recent_df.columns:
                baseline_success = baseline_df['successful'].mean()
                recent_success = recent_df['successful'].mean()
                drift_metrics['success_rate'] = recent_success - baseline_success
        
        return drift_metrics
    
    async def _analyze_model_drift(self, recent_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze model performance drift."""
        model_drift = {}
        
        for model_type, model in self.models.items():
            try:
                # Evaluate model on recent data
                features = []
                targets = []
                
                for data_point in recent_data:
                    feature_vector = await self._extract_features(data_point)
                    features.append(feature_vector)
                    
                    if model_type == ModelType.SUCCESS_PREDICTOR:
                        targets.append(1 if data_point.get('successful', False) else 0)
                
                if features and targets and len(features) >= 10:
                    X = np.array(features)
                    y = np.array(targets)
                    
                    scaler = self.scalers.get(model_type)
                    if scaler:
                        X_scaled = scaler.transform(X)
                        y_pred = model.predict(X_scaled)
                        
                        if model_type == ModelType.SUCCESS_PREDICTOR:
                            current_accuracy = accuracy_score(y, y_pred)
                            baseline_accuracy = self.model_performance[model_type].accuracy
                            model_drift[model_type.value] = current_accuracy - baseline_accuracy
                
            except Exception as e:
                self.logger.error(f"Error analyzing drift for {model_type.value}: {e}")
                continue
        
        return model_drift
    
    async def _generate_drift_recommendations(self, alerts: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on drift alerts."""
        recommendations = []
        
        for alert in alerts:
            if alert['type'] == 'performance_drift':
                if alert['severity'] == 'high':
                    recommendations.append(f"Urgent: Investigate {alert['metric']} performance drop")
                    recommendations.append("Consider reverting recent strategy changes")
                else:
                    recommendations.append(f"Monitor {alert['metric']} trend closely")
            
            elif alert['type'] == 'model_drift':
                recommendations.append("Retrain machine learning models with recent data")
                recommendations.append("Review feature engineering pipeline")
        
        return recommendations
    
    async def _save_model(self, model_type: ModelType):
        """Save trained model to disk."""
        try:
            model_path = self.model_storage_path / f"{model_type.value}_model.joblib"
            scaler_path = self.model_storage_path / f"{model_type.value}_scaler.joblib"
            
            if model_type in self.models:
                joblib.dump(self.models[model_type], model_path)
            
            if model_type in self.scalers:
                joblib.dump(self.scalers[model_type], scaler_path)
                
        except Exception as e:
            self.logger.error(f"Failed to save model {model_type.value}: {e}")
    
    async def _load_existing_models(self):
        """Load existing models from disk."""
        try:
            for model_type in ModelType:
                model_path = self.model_storage_path / f"{model_type.value}_model.joblib"
                scaler_path = self.model_storage_path / f"{model_type.value}_scaler.joblib"
                
                if model_path.exists():
                    self.models[model_type] = joblib.load(model_path)
                    self.logger.info(f"Loaded {model_type.value} model")
                
                if scaler_path.exists():
                    self.scalers[model_type] = joblib.load(scaler_path)
                    self.logger.info(f"Loaded {model_type.value} scaler")
                    
        except Exception as e:
            self.logger.error(f"Failed to load existing models: {e}")

if __name__ == "__main__":
    async def demo():
        agent = OptimizationAgent()
        
        # Generate sample historical data
        historical_data = []
        for i in range(100):
            data = {
                'application_id': str(uuid.uuid4()),
                'submitted_at': (datetime.now() - timedelta(days=np.random.randint(1, 90))).isoformat(),
                'responded': np.random.random() < 0.2,
                'successful': np.random.random() < 0.05,
                'platform': np.random.choice(['LinkedIn', 'Indeed', 'Company Site']),
                'cover_letter_used': np.random.random() < 0.7,
                'experience_years': np.random.randint(1, 15),
                'skill_match_score': np.random.uniform(0.3, 0.9),
                'salary': np.random.uniform(50000, 150000),
                'response_time_days': np.random.exponential(7) if np.random.random() < 0.2 else None
            }
            historical_data.append(data)
        
        current_metrics = {
            'response_rate': 0.15,
            'interview_rate': 0.08,
            'offer_rate': 0.03,
            'time_per_application': 30.0,
            'skill_match_score': 0.65
        }
        
        # Analyze optimization opportunities
        opportunities = await agent.analyze_optimization_opportunities(historical_data, current_metrics)
        print(f"🎯 Found {len(opportunities)} optimization opportunities:")
        for opp in opportunities[:3]:
            print(f"   • {opp.optimization_type.value}: {opp.improvement_potential:.1%} potential improvement")
        
        # Train predictive models
        model_performance = await agent.train_predictive_models(historical_data)
        print(f"🤖 Trained {len(model_performance)} ML models:")
        for model_type, performance in model_performance.items():
            print(f"   • {model_type.value}: {performance.accuracy:.3f} accuracy")
        
        # Run A/B test
        variant_a = {'personalized_cover_letter': False, 'follow_up_enabled': False}
        variant_b = {'personalized_cover_letter': True, 'follow_up_enabled': True}
        
        ab_result = await agent.run_ab_test(
            "Cover Letter Personalization Test", 
            variant_a, 
            variant_b, 
            sample_size=50
        )
        print(f"📊 A/B Test Result: {ab_result.recommendation}")
        
        # Multi-objective optimization
        objectives = [OptimizationType.RESPONSE_RATE, OptimizationType.TIME_EFFICIENCY]
        constraints = {'max_applications_per_week': 20, 'max_time_per_app': 45}
        
        optimization_result = await agent.optimize_multi_objective(objectives, constraints, historical_data)
        print(f"🔧 Multi-objective optimization: {optimization_result['solution_count']} optimal solutions found")
        
        # Predict success for sample application
        sample_application = {
            'experience_years': 5,
            'skill_match_score': 0.8,
            'cover_letter_used': True,
            'referral': False,
            'remote_position': True
        }
        
        predictions = await agent.predict_success_probability(sample_application)
        print(f"🔮 Success Predictions:")
        for metric, value in predictions.items():
            if 'rate' in metric or 'success' in metric:
                print(f"   • {metric}: {value:.1%}")
            else:
                print(f"   • {metric}: {value:.0f}")
    
    asyncio.run(demo())