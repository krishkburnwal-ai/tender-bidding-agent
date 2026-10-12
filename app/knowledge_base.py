import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings

DEFAULT_COMPANY_PROFILE = {
    "company_name": "NexGen Infotech & Solutions Pvt. Ltd.",
    "registration_number": "U72200DL2016PTC294812",
    "incorporation_year": 2016,
    "years_in_business": 10,
    "headquarters": "New Delhi & Bengaluru, India",
    "pan_number": "AABCN1234F",
    "gstin": "07AABCN1234F1Z9",
    "msme_registration": "UDYAM-DL-08-0029410 (Medium Enterprise)",
    "dpiit_recognized": True,
    "total_workforce": 145,
    "financials": {
        "turnover_fy_23_24_inr": 425000000,
        "turnover_fy_22_23_inr": 358000000,
        "turnover_fy_21_22_inr": 284000000,
        "average_annual_turnover_inr": 355666667,
        "average_turnover_crores": 35.57,
        "net_worth_inr": 182000000,
        "net_worth_crores": 18.2,
        "solvency_certificate_amount_inr": 150000000,
        "solvency_crores": 15.0,
        "banker": "State Bank of India (CAG Branch)"
    },
    "certifications": [
        {"name": "ISO 9001:2015", "desc": "Quality Management Systems", "valid_until": "2027-11-30"},
        {"name": "ISO 27001:2022", "desc": "Information Security Management", "valid_until": "2027-08-15"},
        {"name": "ISO 20000-1:2018", "desc": "IT Service Management", "valid_until": "2028-02-28"},
        {"name": "CMMI Level 3 (DEV)", "desc": "Capability Maturity Model Integration", "valid_until": "2027-05-14"},
        {"name": "SOC 2 Type II", "desc": "Security, Availability & Confidentiality", "valid_until": "2026-12-31"},
        {"name": "MeitY Cloud Partner", "desc": "Empanelled MSP with AWS, Azure & CtrlS", "valid_until": "Active"}
    ],
    "core_competencies": [
        "Cloud Migration & Cloud-Native Microservices Architecture",
        "Large-scale e-Governance & Citizen Portal Development",
        "Smart City IoT Platforms & Integrated Command Control Centers (ICCC)",
        "Enterprise AI/ML, NLP Document Digitization & Process Automation",
        "Cybersecurity Operations, DevSecOps & Zero Trust Architecture",
        "24x7 Tier-3 IT Managed Operations & SLA-Backed Support (99.95% uptime)"
    ]
}

DEFAULT_PAST_PROPOSALS = [
    {
        "id": "PROP-2024-001",
        "project_name": "State-wide Unified e-Governance Citizen Portal & Single Window Clearance",
        "client": "Department of Electronics & IT, Government of Karnataka",
        "contract_value_inr": 148000000,
        "contract_value_crores": 14.8,
        "duration_months": 36,
        "status": "Successfully Delivered & Maintained",
        "completion_year": 2024,
        "scope_summary": "Architecture, cloud migration, containerization, and 24x7 SLA support for a high-traffic citizen service portal handling 15M+ requests annually. Integrated with DigiLocker, Aadhaar SSO, and payment gateways.",
        "technologies": ["Kubernetes", "PostgreSQL Enterprise", "React", "Python FastAPI", "Kafka", "AWS GovCloud"],
        "outcomes": "Achieved 99.98% uptime across 3 years. Reduced average citizen application turnaround from 14 days to 48 hours. Won National e-Governance Award 2024."
    },
    {
        "id": "PROP-2023-014",
        "project_name": "Smart City Integrated Command and Control Center (ICCC) IoT Data Platform",
        "client": "Pune Smart City Development Corporation Ltd. (PSCDCL)",
        "contract_value_inr": 185000000,
        "contract_value_crores": 18.5,
        "duration_months": 48,
        "status": "Active / Fully Operational",
        "completion_year": 2023,
        "scope_summary": "Designed and deployed city-wide IoT telemetry ingestion engine, smart traffic management integration, environmental sensor dashboards, and GIS geospatial mapping for municipal surveillance.",
        "technologies": ["Apache Kafka", "TimescaleDB", "Microservices", "Docker", "GIS Mapbox", "Edge Gateways"],
        "outcomes": "Connecting over 3,200 real-time sensors across the metropolitan zone with sub-second alert dispatch."
    },
    {
        "id": "PROP-2022-009",
        "project_name": "Cloud-Based Healthcare MIS & Hospital Operations Platform",
        "client": "State Health Assurance Society, Maharashtra",
        "contract_value_inr": 92000000,
        "contract_value_crores": 9.2,
        "duration_months": 24,
        "status": "Successfully Completed",
        "completion_year": 2023,
        "scope_summary": "Digitization of 450+ district and taluka hospital health records, Ayushman Bharat Digital Mission (ABDM) integration, telemedicine modules, and automated drug inventory tracking.",
        "technologies": ["Python", "Angular", "Redis", "Elasticsearch", "ABDM M1/M2/M3 APIs", "PostgreSQL"],
        "outcomes": "Over 4.5 million patient electronic medical records secured; 100% compliance with ABDM national standards."
    },
    {
        "id": "PROP-2022-003",
        "project_name": "AI-Powered Citizen Grievance Redressal & Ticket Management Automation",
        "client": "Municipal Corporation of Greater Mumbai (MCGM)",
        "contract_value_inr": 64000000,
        "contract_value_crores": 6.4,
        "duration_months": 24,
        "status": "Successfully Completed",
        "completion_year": 2022,
        "scope_summary": "Automated multilingual grievance classification, routing, and sentiment escalation using NLP for civic complaints across WhatsApp, web, and IVR.",
        "technologies": ["NLP LLM Pipelines", "FastAPI", "React", "RabbitMQ", "PostgreSQL"],
        "outcomes": "64% reduction in first-response resolution time; 100,000+ tickets auto-categorized every month."
    }
]

DEFAULT_TEAM_PROFILES = [
    {
        "name": "Dr. Rajesh Sharma",
        "role": "Chief Solution Architect & Project Director",
        "experience_years": 18,
        "qualifications": "Ph.D. Computer Science, M.Tech IIT Delhi, B.Tech CSE",
        "certifications": ["PMP (PMI)", "AWS Certified Solutions Architect - Professional", "TOGAF 9.2 Certified"],
        "relevant_projects": "Project Director for Karnataka e-Governance Portal and Pune Smart City ICCC."
    },
    {
        "name": "Priya Nair",
        "role": "Lead Cloud Infrastructure & DevOps Architect",
        "experience_years": 13,
        "qualifications": "M.S. Software Systems (BITS Pilani), B.Tech IT",
        "certifications": ["CKA (Certified Kubernetes Administrator)", "Microsoft Azure Solutions Architect Expert", "HashiCorp Certified Terraform Associate"],
        "relevant_projects": "Led cloud migration and High Availability deployment for State Health MIS and Urban Citizen Portal."
    },
    {
        "name": "Amitav Roy",
        "role": "Principal Cybersecurity & Compliance Lead",
        "experience_years": 11,
        "qualifications": "B.Tech CSE, Executive PG Diploma in Cyber Law & Security",
        "certifications": ["CISSP (Certified Information Systems Security Professional)", "CEH (Certified Ethical Hacker)", "ISO 27001 Lead Auditor"],
        "relevant_projects": "Spearheaded STQC and CERT-In security audits for 5+ government procurement and citizen applications."
    },
    {
        "name": "Sneha Kulkarni",
        "role": "Quality Assurance & Service Delivery Manager",
        "experience_years": 10,
        "qualifications": "B.E. Information Technology, MBA Project Management",
        "certifications": ["ISTQB Advanced Level", "Certified ScrumMaster (CSM)", "ITIL v4 Managing Professional"],
        "relevant_projects": "Managed SLA delivery, automated regression test suites, and 24x7 operations center for Pune Smart City."
    }
]

class KnowledgeBase:
    """Manages company credentials, past proposals, and supporting profiles."""
    
    def __init__(self):
        self._ensure_files()

    def _ensure_files(self):
        # Write default company profile if absent
        if not settings.COMPANY_PROFILE_PATH.exists():
            with open(settings.COMPANY_PROFILE_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_COMPANY_PROFILE, f, indent=2)
                
        # Write default past proposals if absent
        if not settings.PAST_PROPOSALS_PATH.exists():
            with open(settings.PAST_PROPOSALS_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_PAST_PROPOSALS, f, indent=2)

        # Write default team profiles if absent
        if not settings.TEAM_PROFILES_PATH.exists():
            with open(settings.TEAM_PROFILES_PATH, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_TEAM_PROFILES, f, indent=2)

    def get_company_profile(self) -> Dict[str, Any]:
        with open(settings.COMPANY_PROFILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_company_profile(self, data: Dict[str, Any]) -> None:
        with open(settings.COMPANY_PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_past_proposals(self) -> List[Dict[str, Any]]:
        with open(settings.PAST_PROPOSALS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_past_proposals(self, data: List[Dict[str, Any]]) -> None:
        with open(settings.PAST_PROPOSALS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_past_proposal(self, proposal: Dict[str, Any]) -> None:
        proposals = self.get_past_proposals()
        proposals.insert(0, proposal)
        self.save_past_proposals(proposals)

    def get_team_profiles(self) -> List[Dict[str, Any]]:
        with open(settings.TEAM_PROFILES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_team_profiles(self, data: List[Dict[str, Any]]) -> None:
        with open(settings.TEAM_PROFILES_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_context_summary(self) -> str:
        """Constructs a comprehensive knowledge summary for prompt injection."""
        cp = self.get_company_profile()
        proposals = self.get_past_proposals()
        team = self.get_team_profiles()

        summary_parts = []
        summary_parts.append(f"COMPANY NAME: {cp['company_name']}")
        summary_parts.append(f"EXPERIENCE: Established {cp['incorporation_year']} ({cp['years_in_business']} years in IT & Govtech)")
        summary_parts.append(f"TURNOVER: FY23-24: ₹{cp['financials']['turnover_fy_23_24_inr'] / 1e7:.2f} Cr, 3-Yr Avg: ₹{cp['financials']['average_turnover_crores']} Cr")
        summary_parts.append(f"NET WORTH: ₹{cp['financials']['net_worth_crores']} Cr, Solvency: ₹{cp['financials']['solvency_crores']} Cr")
        summary_parts.append(f"REGISTRATIONS: GST: {cp['gstin']}, PAN: {cp['pan_number']}, MSME: {cp['msme_registration']}")
        
        certs = ", ".join([c["name"] for c in cp["certifications"]])
        summary_parts.append(f"CERTIFICATIONS: {certs}")
        
        summary_parts.append("\nRELEVANT PAST PROPOSALS & CREDENTIALS:")
        for p in proposals[:4]:
            summary_parts.append(f"- {p['project_name']} (Client: {p['client']}, Value: ₹{p['contract_value_crores']} Cr, Status: {p['status']}) - Scope: {p['scope_summary']}")

        summary_parts.append("\nKEY BID TEAM PROFILES:")
        for m in team:
            summary_parts.append(f"- {m['name']} ({m['role']}, {m['experience_years']} yrs exp, {m['qualifications']}) - Certs: {', '.join(m['certifications'])}")

        return "\n".join(summary_parts)

knowledge_base = KnowledgeBase()
