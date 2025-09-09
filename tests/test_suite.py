#!/usr/bin/env python3
"""
🤖 AI Job Autopilot - Comprehensive Testing Suite
Complete test coverage for all enhanced modules and integrations
"""

import unittest
import asyncio
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import modules to test
from ai_question_answerer import AIQuestionAnswerer, QuestionAnswer
from dynamic_resume_rewriter import DynamicResumeRewriter, ResumeVersion
from smart_duplicate_detector import SmartDuplicateDetector, JobApplication, DuplicateMatch
from undetected_browser import UndetectedBrowser, BrowserConfig, HumanBehaviorConfig
from config_manager import AdvancedConfigManager
from integration_layer import EnhancedIntegrationLayer, AutopilotSession
from notification_system import RealtimeNotificationSystem, Notification

class TestAIQuestionAnswerer(unittest.TestCase):
    """Test AI Question Answerer functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.qa = AIQuestionAnswerer()
        self.test_job_context = {
            "title": "Software Engineer",
            "company": "TestCorp",
            "description": "Looking for a Python developer with React experience"
        }
    
    def test_initialization(self):
        """Test QA system initialization"""
        self.assertIsNotNone(self.qa)
        self.assertIsNotNone(self.qa.user_profile)
        self.assertIsInstance(self.qa.answers_cache, dict)
    
    def test_question_categorization(self):
        """Test question categorization"""
        test_cases = [
            ("Why are you interested in this position?", "motivation"),
            ("How many years of experience do you have?", "experience"),
            ("What are your key skills?", "skills"),
            ("When can you start?", "availability"),
            ("What are your salary expectations?", "salary")
        ]
        
        for question, expected_category in test_cases:
            category = self.qa._categorize_question(question)
            self.assertEqual(category, expected_category)
    
    def test_answer_question(self):
        """Test question answering"""
        question = "Why are you interested in this position?"
        
        result = self.qa.answer_question(question, self.test_job_context)
        
        self.assertIsInstance(result, QuestionAnswer)
        self.assertEqual(result.question, question)
        self.assertIsInstance(result.answer, str)
        self.assertGreater(len(result.answer), 10)  # Answer should have content
        self.assertGreater(result.confidence, 0)
    
    def test_bulk_answer_questions(self):
        """Test bulk question answering"""
        questions = [
            "Why are you interested in this position?",
            "What relevant experience do you have?",
            "What are your salary expectations?"
        ]
        
        results = self.qa.bulk_answer_questions(questions, self.test_job_context)
        
        self.assertEqual(len(results), len(questions))
        for result in results:
            self.assertIsInstance(result, QuestionAnswer)
            self.assertIsInstance(result.answer, str)
    
    def test_answer_caching(self):
        """Test answer caching functionality"""
        question = "What is your email address?"
        
        # Answer question twice
        result1 = self.qa.answer_question(question)
        result2 = self.qa.answer_question(question)
        
        # Should use cache for second call
        self.assertEqual(result1.answer, result2.answer)
    
    def test_statistics(self):
        """Test statistics generation"""
        # Answer some questions first
        self.qa.answer_question("Test question 1", self.test_job_context)
        self.qa.answer_question("Test question 2", self.test_job_context)
        
        stats = self.qa.get_answer_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_questions", stats)
        self.assertGreater(stats["total_questions"], 0)

class TestDynamicResumeRewriter(unittest.TestCase):
    """Test Dynamic Resume Rewriter functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary resume file
        self.temp_resume = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        self.temp_resume.write("John Doe\\nSoftware Engineer\\n5 years Python experience\\nReact, Node.js, AWS")
        self.temp_resume.close()
        
        self.rewriter = DynamicResumeRewriter(self.temp_resume.name)
        
        self.test_job_description = """
        We are seeking a Senior Software Engineer with expertise in Python and React.
        Experience with AWS, Docker, and microservices is preferred.
        The ideal candidate will have 5+ years of software development experience.
        """
    
    def tearDown(self):
        """Clean up test environment"""
        os.unlink(self.temp_resume.name)
    
    def test_initialization(self):
        """Test rewriter initialization"""
        self.assertIsNotNone(self.rewriter)
        self.assertTrue(self.rewriter.base_resume_path.exists())
    
    def test_extract_resume_text(self):
        """Test resume text extraction"""
        text = self.rewriter.extract_resume_text(Path(self.temp_resume.name))
        
        self.assertIsInstance(text, str)
        self.assertIn("John Doe", text)
        self.assertIn("Python", text)
    
    def test_analyze_job_description(self):
        """Test job description analysis"""
        analysis = self.rewriter.analyze_job_description(self.test_job_description)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn("keywords", analysis)
        self.assertIn("requirements", analysis)
        self.assertIn("Python", analysis["keywords"])
        self.assertIn("React", analysis["keywords"])
    
    def test_calculate_similarity(self):
        """Test resume-job similarity calculation"""
        resume_text = "Python developer with React experience"
        
        similarity = self.rewriter.calculate_resume_job_similarity(
            resume_text, self.test_job_description
        )
        
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
    
    def test_create_optimized_resume(self):
        """Test optimized resume creation"""
        result = self.rewriter.create_optimized_resume(
            job_title="Senior Software Engineer",
            company="TestCorp",
            job_description=self.test_job_description
        )
        
        self.assertIsInstance(result, ResumeVersion)
        self.assertEqual(result.job_title, "Senior Software Engineer")
        self.assertEqual(result.company, "TestCorp")
        self.assertGreater(result.similarity_score, 0)
        self.assertTrue(Path(result.optimized_resume_path).exists())
    
    def test_statistics(self):
        """Test statistics generation"""
        # Create an optimized resume first
        self.rewriter.create_optimized_resume(
            "Test Engineer", "TestCorp", self.test_job_description
        )
        
        stats = self.rewriter.get_optimization_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_versions", stats)
        self.assertGreater(stats["total_versions"], 0)

class TestSmartDuplicateDetector(unittest.TestCase):
    """Test Smart Duplicate Detector functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.detector = SmartDuplicateDetector()
    
    def test_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector.applications, dict)
    
    def test_generate_job_id(self):
        """Test job ID generation"""
        job_id = self.detector.generate_job_id(
            "Software Engineer", "Google", "https://linkedin.com/jobs/view/12345"
        )
        
        self.assertIsInstance(job_id, str)
        self.assertGreater(len(job_id), 0)
        
        # Test URL extraction
        self.assertIn("linkedin", job_id)
    
    def test_normalize_job_title(self):
        """Test job title normalization"""
        test_cases = [
            ("Senior Software Engineer", "senior software engineer"),
            ("Frontend Developer (Remote)", "frontend developer"),
            ("Full Stack Developer - Urgent", "fullstack developer")
        ]
        
        for original, expected in test_cases:
            normalized = self.detector.normalize_job_title(original)
            self.assertEqual(normalized, expected)
    
    def test_normalize_company_name(self):
        """Test company name normalization"""
        test_cases = [
            ("Google Inc.", "google"),
            ("Facebook, Inc", "meta"),  # Alias
            ("Microsoft Corporation", "microsoft"),
            ("Apple Inc", "apple")
        ]
        
        for original, expected in test_cases:
            normalized = self.detector.normalize_company_name(original)
            self.assertEqual(normalized, expected)
    
    def test_add_application(self):
        """Test adding job application"""
        was_added, app = self.detector.add_application(
            job_title="Software Engineer",
            company="Google",
            job_url="https://linkedin.com/jobs/view/12345",
            job_description="Python developer position",
            location="San Francisco",
            job_source="linkedin"
        )
        
        self.assertTrue(was_added)
        self.assertIsInstance(app, JobApplication)
        self.assertEqual(app.job_title, "Software Engineer")
        self.assertEqual(app.company, "Google")
    
    def test_duplicate_detection(self):
        """Test duplicate detection"""
        # Add first application
        self.detector.add_application(
            "Software Engineer", "Google", "https://linkedin.com/jobs/view/12345"
        )
        
        # Check for duplicate (similar title and same company)
        is_duplicate, match = self.detector.check_if_duplicate(
            "Sr. Software Engineer", "Alphabet", "https://linkedin.com/jobs/view/12346"
        )
        
        self.assertTrue(is_duplicate)
        self.assertIsNotNone(match)
        self.assertGreater(match.similarity_score, 0.7)
    
    def test_statistics(self):
        """Test statistics generation"""
        # Add some applications
        self.detector.add_application("Engineer 1", "Company 1", "url1")
        self.detector.add_application("Engineer 2", "Company 2", "url2")
        
        stats = self.detector.get_application_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_applications", stats)
        self.assertGreater(stats["total_applications"], 0)

class TestUndetectedBrowser(unittest.TestCase):
    """Test Undetected Browser functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.browser_config = BrowserConfig(headless=True)
        self.behavior_config = HumanBehaviorConfig()
        
    def test_initialization(self):
        """Test browser initialization"""
        browser = UndetectedBrowser(self.browser_config, self.behavior_config)
        self.assertIsNotNone(browser)
        self.assertEqual(browser.browser_config.headless, True)
    
    def test_user_agent_selection(self):
        """Test user agent selection"""
        browser = UndetectedBrowser(self.browser_config, self.behavior_config)
        self.assertIn("Mozilla", browser.user_agents[0])
        self.assertIn("Chrome", browser.user_agents[0])
    
    def test_screen_resolution_selection(self):
        """Test screen resolution selection"""
        browser = UndetectedBrowser(self.browser_config, self.behavior_config)
        resolutions = browser.screen_resolutions
        
        self.assertIsInstance(resolutions, list)
        self.assertGreater(len(resolutions), 0)
        
        # Test that resolutions are tuples of two integers
        for resolution in resolutions:
            self.assertIsInstance(resolution, tuple)
            self.assertEqual(len(resolution), 2)
            self.assertIsInstance(resolution[0], int)
            self.assertIsInstance(resolution[1], int)

class TestAdvancedConfigManager(unittest.TestCase):
    """Test Advanced Configuration Manager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_config_dir = tempfile.mkdtemp()
        self.config_manager = AdvancedConfigManager(self.temp_config_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_config_dir)
    
    def test_initialization(self):
        """Test config manager initialization"""
        self.assertIsNotNone(self.config_manager)
        self.assertTrue(self.config_manager.config_dir.exists())
    
    def test_get_set_configuration(self):
        """Test getting and setting configuration values"""
        # Test setting a value
        self.config_manager.set("test.key", "test_value")
        
        # Test getting the value
        value = self.config_manager.get("test.key")
        self.assertEqual(value, "test_value")
        
        # Test default value
        default_value = self.config_manager.get("nonexistent.key", "default")
        self.assertEqual(default_value, "default")
    
    def test_ai_provider_config(self):
        """Test AI provider configuration"""
        from config_manager import AIProviderConfig
        
        # Create provider config
        provider_config = AIProviderConfig(
            name="test_provider",
            api_key="test_key",
            model="test_model"
        )
        
        # Set and get provider config
        self.config_manager.set_ai_provider_config("test_provider", provider_config)
        retrieved_config = self.config_manager.get_ai_provider_config("test_provider")
        
        self.assertEqual(retrieved_config.name, "test_provider")
        self.assertEqual(retrieved_config.api_key, "test_key")
        self.assertEqual(retrieved_config.model, "test_model")
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        issues = self.config_manager.validate_configuration()
        self.assertIsInstance(issues, dict)
        
        # Should have issues initially (no credentials set)
        self.assertGreater(len(issues), 0)
    
    def test_save_load_configuration(self):
        """Test saving and loading configuration"""
        # Set a test value
        self.config_manager.set("test.save_load", "test_value")
        
        # Save configuration
        self.config_manager.save()
        
        # Create new config manager and verify value persists
        new_config_manager = AdvancedConfigManager(self.temp_config_dir)
        value = new_config_manager.get("test.save_load")
        self.assertEqual(value, "test_value")

class TestEnhancedIntegrationLayer(unittest.TestCase):
    """Test Enhanced Integration Layer functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.integration = EnhancedIntegrationLayer()
    
    def tearDown(self):
        """Clean up test environment"""
        self.integration.cleanup()
    
    def test_initialization(self):
        """Test integration layer initialization"""
        self.assertIsNotNone(self.integration)
        self.assertIsNotNone(self.integration.question_answerer)
        self.assertIsNotNone(self.integration.resume_rewriter)
        self.assertIsNotNone(self.integration.duplicate_detector)
    
    def test_event_system(self):
        """Test event system functionality"""
        received_events = []
        
        def test_handler(event_type, data):
            received_events.append((event_type, data))
        
        # Register handler
        self.integration.register_event_handler("test_event", test_handler)
        
        # Emit event
        self.integration.emit_event("test_event", {"test": "data"})
        
        # Verify event was received
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0][0], "test_event")
        self.assertEqual(received_events[0][1]["test"], "data")
    
    def test_notification_system(self):
        """Test notification system integration"""
        received_notifications = []
        
        def notification_handler(notification):
            received_notifications.append(notification)
        
        # Add notification handler
        self.integration.add_notification_handler(notification_handler)
        
        # Send notification
        self.integration._notify("Test message", "info", {"test": "data"})
        
        # Verify notification was received
        self.assertEqual(len(received_notifications), 1)
        self.assertEqual(received_notifications[0]["message"], "Test message")
    
    def test_system_statistics(self):
        """Test system statistics generation"""
        stats = self.integration.get_system_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("session_stats", stats)
        self.assertIn("performance_metrics", stats)
        self.assertIn("module_stats", stats)
        self.assertIn("system_health", stats)
    
    def test_ai_integration(self):
        """Test AI integration testing"""
        results = self.integration.test_ai_integration()
        
        self.assertIsInstance(results, dict)
        self.assertIn("question_answerer", results)
        self.assertIn("resume_rewriter", results)
        self.assertIn("duplicate_detector", results)

class TestNotificationSystem(unittest.TestCase):
    """Test Real-Time Notification System functionality"""
    
    def setUp(self):
        """Set up test environment"""
        config = {
            "desktop": {"enabled": True},
            "email": {"enabled": False}  # Disabled for testing
        }
        self.notification_system = RealtimeNotificationSystem(config)
    
    def tearDown(self):
        """Clean up test environment"""
        self.notification_system.cleanup()
    
    def test_initialization(self):
        """Test notification system initialization"""
        self.assertIsNotNone(self.notification_system)
        self.assertIsInstance(self.notification_system.handlers, dict)
    
    def test_send_notification(self):
        """Test sending notification"""
        notification_id = self.notification_system.send_notification(
            title="Test Notification",
            message="This is a test message",
            level="info"
        )
        
        self.assertIsInstance(notification_id, str)
        self.assertGreater(len(notification_id), 0)
        
        # Wait a bit for processing
        import time
        time.sleep(1)
        
        # Check history
        history = self.notification_system.get_notification_history(1)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["title"], "Test Notification")
    
    def test_notification_types(self):
        """Test different notification types"""
        # Test session started
        session_id = self.notification_system.send_session_started({
            "max_applications": 10,
            "job_titles": ["Software Engineer"]
        })
        self.assertIsInstance(session_id, str)
        
        # Test application success
        app_id = self.notification_system.send_application_success({
            "title": "Test Job",
            "company": "Test Company"
        })
        self.assertIsInstance(app_id, str)
        
        # Test error
        error_id = self.notification_system.send_error("Test error message")
        self.assertIsInstance(error_id, str)
    
    def test_handler_status(self):
        """Test handler status reporting"""
        status = self.notification_system.get_handler_status()
        
        self.assertIsInstance(status, dict)
        self.assertGreater(len(status), 0)
        
        for handler_name, handler_status in status.items():
            self.assertIn("available", handler_status)
            self.assertIn("type", handler_status)

class IntegrationTests(unittest.TestCase):
    """Integration tests for complete system functionality"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.integration = EnhancedIntegrationLayer()
    
    def tearDown(self):
        """Clean up integration test environment"""
        self.integration.cleanup()
    
    def test_end_to_end_question_answering(self):
        """Test end-to-end question answering flow"""
        job_context = {
            "title": "Software Engineer",
            "company": "TestCorp",
            "description": "Python developer position"
        }
        
        # Answer question
        result = self.integration.question_answerer.answer_question(
            "Why are you interested in this position?", job_context
        )
        
        self.assertIsInstance(result, QuestionAnswer)
        self.assertGreater(len(result.answer), 10)
    
    def test_end_to_end_resume_optimization(self):
        """Test end-to-end resume optimization flow"""
        # Create temporary resume
        temp_resume = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_resume.write("John Doe\\nSoftware Engineer\\nPython, React")
        temp_resume.close()
        
        try:
            self.integration.resume_rewriter.base_resume_path = Path(temp_resume.name)
            
            # Optimize resume
            result = self.integration.resume_rewriter.create_optimized_resume(
                "Senior Software Engineer",
                "Google",
                "Looking for Python developer with React experience"
            )
            
            self.assertIsInstance(result, ResumeVersion)
            self.assertGreater(result.similarity_score, 0)
            
        finally:
            os.unlink(temp_resume.name)
    
    def test_end_to_end_duplicate_detection(self):
        """Test end-to-end duplicate detection flow"""
        # Add application
        was_added, app = self.integration.duplicate_detector.add_application(
            "Software Engineer", "Google", "https://example.com/job1"
        )
        self.assertTrue(was_added)
        
        # Check for duplicate
        is_duplicate, match = self.integration.duplicate_detector.check_if_duplicate(
            "Sr. Software Engineer", "Alphabet", "https://example.com/job2"
        )
        
        self.assertTrue(is_duplicate)
        self.assertIsNotNone(match)

def run_performance_tests():
    """Run performance tests for critical components"""
    print("\\n🚀 Running Performance Tests...")
    
    import time
    
    # Test AI question answering speed
    start_time = time.time()
    qa = AIQuestionAnswerer()
    result = qa.answer_question("What is your experience with Python?")
    qa_time = time.time() - start_time
    print(f"   ⚡ AI Question Answering: {qa_time:.2f}s")
    
    # Test duplicate detection speed
    start_time = time.time()
    detector = SmartDuplicateDetector()
    detector.add_application("Test Job", "Test Company", "test_url")
    is_duplicate, _ = detector.check_if_duplicate("Test Job 2", "Test Company 2", "test_url2")
    detection_time = time.time() - start_time
    print(f"   🔍 Duplicate Detection: {detection_time:.2f}s")
    
    # Test configuration operations
    start_time = time.time()
    config = AdvancedConfigManager()
    config.set("test.key", "test_value")
    value = config.get("test.key")
    config_time = time.time() - start_time
    print(f"   ⚙️ Configuration Operations: {config_time:.2f}s")
    
    print("   ✅ Performance tests completed")

def main():
    """Run the complete test suite"""
    print("🤖 AI Job Autopilot - Comprehensive Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAIQuestionAnswerer,
        TestDynamicResumeRewriter,
        TestSmartDuplicateDetector,
        TestUndetectedBrowser,
        TestAdvancedConfigManager,
        TestEnhancedIntegrationLayer,
        TestNotificationSystem,
        IntegrationTests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\\n📊 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\\n❌ Failures:")
        for test, traceback in result.failures:
            newline = '\\n'
            print(f"   - {test}: {traceback.split(newline)[-2]}")
    
    if result.errors:
        print(f"\\n🚨 Errors:")
        for test, traceback in result.errors:
            newline = '\\n'
            print(f"   - {test}: {traceback.split(newline)[-2]}")
    
    # Run performance tests
    run_performance_tests()
    
    # Overall result
    if result.wasSuccessful():
        print("\\n🎉 All tests passed! System is ready for production.")
        return True
    else:
        print("\\n⚠️ Some tests failed. Please review and fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)