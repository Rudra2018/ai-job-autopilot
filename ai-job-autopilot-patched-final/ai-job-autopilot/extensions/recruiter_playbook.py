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
[Your Name]
""",

    "german_formal": lambda name, role: f"""
Sehr geehrte/r {name},

Ich bin ein erfahrener Bewerber im Bereich {role} und interessiere mich für eine potenzielle Mitarbeit in Ihrem Unternehmen. 
Gerne würde ich mich vorstellen und mehr über offene Stellen erfahren.

Mit freundlichen Grüßen,
[Ihr Name]
"""
}
