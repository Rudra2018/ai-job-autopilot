from dotenv import load_dotenv
load_dotenv()
import os
TEMPLATES = {
    "cold_intro": lambda name, role, company: f"""
Hi {name},

I came across your work at {company} and wanted to express interest in potential opportunities you might be hiring for in {role}. 
My background aligns closely with the requirements and I'm passionate about contributing to your team.

Would love to connect!

Best,
Ankit Thakur
""",

    "security_specialist": lambda role, company, location: f"""
Hi Hiring Team,

My name is Ankit Thakur and I'm very interested in the {role} position at {company} in {location}. 

With my extensive background in penetration testing, API security, and cloud security at companies like Halodoc Technologies and Prescient Security LLC, I believe I would be a strong fit for your team. My expertise includes:

• Penetration Testing & Vulnerability Assessment
• API Security & Mobile Application Security 
• Cloud Security & DevSecOps Tools
• GDPR Compliance & ISO 27001 Standards
• Risk Analysis & Threat Modeling
• AWS Security Certifications (Security+, Cloud Practitioner, SysOps, Security Specialty)

I have successfully reduced security risks by 25% for clients and improved data protection by 30% through comprehensive security audits. I'd love to discuss how my skills can contribute to your security initiatives.

Best regards,
Ankit Thakur
at87.at17@gmail.com | +91 8717934430
""",

    "german_formal": lambda name, role: f"""
Sehr geehrte/r {name},

Mein Name ist Ankit Thakur und ich bin ein erfahrener Cybersecurity-Spezialist im Bereich {role}. Mit umfangreicher Erfahrung in Penetrationstests, API-Sicherheit und Cloud-Sicherheit interessiere mich für eine potenzielle Mitarbeit in Ihrem Unternehmen.

Gerne würde ich mich vorstellen und mehr über offene Stellen erfahren.

Mit freundlichen Grüßen,
Ankit Thakur
"""
}
