#!/usr/bin/env python3
"""
🎯 Master Test Runner
Unified test execution orchestrator for the complete AI Job Autopilot testing suite
"""

import asyncio
import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class TestSuiteResult:
    """Results from a test suite execution"""
    suite_name: str
    status: str
    duration_seconds: float
    tests_passed: int
    tests_failed: int
    coverage_percent: Optional[float]
    artifacts_created: List[str]
    error_message: Optional[str] = None

class MasterTestOrchestrator:
    """Master test orchestrator for all testing suites"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results_dir = self.project_root / "test_results" / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.test_results_dir.mkdir(parents=True, exist_ok=True)
        
        self.available_test_suites = {
            "comprehensive": {
                "file": "comprehensive_test_suite.py",
                "description": "Complete end-to-end testing with all components",
                "estimated_minutes": 15,
                "critical": True
            },
            "ui_automation": {
                "file": "ui_automation_tests.py",
                "description": "UI testing with Selenium and Playwright",
                "estimated_minutes": 20,
                "critical": False
            },
            "integration": {
                "file": "integration_test_suite.py",
                "description": "Integration tests for pipeline components",
                "estimated_minutes": 12,
                "critical": True
            },
            "performance": {
                "file": "performance_load_testing.py",
                "description": "Performance and load testing",
                "estimated_minutes": 25,
                "critical": False
            },
            "ci_cd": {
                "file": "ci_cd_testing_workflow.py",
                "description": "CI/CD pipeline validation",
                "estimated_minutes": 10,
                "critical": True
            },
            "mock_scenarios": {
                "file": "enhanced_mock_scenarios.py",
                "description": "Mock data generation and validation",
                "estimated_minutes": 3,
                "critical": False
            }
        }
    
    def print_banner(self):
        """Print test execution banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🎯 MASTER TEST RUNNER - AI JOB AUTOPILOT 🎯             ║
║                                                              ║
║    Comprehensive Testing Suite Orchestrator                 ║
║    ═══════════════════════════════════════                  ║
║                                                              ║
║    ✅ End-to-End Testing                                    ║
║    ✅ UI Automation (Selenium + Playwright)                 ║
║    ✅ Integration Testing                                    ║
║    ✅ Performance & Load Testing                             ║
║    ✅ CI/CD Pipeline Validation                              ║
║    ✅ Mock Data Scenarios                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    async def run_test_suite(self, suite_name: str, suite_config: Dict[str, Any]) -> TestSuiteResult:
        """Run a single test suite"""
        print(f"\n🔄 Running {suite_name} test suite...")
        print(f"📝 Description: {suite_config['description']}")
        print(f"⏱️  Estimated time: {suite_config['estimated_minutes']} minutes")
        
        start_time = time.time()
        suite_file = self.project_root / suite_config["file"]
        
        # Check if test suite file exists
        if not suite_file.exists():
            print(f"⚠️  Test suite file not found: {suite_file}")
            return TestSuiteResult(
                suite_name=suite_name,
                status="skipped",
                duration_seconds=time.time() - start_time,
                tests_passed=0,
                tests_failed=0,
                coverage_percent=None,
                artifacts_created=[],
                error_message=f"Test suite file not found: {suite_file}"
            )
        
        try:
            # Run the test suite
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(suite_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )
            
            # Wait for completion with timeout
            timeout_seconds = suite_config["estimated_minutes"] * 60 * 2  # 2x estimated time
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout_seconds
                )
                
                duration = time.time() - start_time
                
                # Parse output to extract test results
                output_text = stdout.decode() + stderr.decode()
                
                # Save output to file
                output_file = self.test_results_dir / f"{suite_name}_output.txt"
                with open(output_file, "w") as f:
                    f.write(output_text)
                
                # Determine status based on return code and output
                if process.returncode == 0:
                    status = "passed"
                    error_message = None
                else:
                    status = "failed"
                    error_message = stderr.decode()
                
                # Extract test counts (simplified parsing)
                tests_passed = output_text.count("PASSED") + output_text.count("✅")
                tests_failed = output_text.count("FAILED") + output_text.count("❌")
                
                # Look for coverage information
                coverage_percent = None
                if "coverage" in output_text.lower():
                    # Try to extract coverage percentage (simplified)
                    import re
                    coverage_match = re.search(r'(\d+\.?\d*)%', output_text)
                    if coverage_match:
                        coverage_percent = float(coverage_match.group(1))
                
                print(f"   {'✅' if status == 'passed' else '❌'} Status: {status.upper()}")
                print(f"   ⏱️  Duration: {duration:.1f} seconds")
                print(f"   📊 Tests: {tests_passed} passed, {tests_failed} failed")
                if coverage_percent:
                    print(f"   📈 Coverage: {coverage_percent}%")
                
                return TestSuiteResult(
                    suite_name=suite_name,
                    status=status,
                    duration_seconds=duration,
                    tests_passed=tests_passed,
                    tests_failed=tests_failed,
                    coverage_percent=coverage_percent,
                    artifacts_created=[str(output_file)],
                    error_message=error_message
                )
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                
                print(f"   ⏰ Test suite timed out after {timeout_seconds} seconds")
                
                return TestSuiteResult(
                    suite_name=suite_name,
                    status="timeout",
                    duration_seconds=time.time() - start_time,
                    tests_passed=0,
                    tests_failed=0,
                    coverage_percent=None,
                    artifacts_created=[],
                    error_message=f"Timed out after {timeout_seconds} seconds"
                )
                
        except Exception as e:
            duration = time.time() - start_time
            print(f"   💥 Unexpected error: {e}")
            
            return TestSuiteResult(
                suite_name=suite_name,
                status="error",
                duration_seconds=duration,
                tests_passed=0,
                tests_failed=0,
                coverage_percent=None,
                artifacts_created=[],
                error_message=str(e)
            )
    
    def generate_test_plan(self, test_mode: str = "full") -> List[str]:
        """Generate test execution plan based on mode"""
        if test_mode == "critical":
            # Only run critical tests
            return [name for name, config in self.available_test_suites.items() if config["critical"]]
        elif test_mode == "quick":
            # Run only fast tests
            return [name for name, config in self.available_test_suites.items() 
                   if config["estimated_minutes"] <= 10]
        elif test_mode == "ui":
            # Only UI-related tests
            return ["ui_automation", "comprehensive"]
        elif test_mode == "performance":
            # Performance and load tests
            return ["performance", "integration"]
        else:  # full
            # Run all test suites
            return list(self.available_test_suites.keys())
    
    async def run_test_plan(self, test_plan: List[str]) -> List[TestSuiteResult]:
        """Execute a test plan"""
        print(f"\n📋 Executing test plan with {len(test_plan)} test suites:")
        for suite_name in test_plan:
            config = self.available_test_suites[suite_name]
            print(f"   • {suite_name}: {config['description']}")
        
        total_estimated_time = sum(
            self.available_test_suites[suite_name]["estimated_minutes"] 
            for suite_name in test_plan
        )
        print(f"\n⏱️  Total estimated time: {total_estimated_time} minutes")
        print("=" * 60)
        
        results = []
        
        for suite_name in test_plan:
            suite_config = self.available_test_suites[suite_name]
            result = await self.run_test_suite(suite_name, suite_config)
            results.append(result)
            
            # Short pause between test suites
            if suite_name != test_plan[-1]:  # Not the last suite
                print(f"   ⏳ Pausing 2 seconds before next suite...")
                await asyncio.sleep(2)
        
        return results
    
    def generate_comprehensive_report(self, results: List[TestSuiteResult]) -> str:
        """Generate comprehensive test report"""
        total_duration = sum(r.duration_seconds for r in results)
        total_tests_passed = sum(r.tests_passed for r in results)
        total_tests_failed = sum(r.tests_failed for r in results)
        
        passed_suites = [r for r in results if r.status == "passed"]
        failed_suites = [r for r in results if r.status in ["failed", "error", "timeout"]]
        skipped_suites = [r for r in results if r.status == "skipped"]
        
        # Calculate overall coverage
        coverage_results = [r.coverage_percent for r in results if r.coverage_percent is not None]
        avg_coverage = sum(coverage_results) / len(coverage_results) if coverage_results else None
        
        report = []
        report.append("🎯 COMPREHENSIVE TEST EXECUTION REPORT")
        report.append("=" * 50)
        report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📁 Results Directory: {self.test_results_dir}")
        report.append("")
        
        # Executive Summary
        report.append("📊 EXECUTIVE SUMMARY")
        report.append("-" * 25)
        report.append(f"Total Test Suites: {len(results)}")
        report.append(f"✅ Passed: {len(passed_suites)} ({len(passed_suites)/len(results)*100:.1f}%)")
        report.append(f"❌ Failed: {len(failed_suites)} ({len(failed_suites)/len(results)*100:.1f}%)")
        report.append(f"⏭️  Skipped: {len(skipped_suites)} ({len(skipped_suites)/len(results)*100:.1f}%)")
        report.append(f"⏱️  Total Execution Time: {total_duration/60:.1f} minutes")
        report.append(f"🧪 Total Individual Tests: {total_tests_passed + total_tests_failed}")
        report.append(f"✅ Individual Tests Passed: {total_tests_passed}")
        report.append(f"❌ Individual Tests Failed: {total_tests_failed}")
        if avg_coverage:
            report.append(f"📈 Average Coverage: {avg_coverage:.1f}%")
        report.append("")
        
        # Test Suite Details
        report.append("🔍 TEST SUITE DETAILS")
        report.append("-" * 25)
        
        for result in results:
            status_emoji = {
                "passed": "✅",
                "failed": "❌", 
                "error": "💥",
                "timeout": "⏰",
                "skipped": "⏭️"
            }.get(result.status, "❓")
            
            report.append(f"\n{status_emoji} {result.suite_name.upper()}")
            report.append(f"   Status: {result.status}")
            report.append(f"   Duration: {result.duration_seconds:.1f} seconds")
            report.append(f"   Tests Passed: {result.tests_passed}")
            report.append(f"   Tests Failed: {result.tests_failed}")
            if result.coverage_percent:
                report.append(f"   Coverage: {result.coverage_percent:.1f}%")
            if result.error_message:
                report.append(f"   Error: {result.error_message}")
            report.append(f"   Artifacts: {len(result.artifacts_created)} files")
        
        # Recommendations
        report.append("\n💡 RECOMMENDATIONS")
        report.append("-" * 20)
        
        if failed_suites:
            report.append(f"🔴 {len(failed_suites)} test suite(s) failed - investigate and fix issues")
            for failed in failed_suites:
                if failed.error_message:
                    report.append(f"   • {failed.suite_name}: {failed.error_message}")
        
        if total_tests_failed > 0:
            report.append(f"🔴 {total_tests_failed} individual tests failed - review test output")
        
        if avg_coverage and avg_coverage < 80:
            report.append(f"🔴 Test coverage below 80% ({avg_coverage:.1f}%) - add more tests")
        
        if not failed_suites and total_tests_failed == 0:
            report.append("✅ All tests passed successfully!")
            report.append("✅ System is ready for deployment")
        
        return "\n".join(report)
    
    def save_results(self, results: List[TestSuiteResult]) -> None:
        """Save test results and generate reports"""
        # Save JSON results
        json_file = self.test_results_dir / "test_results.json"
        with open(json_file, "w") as f:
            json.dump([asdict(r) for r in results], f, indent=2, default=str)
        
        # Save comprehensive report
        report = self.generate_comprehensive_report(results)
        report_file = self.test_results_dir / "comprehensive_report.txt"
        with open(report_file, "w") as f:
            f.write(report)
        
        # Save summary CSV
        import csv
        csv_file = self.test_results_dir / "test_summary.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Suite Name", "Status", "Duration (s)", "Tests Passed", 
                "Tests Failed", "Coverage %", "Error Message"
            ])
            for result in results:
                writer.writerow([
                    result.suite_name, result.status, result.duration_seconds,
                    result.tests_passed, result.tests_failed, 
                    result.coverage_percent or "", result.error_message or ""
                ])
        
        print(f"\n📊 Test results saved to: {self.test_results_dir}")

async def main():
    """Main test execution function"""
    orchestrator = MasterTestOrchestrator()
    orchestrator.print_banner()
    
    # Parse command line arguments
    test_mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    if test_mode == "help":
        print("🆘 USAGE:")
        print("python master_test_runner.py [mode]")
        print("\nAvailable modes:")
        print("  full        - Run all test suites (default)")
        print("  critical    - Run only critical test suites")
        print("  quick       - Run only quick test suites (≤10 minutes)")
        print("  ui          - Run UI-related test suites")
        print("  performance - Run performance test suites")
        print("  help        - Show this help message")
        return
    
    print(f"🎯 Test Mode: {test_mode.upper()}")
    print(f"📁 Results Directory: {orchestrator.test_results_dir}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Generate and execute test plan
        test_plan = orchestrator.generate_test_plan(test_mode)
        results = await orchestrator.run_test_plan(test_plan)
        
        # Generate and display report
        report = orchestrator.generate_comprehensive_report(results)
        print("\n" + report)
        
        # Save results
        orchestrator.save_results(results)
        
        # Determine exit code
        failed_critical = any(
            r.status in ["failed", "error"] and orchestrator.available_test_suites[r.suite_name]["critical"]
            for r in results
        )
        
        if failed_critical:
            print("\n💥 CRITICAL TEST FAILURES DETECTED!")
            print("🚫 System is not ready for deployment")
            sys.exit(1)
        else:
            print("\n🎉 Test execution completed successfully!")
            if test_mode == "full":
                print("✅ System validation complete - ready for deployment")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n👋 Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error during test execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())