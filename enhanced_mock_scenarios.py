#!/usr/bin/env python3
"""
🧪 Enhanced Mock Data and Test Scenarios
Comprehensive test data generation for realistic testing scenarios
"""

import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class TestScenario:
    """Test scenario configuration"""
    name: str
    description: str
    resume_profile: str
    job_count: int
    expected_matches: int
    success_rate_threshold: float
    test_duration_minutes: int
    complexity_level: str

class EnhancedMockDataGenerator:
    """Enhanced mock data generator for comprehensive testing"""
    
    def __init__(self):
        self.industries = [
            "Technology", "Healthcare", "Finance", "Education", 
            "Retail", "Manufacturing", "Consulting", "Media"
        ]
        
        self.job_titles = {
            "cybersecurity": [
                "Security Engineer", "Cybersecurity Analyst", "SOC Analyst",
                "Penetration Tester", "Security Architect", "CISO",
                "Security Consultant", "Incident Response Specialist"
            ],
            "software_engineering": [
                "Software Engineer", "Full Stack Developer", "Backend Engineer",
                "Frontend Developer", "DevOps Engineer", "Cloud Engineer",
                "Solutions Architect", "Technical Lead"
            ],
            "data_science": [
                "Data Scientist", "ML Engineer", "Data Analyst",
                "AI Researcher", "Business Intelligence Analyst",
                "Data Engineer", "Research Scientist"
            ]
        }
        
        self.company_names = [
            "TechCorp", "InnovateIO", "SecureVault", "DataDriven Inc",
            "CloudFirst Solutions", "CyberGuard", "NextGen Systems",
            "QuantumTech", "SafeNet Industries", "DevOps Masters"
        ]
        
        self.locations = [
            "San Francisco, CA", "New York, NY", "Austin, TX",
            "Seattle, WA", "Boston, MA", "Remote", "Chicago, IL",
            "Los Angeles, CA", "Denver, CO", "Atlanta, GA"
        ]
        
        self.skills_database = {
            "cybersecurity": [
                "penetration testing", "vulnerability assessment", "incident response",
                "security architecture", "threat hunting", "malware analysis",
                "network security", "cloud security", "compliance", "risk assessment"
            ],
            "programming": [
                "python", "javascript", "java", "c++", "go", "rust",
                "typescript", "php", "ruby", "scala"
            ],
            "cloud": [
                "aws", "azure", "gcp", "kubernetes", "docker",
                "terraform", "ansible", "jenkins", "gitlab ci/cd"
            ],
            "databases": [
                "postgresql", "mysql", "mongodb", "redis",
                "elasticsearch", "cassandra", "dynamodb"
            ]
        }

    def generate_test_scenarios(self) -> List[TestScenario]:
        """Generate comprehensive test scenarios"""
        scenarios = [
            TestScenario(
                name="Perfect Match Scenario",
                description="High-skill candidate with perfect job matches",
                resume_profile="senior_cybersecurity",
                job_count=50,
                expected_matches=35,
                success_rate_threshold=0.8,
                test_duration_minutes=15,
                complexity_level="simple"
            ),
            TestScenario(
                name="Career Transition Scenario",
                description="Professional changing career paths",
                resume_profile="transitioning_professional",
                job_count=100,
                expected_matches=25,
                success_rate_threshold=0.5,
                test_duration_minutes=25,
                complexity_level="complex"
            ),
            TestScenario(
                name="Entry Level Scenario",
                description="Recent graduate with limited experience",
                resume_profile="entry_level",
                job_count=75,
                expected_matches=40,
                success_rate_threshold=0.6,
                test_duration_minutes=20,
                complexity_level="medium"
            ),
            TestScenario(
                name="High Volume Processing",
                description="Large scale job processing test",
                resume_profile="senior_software_engineer",
                job_count=500,
                expected_matches=150,
                success_rate_threshold=0.7,
                test_duration_minutes=45,
                complexity_level="stress_test"
            ),
            TestScenario(
                name="Remote Work Focus",
                description="Candidate focused on remote opportunities",
                resume_profile="remote_specialist",
                job_count=80,
                expected_matches=50,
                success_rate_threshold=0.75,
                test_duration_minutes=18,
                complexity_level="medium"
            )
        ]
        return scenarios

    def create_resume_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Create diverse resume profiles for testing"""
        profiles = {
            "senior_cybersecurity": {
                "name": "Alex Johnson",
                "email": "alex.johnson@email.com",
                "experience_years": 8,
                "seniority": "senior",
                "primary_skills": ["penetration testing", "security architecture", "incident response"],
                "secondary_skills": ["python", "aws", "kubernetes"],
                "education_level": "masters",
                "certifications": ["CISSP", "CEH", "OSCP"],
                "salary_expectation": 150000,
                "location_preference": "San Francisco, CA"
            },
            "entry_level": {
                "name": "Jordan Smith",
                "email": "jordan.smith@email.com",
                "experience_years": 1,
                "seniority": "junior",
                "primary_skills": ["python", "sql", "git"],
                "secondary_skills": ["html", "css", "javascript"],
                "education_level": "bachelors",
                "certifications": [],
                "salary_expectation": 65000,
                "location_preference": "Remote"
            },
            "transitioning_professional": {
                "name": "Morgan Davis",
                "email": "morgan.davis@email.com",
                "experience_years": 5,
                "seniority": "mid",
                "primary_skills": ["project management", "business analysis"],
                "secondary_skills": ["python", "data analysis", "sql"],
                "education_level": "bachelors",
                "certifications": ["PMP", "Scrum Master"],
                "salary_expectation": 95000,
                "location_preference": "Austin, TX"
            },
            "senior_software_engineer": {
                "name": "Casey Wilson",
                "email": "casey.wilson@email.com",
                "experience_years": 10,
                "seniority": "senior",
                "primary_skills": ["python", "java", "system design"],
                "secondary_skills": ["aws", "docker", "microservices"],
                "education_level": "masters",
                "certifications": ["AWS Solutions Architect", "Google Cloud Professional"],
                "salary_expectation": 180000,
                "location_preference": "Seattle, WA"
            },
            "remote_specialist": {
                "name": "Taylor Brown",
                "email": "taylor.brown@email.com",
                "experience_years": 6,
                "seniority": "senior",
                "primary_skills": ["javascript", "react", "node.js"],
                "secondary_skills": ["aws", "mongodb", "docker"],
                "education_level": "bachelors",
                "certifications": ["AWS Developer Associate"],
                "salary_expectation": 120000,
                "location_preference": "Remote"
            }
        }
        return profiles

    def generate_job_listings_for_scenario(self, scenario: TestScenario) -> List[Dict[str, Any]]:
        """Generate job listings tailored to a specific test scenario"""
        jobs = []
        profiles = self.create_resume_profiles()
        profile = profiles[scenario.resume_profile]
        
        # Generate jobs with varying match quality
        high_match_count = int(scenario.job_count * 0.3)  # 30% high matches
        medium_match_count = int(scenario.job_count * 0.4)  # 40% medium matches
        low_match_count = scenario.job_count - high_match_count - medium_match_count
        
        # High match jobs
        for i in range(high_match_count):
            jobs.append(self._create_high_match_job(profile, i))
        
        # Medium match jobs
        for i in range(medium_match_count):
            jobs.append(self._create_medium_match_job(profile, i + high_match_count))
        
        # Low match jobs
        for i in range(low_match_count):
            jobs.append(self._create_low_match_job(profile, i + high_match_count + medium_match_count))
        
        return jobs

    def _create_high_match_job(self, profile: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Create a job that should match well with the profile"""
        domain = "cybersecurity" if "security" in str(profile["primary_skills"]) else "software_engineering"
        
        job = {
            "id": f"high_match_{index:03d}",
            "title": f"{profile['seniority'].title()} {random.choice(self.job_titles[domain])}",
            "company": random.choice(self.company_names),
            "location": profile["location_preference"],
            "salary_range": f"${profile['salary_expectation'] - 10000}-${profile['salary_expectation'] + 20000}",
            "required_skills": profile["primary_skills"][:2] + profile["secondary_skills"][:1],
            "preferred_skills": profile["secondary_skills"],
            "experience_required": f"{max(1, profile['experience_years'] - 2)}-{profile['experience_years'] + 2} years",
            "education_required": profile["education_level"],
            "remote_friendly": profile["location_preference"] == "Remote",
            "company_size": random.choice(["startup", "medium", "large"]),
            "industry": random.choice(self.industries),
            "job_type": "full-time",
            "posted_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "application_deadline": (datetime.now() + timedelta(days=random.randint(7, 60))).isoformat(),
            "description": f"We are looking for a {profile['seniority']} professional with expertise in {', '.join(profile['primary_skills'])}",
            "easy_apply": random.choice([True, False]),
            "match_probability": random.uniform(0.8, 0.95)
        }
        return job

    def _create_medium_match_job(self, profile: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Create a job that should partially match the profile"""
        domain = random.choice(list(self.job_titles.keys()))
        
        job = {
            "id": f"medium_match_{index:03d}",
            "title": random.choice(self.job_titles[domain]),
            "company": random.choice(self.company_names),
            "location": random.choice(self.locations),
            "salary_range": f"${profile['salary_expectation'] - 20000}-${profile['salary_expectation'] + 10000}",
            "required_skills": random.sample(profile["primary_skills"] + profile["secondary_skills"], 2),
            "preferred_skills": random.sample(sum(self.skills_database.values(), []), 3),
            "experience_required": f"{max(1, profile['experience_years'] - 3)}-{profile['experience_years'] + 3} years",
            "education_required": random.choice(["bachelors", "masters"]),
            "remote_friendly": random.choice([True, False]),
            "company_size": random.choice(["startup", "medium", "large"]),
            "industry": random.choice(self.industries),
            "job_type": random.choice(["full-time", "contract", "part-time"]),
            "posted_date": (datetime.now() - timedelta(days=random.randint(1, 45))).isoformat(),
            "application_deadline": (datetime.now() + timedelta(days=random.randint(7, 90))).isoformat(),
            "description": "Looking for a motivated professional with relevant experience",
            "easy_apply": random.choice([True, False]),
            "match_probability": random.uniform(0.5, 0.79)
        }
        return job

    def _create_low_match_job(self, profile: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Create a job that should not match well with the profile"""
        domain = random.choice(list(self.job_titles.keys()))
        
        # Intentionally mismatched requirements
        mismatched_skills = random.sample(sum(self.skills_database.values(), []), 3)
        mismatched_skills = [skill for skill in mismatched_skills 
                           if skill not in profile["primary_skills"] + profile["secondary_skills"]]
        
        job = {
            "id": f"low_match_{index:03d}",
            "title": random.choice(self.job_titles[domain]),
            "company": random.choice(self.company_names),
            "location": random.choice([loc for loc in self.locations if loc != profile["location_preference"]]),
            "salary_range": f"${max(30000, profile['salary_expectation'] - 50000)}-${profile['salary_expectation'] - 30000}",
            "required_skills": mismatched_skills[:3] if mismatched_skills else ["specialized_skill", "niche_tool"],
            "preferred_skills": random.sample(sum(self.skills_database.values(), []), 2),
            "experience_required": f"{profile['experience_years'] + 5}-{profile['experience_years'] + 10} years" if random.choice([True, False]) else "0-2 years",
            "education_required": "phd" if profile["education_level"] == "bachelors" else "high school",
            "remote_friendly": not (profile["location_preference"] == "Remote"),
            "company_size": random.choice(["startup", "medium", "large"]),
            "industry": random.choice(self.industries),
            "job_type": random.choice(["internship", "contract", "part-time"]),
            "posted_date": (datetime.now() - timedelta(days=random.randint(60, 120))).isoformat(),
            "application_deadline": (datetime.now() + timedelta(days=random.randint(1, 7))).isoformat(),
            "description": "Seeking candidates with very specific requirements",
            "easy_apply": False,
            "match_probability": random.uniform(0.1, 0.49)
        }
        return job

    def create_application_test_data(self) -> Dict[str, Any]:
        """Create test data for form filling scenarios"""
        return {
            "personal_info": {
                "first_name": "Test",
                "last_name": "Candidate",
                "email": "test.candidate@example.com",
                "phone": "+1-555-0199",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "CA",
                "zip_code": "94000",
                "country": "United States"
            },
            "work_authorization": {
                "authorized_to_work": True,
                "visa_sponsorship_needed": False,
                "security_clearance": "None"
            },
            "preferences": {
                "salary_expectation": 120000,
                "start_date": "Immediately",
                "willing_to_relocate": True,
                "remote_work_preference": "Hybrid"
            },
            "additional_info": {
                "cover_letter": "I am excited about this opportunity to contribute to your team...",
                "portfolio_url": "https://testcandidate.dev",
                "linkedin_url": "https://linkedin.com/in/testcandidate",
                "github_url": "https://github.com/testcandidate"
            }
        }

    def generate_performance_test_data(self, scale: str = "medium") -> Dict[str, Any]:
        """Generate data for performance testing"""
        scales = {
            "small": {"jobs": 50, "companies": 10, "resumes": 5},
            "medium": {"jobs": 200, "companies": 25, "resumes": 10},
            "large": {"jobs": 1000, "companies": 50, "resumes": 25},
            "stress": {"jobs": 5000, "companies": 100, "resumes": 50}
        }
        
        config = scales.get(scale, scales["medium"])
        
        return {
            "job_listings": [self._create_random_job(i) for i in range(config["jobs"])],
            "companies": [self._create_random_company(i) for i in range(config["companies"])],
            "resume_profiles": [self._create_random_resume_profile(i) for i in range(config["resumes"])],
            "expected_processing_time": config["jobs"] * 0.1,  # seconds
            "memory_limit_mb": 500,
            "concurrent_workers": min(10, config["jobs"] // 10)
        }

    def _create_random_job(self, index: int) -> Dict[str, Any]:
        """Create a random job listing"""
        domain = random.choice(list(self.job_titles.keys()))
        return {
            "id": f"perf_job_{index:04d}",
            "title": random.choice(self.job_titles[domain]),
            "company": random.choice(self.company_names),
            "location": random.choice(self.locations),
            "salary_range": f"${random.randint(60, 200)}k-${random.randint(80, 250)}k",
            "required_skills": random.sample(sum(self.skills_database.values(), []), 3),
            "experience_required": f"{random.randint(0, 10)}-{random.randint(2, 15)} years",
            "posted_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            "match_probability": random.uniform(0.1, 0.9)
        }

    def _create_random_company(self, index: int) -> Dict[str, Any]:
        """Create a random company profile"""
        return {
            "id": f"company_{index:03d}",
            "name": f"Company {index}",
            "industry": random.choice(self.industries),
            "size": random.choice(["startup", "small", "medium", "large", "enterprise"]),
            "location": random.choice(self.locations),
            "careers_url": f"https://company{index}.com/careers",
            "description": f"Leading company in {random.choice(self.industries)}"
        }

    def _create_random_resume_profile(self, index: int) -> Dict[str, Any]:
        """Create a random resume profile"""
        domain = random.choice(list(self.skills_database.keys()))
        return {
            "id": f"resume_{index:03d}",
            "name": f"Candidate {index}",
            "skills": random.sample(self.skills_database[domain], 3),
            "experience_years": random.randint(1, 15),
            "education": random.choice(["bachelors", "masters", "phd"]),
            "location": random.choice(self.locations)
        }

    def save_test_scenarios(self, output_dir: str = "data/test_scenarios") -> None:
        """Save all test scenarios and data to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save scenarios
        scenarios = self.generate_test_scenarios()
        with open(output_path / "test_scenarios.json", "w") as f:
            json.dump([asdict(s) for s in scenarios], f, indent=2)
        
        # Save resume profiles
        profiles = self.create_resume_profiles()
        with open(output_path / "resume_profiles.json", "w") as f:
            json.dump(profiles, f, indent=2)
        
        # Save job listings for each scenario
        for scenario in scenarios:
            jobs = self.generate_job_listings_for_scenario(scenario)
            with open(output_path / f"jobs_{scenario.name.lower().replace(' ', '_')}.json", "w") as f:
                json.dump(jobs, f, indent=2)
        
        # Save application test data
        app_data = self.create_application_test_data()
        with open(output_path / "application_test_data.json", "w") as f:
            json.dump(app_data, f, indent=2)
        
        # Save performance test data
        for scale in ["small", "medium", "large", "stress"]:
            perf_data = self.generate_performance_test_data(scale)
            with open(output_path / f"performance_test_{scale}.json", "w") as f:
                json.dump(perf_data, f, indent=2, default=str)
        
        print(f"✅ Test scenarios and data saved to {output_path}")

def main():
    """Generate and save all test scenarios"""
    print("🧪 Generating Enhanced Mock Data and Test Scenarios...")
    
    generator = EnhancedMockDataGenerator()
    generator.save_test_scenarios()
    
    # Display summary
    scenarios = generator.generate_test_scenarios()
    profiles = generator.create_resume_profiles()
    
    print(f"\n📊 Generated Test Data Summary:")
    print(f"   🎯 Test Scenarios: {len(scenarios)}")
    print(f"   👤 Resume Profiles: {len(profiles)}")
    print(f"   💼 Job Listings: {sum(s.job_count for s in scenarios)}")
    print(f"   🏢 Performance Test Scales: 4 (small, medium, large, stress)")
    
    print("\n🎭 Test Scenario Overview:")
    for scenario in scenarios:
        print(f"   • {scenario.name}: {scenario.job_count} jobs, {scenario.expected_matches} expected matches")

if __name__ == "__main__":
    main()