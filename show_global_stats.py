#!/usr/bin/env python3
"""
Global Statistics Dashboard for Enhanced AI Job Autopilot
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

def load_application_log():
    """Load application log data"""
    log_path = Path("dashboard/application_log.jsonl")
    if not log_path.exists():
        return []
    
    applications = []
    with open(log_path, 'r') as f:
        for line in f:
            applications.append(json.loads(line.strip()))
    return applications

def analyze_applications():
    """Analyze application patterns"""
    applications = load_application_log()
    
    print("🌍 GLOBAL CYBERSECURITY JOB APPLICATION ANALYSIS")
    print("="*70)
    
    if not applications:
        print("No applications found in log.")
        return
    
    # Regional analysis
    print(f"📊 Total Applications: {len(applications)}")
    print()
    
    regions = defaultdict(list)
    for app in applications:
        location = app.get('location', 'Unknown')
        if any(country in location for country in ['UK', 'Netherlands', 'Ireland', 'Switzerland', 'France', 'Sweden', 'Denmark', 'Norway', 'Finland', 'Austria', 'Belgium', 'Luxembourg']):
            regions['EMEA'].append(app)
        elif 'Germany' in location:
            regions['Germany'].append(app)
        elif any(state in location for state in ['NY', 'CA', 'TX', 'WA', 'IL', 'MA', 'DC', 'GA', 'FL', 'CO', 'NC', 'AZ']):
            regions['USA'].append(app)
        elif 'Remote' in location:
            regions['Remote'].append(app)
        else:
            regions['Other'].append(app)
    
    print("🗺️  REGIONAL BREAKDOWN:")
    for region, apps in regions.items():
        print(f"   {region}: {len(apps)} applications")
        for app in apps[:3]:  # Show top 3 per region
            print(f"      • {app['title']} @ {app['company']} ({app['location']})")
        if len(apps) > 3:
            print(f"      ... and {len(apps) - 3} more")
        print()
    
    # Company analysis
    companies = Counter(app['company'] for app in applications)
    print("🏢 TOP TARGET COMPANIES:")
    for company, count in companies.most_common(10):
        print(f"   {company}: {count} applications")
    print()
    
    # Role analysis
    roles = Counter(app['title'] for app in applications)
    print("💼 CYBERSECURITY ROLES APPLIED:")
    for role, count in roles.most_common():
        print(f"   {role}: {count} applications")
    print()
    
    # Success rate
    successful = sum(1 for app in applications if app.get('status') == 'applied')
    success_rate = (successful / len(applications)) * 100 if applications else 0
    print(f"✅ APPLICATION SUCCESS RATE: {success_rate:.1f}% ({successful}/{len(applications)})")
    print()
    
    # Recent applications
    print("🕒 RECENT APPLICATIONS:")
    for app in applications[-5:]:
        status_icon = "✅" if app.get('status') == 'applied' else "❌"
        print(f"   {status_icon} {app['title']} @ {app['company']} ({app['location']})")
    
    return applications

def show_enhanced_features():
    """Show the enhanced features of the system"""
    print("\n" + "="*70)
    print("🚀 ENHANCED AI JOB AUTOPILOT FEATURES")
    print("="*70)
    
    features = [
        "🌍 Global Coverage: EMEA, Germany, USA regions",
        "🎯 Cybersecurity Focus: 18+ specialized role types",
        "⚡ LinkedIn Easy Apply: Automated form filling",
        "🧠 Enhanced AI Matching: JobBERT-v3 + bonus scoring",
        "📧 Personalized Messages: Ankit's actual experience & skills",
        "📊 Smart Filtering: Location, role, and keyword bonuses",
        "🏆 Company Targeting: Top-tier tech and financial companies",
        "📈 Real-time Analytics: Live dashboard with statistics",
        "🔄 Batch Processing: Up to 50 applications per day",
        "💼 Professional Templates: Industry-specific messaging"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print(f"\n📍 TARGET LOCATIONS ({sum(len(regions) for regions in [
        ['London', 'Amsterdam', 'Dublin', 'Zurich', 'Paris', 'Stockholm'],  # EMEA
        ['Berlin', 'Munich', 'Frankfurt', 'Hamburg', 'Cologne'],  # Germany  
        ['New York', 'San Francisco', 'Seattle', 'Austin', 'Chicago']  # USA
    ])}):")
    
    emea_cities = ['London, UK', 'Amsterdam, Netherlands', 'Dublin, Ireland', 'Zurich, Switzerland', 
                  'Paris, France', 'Stockholm, Sweden', 'Copenhagen, Denmark', 'Oslo, Norway']
    germany_cities = ['Berlin', 'Munich', 'Frankfurt', 'Hamburg', 'Cologne', 'Stuttgart', 'Düsseldorf']
    usa_cities = ['New York, NY', 'San Francisco, CA', 'Seattle, WA', 'Austin, TX', 'Chicago, IL', 
                 'Boston, MA', 'Washington, DC']
    
    print(f"   🇪🇺 EMEA: {', '.join(emea_cities[:4])} + {len(emea_cities)-4} more")
    print(f"   🇩🇪 Germany: {', '.join(germany_cities[:4])} + {len(germany_cities)-4} more")  
    print(f"   🇺🇸 USA: {', '.join(usa_cities[:4])} + {len(usa_cities)-4} more")

def show_config_summary():
    """Show current configuration"""
    import yaml
    
    print(f"\n📋 CURRENT CONFIGURATION:")
    config_path = Path("config/user_profile.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"   👤 Candidate: {config.get('name', 'Not set')}")
        print(f"   📧 Email: {config.get('email', 'Not set')}")
        print(f"   📱 Phone: {config.get('phone', 'Not set')}")
        
        automation = config.get('job_preferences', {}).get('automation', {})
        print(f"   🤖 Easy Apply: {automation.get('easy_apply', 'Not set')}")
        print(f"   📈 Max Applications/Day: {automation.get('max_applications_per_day', 'Not set')}")
        print(f"   🎯 Match Threshold: {automation.get('target_match_threshold', 'Not set')}%")
        
        titles = config.get('job_preferences', {}).get('titles', [])
        print(f"   💼 Target Roles: {len(titles)} configured")

if __name__ == "__main__":
    applications = analyze_applications()
    show_enhanced_features() 
    show_config_summary()
    
    print(f"\n🎉 SYSTEM STATUS: ACTIVE")
    print(f"📊 Dashboard: http://localhost:8501")
    print(f"📁 Application Log: dashboard/application_log.jsonl")
    print(f"⚡ Ready for next autopilot run!")