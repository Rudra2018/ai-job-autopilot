#!/usr/bin/env python3
"""
⚡ Performance and Load Testing Suite
Comprehensive performance testing for the AI Job Autopilot system
"""

import asyncio
import time
import psutil
import json
import statistics
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import aiohttp
import pandas as pd
from unittest.mock import Mock, patch
import sys

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

from enhanced_mock_scenarios import EnhancedMockDataGenerator
from universal_job_scraper import UniversalJobScraper
from advanced_resume_parser import ResumeParser
from intelligent_job_matcher import AIJobMatcher
from auto_form_filler import IndustryStandardFormFiller
from job_application_orchestrator import JobApplicationOrchestrator

@dataclass
class PerformanceMetrics:
    """Performance measurement results"""
    test_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    throughput_ops_per_second: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success_rate: float
    error_count: int
    peak_memory_mb: float
    average_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    concurrent_users: int
    total_operations: int

@dataclass
class LoadTestConfig:
    """Load test configuration"""
    test_name: str
    concurrent_users: int
    total_operations: int
    ramp_up_seconds: int
    test_duration_seconds: int
    target_throughput: float
    max_memory_mb: int
    max_cpu_percent: float

class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics = []
        self.process = psutil.Process()
    
    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring = True
        self.metrics = []
        
        def monitor():
            while self.monitoring:
                try:
                    cpu_percent = self.process.cpu_percent()
                    memory_info = self.process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024
                    
                    self.metrics.append({
                        'timestamp': datetime.now(),
                        'cpu_percent': cpu_percent,
                        'memory_mb': memory_mb,
                        'threads': self.process.num_threads()
                    })
                    time.sleep(0.1)  # Monitor every 100ms
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    break
        
        self.monitor_thread = threading.Thread(target=monitor, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Dict[str, float]:
        """Stop monitoring and return statistics"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1)
        
        if not self.metrics:
            return {}
        
        cpu_values = [m['cpu_percent'] for m in self.metrics]
        memory_values = [m['memory_mb'] for m in self.metrics]
        
        return {
            'avg_cpu_percent': statistics.mean(cpu_values),
            'peak_cpu_percent': max(cpu_values),
            'avg_memory_mb': statistics.mean(memory_values),
            'peak_memory_mb': max(memory_values),
            'sample_count': len(self.metrics)
        }

class PerformanceTester:
    """Performance testing orchestrator"""
    
    def __init__(self):
        self.mock_generator = EnhancedMockDataGenerator()
        self.system_monitor = SystemMonitor()
        self.results = []
    
    async def run_job_scraping_performance_test(self, config: LoadTestConfig) -> PerformanceMetrics:
        """Test job scraping performance"""
        print(f"🔍 Running job scraping performance test: {config.test_name}")
        
        # Generate test data
        test_data = self.mock_generator.generate_performance_test_data("large")
        
        start_time = datetime.now()
        self.system_monitor.start_monitoring()
        
        response_times = []
        errors = 0
        successful_operations = 0
        
        async def scrape_job_batch(batch_jobs):
            """Scrape a batch of jobs"""
            batch_start = time.time()
            try:
                # Mock job scraping operation
                await asyncio.sleep(0.01)  # Simulate network delay
                
                # Simulate job processing
                processed_jobs = []
                for job in batch_jobs:
                    if random.random() > 0.05:  # 95% success rate
                        processed_jobs.append({
                            'id': job['id'],
                            'title': job['title'],
                            'company': job['company'],
                            'processed_at': datetime.now().isoformat()
                        })
                    else:
                        raise Exception("Simulated scraping error")
                
                response_time = (time.time() - batch_start) * 1000
                return processed_jobs, response_time, None
                
            except Exception as e:
                response_time = (time.time() - batch_start) * 1000
                return [], response_time, str(e)
        
        # Create job batches
        batch_size = 10
        job_batches = [test_data['job_listings'][i:i+batch_size] 
                      for i in range(0, len(test_data['job_listings']), batch_size)]
        
        # Run concurrent scraping
        semaphore = asyncio.Semaphore(config.concurrent_users)
        
        async def process_batch(batch):
            async with semaphore:
                return await scrape_job_batch(batch)
        
        tasks = [process_batch(batch) for batch in job_batches[:config.total_operations]]
        
        for completed_task in asyncio.as_completed(tasks):
            try:
                processed_jobs, response_time, error = await completed_task
                response_times.append(response_time)
                
                if error:
                    errors += 1
                else:
                    successful_operations += len(processed_jobs)
                    
            except Exception as e:
                errors += 1
                print(f"Task error: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        system_stats = self.system_monitor.stop_monitoring()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            throughput_ops_per_second=successful_operations / duration,
            memory_usage_mb=system_stats.get('avg_memory_mb', 0),
            cpu_usage_percent=system_stats.get('avg_cpu_percent', 0),
            success_rate=successful_operations / (successful_operations + errors),
            error_count=errors,
            peak_memory_mb=system_stats.get('peak_memory_mb', 0),
            average_response_time_ms=statistics.mean(response_times) if response_times else 0,
            p95_response_time_ms=statistics.quantiles(response_times, n=20)[18] if response_times else 0,
            p99_response_time_ms=statistics.quantiles(response_times, n=100)[98] if response_times else 0,
            concurrent_users=config.concurrent_users,
            total_operations=len(tasks)
        )
    
    async def run_resume_parsing_performance_test(self, config: LoadTestConfig) -> PerformanceMetrics:
        """Test resume parsing performance"""
        print(f"📄 Running resume parsing performance test: {config.test_name}")
        
        start_time = datetime.now()
        self.system_monitor.start_monitoring()
        
        response_times = []
        errors = 0
        successful_operations = 0
        
        # Generate mock resumes
        resume_profiles = self.mock_generator.create_resume_profiles()
        
        async def parse_resume_batch(profile_batch):
            """Parse a batch of resumes"""
            batch_start = time.time()
            try:
                parsed_resumes = []
                for profile in profile_batch:
                    # Simulate resume parsing
                    await asyncio.sleep(0.05)  # Simulate AI processing time
                    
                    if random.random() > 0.02:  # 98% success rate
                        parsed_resumes.append({
                            'name': profile['name'],
                            'skills': profile['primary_skills'],
                            'experience': profile['experience_years'],
                            'parsed_at': datetime.now().isoformat()
                        })
                    else:
                        raise Exception("Simulated parsing error")
                
                response_time = (time.time() - batch_start) * 1000
                return parsed_resumes, response_time, None
                
            except Exception as e:
                response_time = (time.time() - batch_start) * 1000
                return [], response_time, str(e)
        
        # Create profile batches
        profiles_list = list(resume_profiles.values())
        batch_size = 5
        profile_batches = [profiles_list[i:i+batch_size] 
                          for i in range(0, min(len(profiles_list), config.total_operations), batch_size)]
        
        semaphore = asyncio.Semaphore(config.concurrent_users)
        
        async def process_batch(batch):
            async with semaphore:
                return await parse_resume_batch(batch)
        
        tasks = [process_batch(batch) for batch in profile_batches]
        
        for completed_task in asyncio.as_completed(tasks):
            try:
                parsed_resumes, response_time, error = await completed_task
                response_times.append(response_time)
                
                if error:
                    errors += 1
                else:
                    successful_operations += len(parsed_resumes)
                    
            except Exception as e:
                errors += 1
                print(f"Resume parsing error: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        system_stats = self.system_monitor.stop_monitoring()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            throughput_ops_per_second=successful_operations / duration,
            memory_usage_mb=system_stats.get('avg_memory_mb', 0),
            cpu_usage_percent=system_stats.get('avg_cpu_percent', 0),
            success_rate=successful_operations / (successful_operations + errors) if (successful_operations + errors) > 0 else 0,
            error_count=errors,
            peak_memory_mb=system_stats.get('peak_memory_mb', 0),
            average_response_time_ms=statistics.mean(response_times) if response_times else 0,
            p95_response_time_ms=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
            p99_response_time_ms=statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0,
            concurrent_users=config.concurrent_users,
            total_operations=len(tasks)
        )
    
    async def run_job_matching_performance_test(self, config: LoadTestConfig) -> PerformanceMetrics:
        """Test job matching performance"""
        print(f"🎯 Running job matching performance test: {config.test_name}")
        
        start_time = datetime.now()
        self.system_monitor.start_monitoring()
        
        response_times = []
        errors = 0
        successful_operations = 0
        
        # Generate test data
        resume_profiles = list(self.mock_generator.create_resume_profiles().values())
        test_data = self.mock_generator.generate_performance_test_data("medium")
        
        async def match_jobs_batch(profile_job_pairs):
            """Match jobs for a batch of profile-job pairs"""
            batch_start = time.time()
            try:
                matches = []
                for profile, jobs in profile_job_pairs:
                    # Simulate AI matching
                    await asyncio.sleep(0.02)  # Simulate AI processing
                    
                    if random.random() > 0.03:  # 97% success rate
                        job_matches = []
                        for job in jobs[:10]:  # Match up to 10 jobs
                            match_score = random.uniform(0.1, 0.95)
                            if match_score > 0.6:  # Only include good matches
                                job_matches.append({
                                    'job_id': job['id'],
                                    'match_score': match_score,
                                    'matched_skills': random.sample(profile['primary_skills'], 2)
                                })
                        matches.append({
                            'profile': profile['name'],
                            'matches': job_matches,
                            'total_jobs_evaluated': len(jobs)
                        })
                    else:
                        raise Exception("Simulated matching error")
                
                response_time = (time.time() - batch_start) * 1000
                return matches, response_time, None
                
            except Exception as e:
                response_time = (time.time() - batch_start) * 1000
                return [], response_time, str(e)
        
        # Create profile-job pairs
        pairs = []
        for i, profile in enumerate(resume_profiles[:config.total_operations]):
            job_batch = test_data['job_listings'][i*20:(i+1)*20]  # 20 jobs per profile
            pairs.append((profile, job_batch))
        
        # Batch the pairs
        batch_size = 3
        pair_batches = [pairs[i:i+batch_size] for i in range(0, len(pairs), batch_size)]
        
        semaphore = asyncio.Semaphore(config.concurrent_users)
        
        async def process_batch(batch):
            async with semaphore:
                return await match_jobs_batch(batch)
        
        tasks = [process_batch(batch) for batch in pair_batches]
        
        for completed_task in asyncio.as_completed(tasks):
            try:
                matches, response_time, error = await completed_task
                response_times.append(response_time)
                
                if error:
                    errors += 1
                else:
                    successful_operations += len(matches)
                    
            except Exception as e:
                errors += 1
                print(f"Job matching error: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        system_stats = self.system_monitor.stop_monitoring()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            throughput_ops_per_second=successful_operations / duration if duration > 0 else 0,
            memory_usage_mb=system_stats.get('avg_memory_mb', 0),
            cpu_usage_percent=system_stats.get('avg_cpu_percent', 0),
            success_rate=successful_operations / (successful_operations + errors) if (successful_operations + errors) > 0 else 0,
            error_count=errors,
            peak_memory_mb=system_stats.get('peak_memory_mb', 0),
            average_response_time_ms=statistics.mean(response_times) if response_times else 0,
            p95_response_time_ms=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
            p99_response_time_ms=statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0,
            concurrent_users=config.concurrent_users,
            total_operations=len(tasks)
        )
    
    async def run_end_to_end_performance_test(self, config: LoadTestConfig) -> PerformanceMetrics:
        """Test complete pipeline performance"""
        print(f"🔄 Running end-to-end performance test: {config.test_name}")
        
        start_time = datetime.now()
        self.system_monitor.start_monitoring()
        
        response_times = []
        errors = 0
        successful_operations = 0
        
        # Generate comprehensive test data
        scenarios = self.mock_generator.generate_test_scenarios()
        
        async def run_complete_pipeline(scenario_data):
            """Run complete pipeline for a scenario"""
            pipeline_start = time.time()
            try:
                scenario, resume_profile, job_listings = scenario_data
                
                # Step 1: Resume parsing (simulated)
                await asyncio.sleep(0.02)
                
                # Step 2: Job scraping (simulated)
                await asyncio.sleep(0.05)
                
                # Step 3: Job matching (simulated)
                await asyncio.sleep(0.08)
                
                # Step 4: Application processing (simulated)
                await asyncio.sleep(0.03)
                
                if random.random() > 0.05:  # 95% success rate
                    result = {
                        'scenario_name': scenario.name,
                        'jobs_processed': len(job_listings),
                        'matches_found': scenario.expected_matches,
                        'applications_submitted': int(scenario.expected_matches * scenario.success_rate_threshold),
                        'success': True
                    }
                else:
                    raise Exception("Simulated pipeline error")
                
                response_time = (time.time() - pipeline_start) * 1000
                return result, response_time, None
                
            except Exception as e:
                response_time = (time.time() - pipeline_start) * 1000
                return None, response_time, str(e)
        
        # Create scenario data
        resume_profiles = self.mock_generator.create_resume_profiles()
        scenario_data = []
        
        for scenario in scenarios[:config.total_operations]:
            profile = list(resume_profiles.values())[0]  # Use first profile
            jobs = self.mock_generator.generate_job_listings_for_scenario(scenario)[:50]  # Limit for performance
            scenario_data.append((scenario, profile, jobs))
        
        semaphore = asyncio.Semaphore(config.concurrent_users)
        
        async def process_scenario(data):
            async with semaphore:
                return await run_complete_pipeline(data)
        
        tasks = [process_scenario(data) for data in scenario_data]
        
        for completed_task in asyncio.as_completed(tasks):
            try:
                result, response_time, error = await completed_task
                response_times.append(response_time)
                
                if error:
                    errors += 1
                else:
                    successful_operations += 1
                    
            except Exception as e:
                errors += 1
                print(f"Pipeline error: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        system_stats = self.system_monitor.stop_monitoring()
        
        return PerformanceMetrics(
            test_name=config.test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            throughput_ops_per_second=successful_operations / duration if duration > 0 else 0,
            memory_usage_mb=system_stats.get('avg_memory_mb', 0),
            cpu_usage_percent=system_stats.get('avg_cpu_percent', 0),
            success_rate=successful_operations / (successful_operations + errors) if (successful_operations + errors) > 0 else 0,
            error_count=errors,
            peak_memory_mb=system_stats.get('peak_memory_mb', 0),
            average_response_time_ms=statistics.mean(response_times) if response_times else 0,
            p95_response_time_ms=statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
            p99_response_time_ms=statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0,
            concurrent_users=config.concurrent_users,
            total_operations=len(tasks)
        )

class LoadTester:
    """Load testing orchestrator"""
    
    def __init__(self):
        self.performance_tester = PerformanceTester()
        self.test_configs = self._create_test_configurations()
    
    def _create_test_configurations(self) -> List[LoadTestConfig]:
        """Create load test configurations"""
        return [
            # Light load tests
            LoadTestConfig(
                test_name="Light Load - Job Scraping",
                concurrent_users=5,
                total_operations=50,
                ramp_up_seconds=10,
                test_duration_seconds=60,
                target_throughput=10.0,
                max_memory_mb=200,
                max_cpu_percent=50
            ),
            LoadTestConfig(
                test_name="Light Load - Resume Parsing",
                concurrent_users=3,
                total_operations=30,
                ramp_up_seconds=5,
                test_duration_seconds=45,
                target_throughput=5.0,
                max_memory_mb=150,
                max_cpu_percent=40
            ),
            
            # Medium load tests
            LoadTestConfig(
                test_name="Medium Load - Job Matching",
                concurrent_users=10,
                total_operations=100,
                ramp_up_seconds=20,
                test_duration_seconds=120,
                target_throughput=15.0,
                max_memory_mb=300,
                max_cpu_percent=70
            ),
            LoadTestConfig(
                test_name="Medium Load - End-to-End",
                concurrent_users=8,
                total_operations=25,
                ramp_up_seconds=15,
                test_duration_seconds=180,
                target_throughput=3.0,
                max_memory_mb=400,
                max_cpu_percent=60
            ),
            
            # Heavy load tests
            LoadTestConfig(
                test_name="Heavy Load - Job Scraping",
                concurrent_users=20,
                total_operations=200,
                ramp_up_seconds=30,
                test_duration_seconds=300,
                target_throughput=25.0,
                max_memory_mb=500,
                max_cpu_percent=80
            ),
            LoadTestConfig(
                test_name="Stress Test - Complete Pipeline",
                concurrent_users=15,
                total_operations=50,
                ramp_up_seconds=45,
                test_duration_seconds=600,
                target_throughput=2.0,
                max_memory_mb=600,
                max_cpu_percent=85
            )
        ]
    
    async def run_all_load_tests(self) -> List[PerformanceMetrics]:
        """Run all load tests"""
        print("⚡ Starting Comprehensive Load Testing Suite...")
        print(f"📊 Total test configurations: {len(self.test_configs)}")
        
        results = []
        
        for i, config in enumerate(self.test_configs, 1):
            print(f"\n🔄 Running test {i}/{len(self.test_configs)}: {config.test_name}")
            
            try:
                if "Job Scraping" in config.test_name:
                    result = await self.performance_tester.run_job_scraping_performance_test(config)
                elif "Resume Parsing" in config.test_name:
                    result = await self.performance_tester.run_resume_parsing_performance_test(config)
                elif "Job Matching" in config.test_name:
                    result = await self.performance_tester.run_job_matching_performance_test(config)
                else:  # End-to-End or Complete Pipeline
                    result = await self.performance_tester.run_end_to_end_performance_test(config)
                
                results.append(result)
                
                # Print immediate results
                print(f"   ✅ Completed in {result.duration_seconds:.2f}s")
                print(f"   📈 Throughput: {result.throughput_ops_per_second:.2f} ops/sec")
                print(f"   💾 Peak Memory: {result.peak_memory_mb:.1f} MB")
                print(f"   🎯 Success Rate: {result.success_rate:.2%}")
                
                # Cool down between tests
                if i < len(self.test_configs):
                    print("   ⏳ Cooling down for 5 seconds...")
                    await asyncio.sleep(5)
                    
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
                # Create a failed result
                failed_result = PerformanceMetrics(
                    test_name=config.test_name,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    duration_seconds=0,
                    throughput_ops_per_second=0,
                    memory_usage_mb=0,
                    cpu_usage_percent=0,
                    success_rate=0,
                    error_count=1,
                    peak_memory_mb=0,
                    average_response_time_ms=0,
                    p95_response_time_ms=0,
                    p99_response_time_ms=0,
                    concurrent_users=config.concurrent_users,
                    total_operations=0
                )
                results.append(failed_result)
        
        return results
    
    def generate_performance_report(self, results: List[PerformanceMetrics]) -> str:
        """Generate comprehensive performance report"""
        report = []
        report.append("📊 COMPREHENSIVE PERFORMANCE TEST REPORT")
        report.append("=" * 50)
        report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"🧪 Total Tests: {len(results)}")
        report.append("")
        
        # Summary statistics
        successful_tests = [r for r in results if r.success_rate > 0]
        if successful_tests:
            avg_throughput = statistics.mean([r.throughput_ops_per_second for r in successful_tests])
            avg_memory = statistics.mean([r.peak_memory_mb for r in successful_tests])
            avg_response_time = statistics.mean([r.average_response_time_ms for r in successful_tests])
            overall_success_rate = statistics.mean([r.success_rate for r in successful_tests])
            
            report.append("📈 SUMMARY STATISTICS")
            report.append("-" * 30)
            report.append(f"🚀 Average Throughput: {avg_throughput:.2f} ops/sec")
            report.append(f"💾 Average Peak Memory: {avg_memory:.1f} MB")
            report.append(f"⏱️  Average Response Time: {avg_response_time:.1f} ms")
            report.append(f"✅ Overall Success Rate: {overall_success_rate:.2%}")
            report.append("")
        
        # Individual test results
        report.append("🔍 DETAILED TEST RESULTS")
        report.append("-" * 30)
        
        for result in results:
            report.append(f"\n🧪 {result.test_name}")
            report.append(f"   ⏰ Duration: {result.duration_seconds:.2f} seconds")
            report.append(f"   👥 Concurrent Users: {result.concurrent_users}")
            report.append(f"   📊 Total Operations: {result.total_operations}")
            report.append(f"   🚀 Throughput: {result.throughput_ops_per_second:.2f} ops/sec")
            report.append(f"   💾 Memory Usage: {result.memory_usage_mb:.1f} MB (Peak: {result.peak_memory_mb:.1f} MB)")
            report.append(f"   🖥️  CPU Usage: {result.cpu_usage_percent:.1f}%")
            report.append(f"   ✅ Success Rate: {result.success_rate:.2%}")
            report.append(f"   ❌ Errors: {result.error_count}")
            report.append(f"   ⏱️  Avg Response Time: {result.average_response_time_ms:.1f} ms")
            report.append(f"   📊 P95 Response Time: {result.p95_response_time_ms:.1f} ms")
            report.append(f"   📈 P99 Response Time: {result.p99_response_time_ms:.1f} ms")
        
        # Performance recommendations
        report.append("\n💡 PERFORMANCE RECOMMENDATIONS")
        report.append("-" * 35)
        
        high_memory_tests = [r for r in results if r.peak_memory_mb > 400]
        high_cpu_tests = [r for r in results if r.cpu_usage_percent > 70]
        slow_tests = [r for r in results if r.average_response_time_ms > 200]
        low_success_tests = [r for r in results if r.success_rate < 0.9]
        
        if high_memory_tests:
            report.append(f"🔴 High Memory Usage detected in {len(high_memory_tests)} tests")
            report.append("   → Consider optimizing memory usage and implementing caching")
        
        if high_cpu_tests:
            report.append(f"🔴 High CPU Usage detected in {len(high_cpu_tests)} tests")
            report.append("   → Consider optimizing algorithms and using async processing")
        
        if slow_tests:
            report.append(f"🔴 Slow Response Times detected in {len(slow_tests)} tests")
            report.append("   → Consider implementing connection pooling and request optimization")
        
        if low_success_tests:
            report.append(f"🔴 Low Success Rates detected in {len(low_success_tests)} tests")
            report.append("   → Consider implementing better error handling and retry mechanisms")
        
        if not any([high_memory_tests, high_cpu_tests, slow_tests, low_success_tests]):
            report.append("✅ All tests performed within acceptable parameters!")
            report.append("   → System is ready for production load")
        
        return "\n".join(report)
    
    def save_results(self, results: List[PerformanceMetrics], output_dir: str = "data/performance_results") -> None:
        """Save performance test results"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw results as JSON
        json_results = [asdict(result) for result in results]
        with open(output_path / f"performance_results_{timestamp}.json", "w") as f:
            json.dump(json_results, f, indent=2, default=str)
        
        # Save detailed report
        report = self.generate_performance_report(results)
        with open(output_path / f"performance_report_{timestamp}.txt", "w") as f:
            f.write(report)
        
        # Save CSV for analysis
        df_data = []
        for result in results:
            df_data.append({
                'test_name': result.test_name,
                'duration_seconds': result.duration_seconds,
                'throughput_ops_per_second': result.throughput_ops_per_second,
                'peak_memory_mb': result.peak_memory_mb,
                'cpu_usage_percent': result.cpu_usage_percent,
                'success_rate': result.success_rate,
                'average_response_time_ms': result.average_response_time_ms,
                'concurrent_users': result.concurrent_users,
                'total_operations': result.total_operations,
                'error_count': result.error_count
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(output_path / f"performance_data_{timestamp}.csv", index=False)
        
        print(f"📊 Performance test results saved to {output_path}")

# Import random for simulation
import random

async def main():
    """Run comprehensive performance and load testing"""
    print("⚡ AI Job Autopilot - Performance and Load Testing Suite")
    print("=" * 55)
    
    load_tester = LoadTester()
    
    try:
        # Run all load tests
        results = await load_tester.run_all_load_tests()
        
        # Generate and display report
        report = load_tester.generate_performance_report(results)
        print("\n" + report)
        
        # Save results
        load_tester.save_results(results)
        
        print("\n🎉 Performance testing completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Performance testing failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())