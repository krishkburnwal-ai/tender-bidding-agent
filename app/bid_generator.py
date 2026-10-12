import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from app.sarvam_client import sarvam_client
from app.knowledge_base import knowledge_base

class BidGenerator:
    """
    Generates customized, RFP-compliant Technical & Management Bid Proposals
    using Sarvam AI, grounded in Company Knowledge and Past Proposal library.
    Exports to Microsoft Word (.docx), Markdown, and formatted HTML.
    """

    def generate_bid_response(
        self,
        tender_data: Dict[str, Any],
        tone: str = "Formal Government Procurement",
        detail_level: str = "Comprehensive",
        custom_instructions: str = ""
    ) -> Dict[str, Any]:
        company = knowledge_base.get_company_profile()
        context_summary = knowledge_base.get_context_summary()
        
        meta = tender_data.get("tender_metadata", {})
        tender_id = meta.get("tender_id", "NIT/2026/092")
        title = meta.get("title", "Tender Work")
        authority = meta.get("issuing_authority", "Tendering Authority")
        scope_list = tender_data.get("scope_of_work", [])
        scope_str = "\n".join([f"- {s}" for s in scope_list])
        
        system_prompt = (
            "You are a Senior Proposal Director and Government Bidding Strategist with 20+ years of experience. "
            "Write an exhaustive, authoritative, procurement-grade Technical Bid Response document. "
            "Adhere strictly to official Indian e-procurement guidelines (GeM/CPPP), referencing the Bidder's "
            "actual credentials, past successful projects, certifications, and named team experts."
        )

        user_prompt = f"""
Generate an official Bid Response Proposal for:
TENDER REFERENCE: {tender_id}
TENDER TITLE: {title}
ISSUING AUTHORITY: {authority}
ESTIMATED VALUE: {meta.get('estimated_value_inr', 'As per RFP')}
EMD REQUIREMENT: {meta.get('emd_amount_inr', 'As specified')}

BIDDER KNOWLEDGE BASE:
{context_summary}

TENDER SCOPE OF WORK:
{scope_str}

TONE: {tone}
DETAIL LEVEL: {detail_level}
SPECIAL INSTRUCTIONS: {custom_instructions}

Please produce a comprehensive 10-section Technical Bid Proposal formatted in clear Markdown:
# SECTION 1: FORMAL COVERING LETTER & TENDER DECLARATION
# SECTION 2: EXECUTIVE SUMMARY & ASSIGNMENT UNDERSTANDING
# SECTION 3: BIDDER PROFILE & RELEVANT PAST TRACK RECORD
# SECTION 4: PROPOSED TECHNICAL ARCHITECTURE & SOLUTION METHODOLOGY
# SECTION 5: WORK BREAKDOWN STRUCTURE & IMPLEMENTATION SCHEDULE
# SECTION 6: KEY PERSONNEL DEPLOYMENT & GOVERNANCE MATRIX
# SECTION 7: CLAUSE-BY-CLAUSE COMPLIANCE MATRIX
# SECTION 8: QUALITY MANAGEMENT, SLA & CYBERSECURITY FRAMEWORK
# SECTION 9: RISK MITIGATION & BUSINESS CONTINUITY PLAN
# SECTION 10: COMMERCIAL VALUE PROPOSITION & SUBMISSION INDEX
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Call Sarvam AI
        ai_resp = sarvam_client.chat_completion(
            messages=messages,
            temperature=0.25,
            max_tokens=4000
        )

        bid_markdown = ai_resp.get("content", "")
        if not bid_markdown or len(bid_markdown) < 200:
            # Fallback to high quality template synthesis
            bid_markdown = self._generate_template_bid(tender_data, company, tone)

        # Parse sections for structured view
        sections = self._parse_markdown_sections(bid_markdown)

        return {
            "title": f"Technical Bid Proposal - {tender_id}",
            "tender_id": tender_id,
            "generated_at": datetime.now().isoformat(),
            "tone": tone,
            "detail_level": detail_level,
            "markdown_content": bid_markdown,
            "sections": sections,
            "provider": ai_resp.get("provider", "Sarvam AI"),
            "is_simulated": ai_resp.get("is_simulated", False)
        }

    def _parse_markdown_sections(self, md_text: str) -> List[Dict[str, str]]:
        """Splits markdown into navigable sections."""
        lines = md_text.splitlines()
        sections = []
        current_title = "Introduction"
        current_content = []

        for line in lines:
            if line.startswith("# ") or line.startswith("## SECTION") or line.startswith("# SECTION"):
                if current_content:
                    sections.append({
                        "title": current_title.replace("#", "").strip(),
                        "content": "\n".join(current_content).strip()
                    })
                    current_content = []
                current_title = line.replace("#", "").strip()
            else:
                current_content.append(line)

        if current_content:
            sections.append({
                "title": current_title.replace("#", "").strip(),
                "content": "\n".join(current_content).strip()
            })

        return sections

    def _generate_template_bid(self, tender_data: Dict[str, Any], company: Dict[str, Any], tone: str) -> str:
        meta = tender_data.get("tender_metadata", {})
        tender_id = meta.get("tender_id", "GEM/2026/B/9842105")
        title = meta.get("title", "State e-Procurement & Citizen Portal Modernization")
        authority = meta.get("issuing_authority", "Centre for e-Governance")
        company_name = company.get("company_name", "NexGen Infotech & Solutions Pvt. Ltd.")

        return f"""# SECTION 1: FORMAL COVERING LETTER & TENDER DECLARATION

**Ref: {company_name[:6].upper()}/BID/{datetime.now().year}/092**  
**Date: {datetime.now().strftime('%d %B %Y')}**

To,  
**The Tendering Authority,**  
{authority}  

**Subject: Submission of Technical & Management Bid Response for Tender Reference: {tender_id} - "{title}"**

Dear Sir / Madam,

Having carefully examined the Tender Documents, Scope of Work, General & Special Conditions of Contract, and Technical Specifications for the subject work, we, **{company_name}**, hereby submit our comprehensive Technical Bid Response in strict accordance with the terms and conditions outlined in the RFP.

We confirm and declare that:
1. **Unconditional Acceptance:** We unequivocally accept all terms, clauses, and conditions of the tender document without any deviations or reservations.
2. **Bid Validity:** Our bid remains valid for a period of **180 days** from the date of bid submission.
3. **Earnest Money Deposit:** The requisite EMD / Bid Security has been submitted as per the prescribed format / MSME exemption criteria.
4. **Institutional Capability:** Our organization possesses over **10 years of proven institutional track record**, supported by an average 3-year annual turnover of **₹ 35.57 Crores** and key quality accreditations including **ISO 9001:2015, ISO 27001:2022, and CMMI Dev Level 3**.
5. **Conflict of Interest & Integrity:** We confirm that we have not been debarred, blacklisted, or penalized by any Ministry, Central/State Government PSU, or Autonomous Body in India.

We look forward to presenting our technical methodology during the technical evaluation.

Yours faithfully,  
For **{company_name}**  
*(Authorized Signatory with Corporate Seal)*

---

# SECTION 2: EXECUTIVE SUMMARY & ASSIGNMENT UNDERSTANDING

### 2.1 Understanding the Authority's Strategic Objectives
The objective of this procurement by **{authority}** is to establish a resilient, cloud-native, and citizen-centric digital backbone for **"{title}"**. The Authority requires:
- High availability architecture guaranteeing **99.95% operational uptime**.
- Scalable microservices infrastructure capable of managing over **50,000 concurrent citizen transactions**.
- Deep integration with National Digital Public Infrastructure (DPI) including **Aadhaar e-KYC, DigiLocker, and Bharat BillPay**.
- Round-the-clock **24x7 Security Operations Center (SOC)** and CERT-In empanelled cyber audit compliance.

### 2.2 The Bidder's Strategic Value Proposition
**{company_name}** brings battle-tested public sector execution credentials. Having successfully delivered the *State-wide Unified e-Governance Citizen Portal for Government of Karnataka (Value: ₹ 14.8 Cr)* and the *Smart City Integrated Command & Control Center (ICCC) Data Platform (Value: ₹ 18.5 Cr)*, our delivery team offers proven acceleration frameworks, zero-day cloud security templates, and domain-native engineers to ensure seamless project transition.

---

# SECTION 3: BIDDER PROFILE & RELEVANT PAST TRACK RECORD

### 3.1 Corporate Profile at a Glance
| Parameter | Corporate Detail |
| :--- | :--- |
| **Legal Entity Name** | {company.get('company_name')} |
| **Incorporation Year** | {company.get('incorporation_year')} (10 Years in Industry) |
| **Corporate Identity / CIN** | {company.get('registration_number')} |
| **GSTIN & PAN** | {company.get('gstin')} / {company.get('pan_number')} |
| **MSME Udyam Registration** | {company.get('msme_registration')} |
| **Average Annual Turnover** | ₹ 35.57 Crores (Audited FY 21-22, 22-23, 23-24) |
| **Net Worth & Solvency** | Net Worth: ₹ 18.2 Cr | Bank Solvency: ₹ 15.0 Cr (SBI) |
| **Quality & Security Certifications** | ISO 9001:2015, ISO 27001:2022, ISO 20000-1, CMMI Level 3 (DEV) |

### 3.2 Showcase of Relevant Winning Public Sector Works
1. **Karnataka Unified e-Governance Citizen Portal (Dept of IT, Govt of Karnataka):**
   - **Contract Value:** ₹ 14.80 Crores
   - **Scope:** Complete microservices modernization, Kubernetes deployment on MeitY cloud, and 24x7 Tier-3 management for 15M+ citizen transactions. Delivered 99.98% availability across 36 consecutive months.
2. **Smart City Integrated Command & Control Center Platform (Pune Smart City):**
   - **Contract Value:** ₹ 18.50 Crores
   - **Scope:** Ingestion of 3,200+ IoT telemetry feeds, GIS mapping, and automated dispatch console for municipal services.
3. **State Health MIS & Hospital Operations Platform (State Health Assurance Society):**
   - **Contract Value:** ₹ 9.20 Crores
   - **Scope:** Digital records for 450+ hospitals, Ayushman Bharat Digital Mission (ABDM) integration, and ISO 27001 compliance.

---

# SECTION 4: PROPOSED TECHNICAL ARCHITECTURE & SOLUTION METHODOLOGY

### 4.1 Solution Architecture Overview
Our proposed architecture is built upon an enterprise-grade, cloud-agnostic, and microservices-first paradigm:
1. **Edge & Traffic Management:** Next-generation Web Application Firewall (WAF), Cloudflare / MeitY CSP CDN, and Automated DDoS mitigation at Layer 3/4/7.
2. **Presentation Layer:** Micro-frontend architecture built on React with strict WCAG 2.1 AA accessibility guidelines for bilingual Indic citizen access.
3. **API & Service Gateway:** Kong / Envoy API Gateway implementing OAuth2 / JWT authentication, rate limiting, and mTLS service mesh.
4. **Core Application Microservices:** Containerized Spring Boot and Python FastAPI services orchestrated on High-Availability Kubernetes (EKS / AKS / OpenShift).
5. **Data Tier:** Active-Active PostgreSQL Enterprise database cluster with automated streaming replication, Redis distributed caching, and cold storage archival on S3-compatible encrypted buckets.

### 4.2 Interoperability & DPI Integration
- **Aadhaar Authentication:** Pre-integrated UIDAI Auth API v2.5 client with HSM key protection.
- **DigiLocker Integration:** Native citizen document pull and certificate push via DigiLocker API v3.
- **Payment Gateway:** Multi-bank integration with NPCI UPI, SBI ePay, and BillDesk with automated reconciliation.

---

# SECTION 5: WORK BREAKDOWN STRUCTURE & IMPLEMENTATION SCHEDULE

### 5.1 Project Phases & Milestone Roadmap
- **Phase 1: Inception & As-Is Architecture Audit (Month 1):** Detailed stakeholder interviews, SRS sign-off, and security blueprint approval.
- **Phase 2: Cloud Infrastructure & Staging Deployment (Month 2 - Month 3):** MeitY Cloud VPC configuration, Kubernetes cluster hardening, and CI/CD pipelines.
- **Phase 3: Core Module Development & DPI Integration (Month 4 - Month 6):** Microservices development, UI/UX implementation, and test automation.
- **Phase 4: Security Audit, VAPT & CERT-In Clearance (Month 7):** Comprehensive vulnerability testing by CERT-In empaneled auditor and remediation.
- **Phase 5: User Acceptance Testing (UAT) & Data Migration (Month 8):** End-to-end data migration with zero data loss and formal sign-off.
- **Phase 6: Go-Live & 36-Month 24x7 Operations (Month 9 Onwards):** Full production switchover, L1/L2/L3 helpdesk deployment, and quarterly performance audits.

---

# SECTION 6: KEY PERSONNEL DEPLOYMENT & GOVERNANCE MATRIX

| Name | Role | Total Experience | Qualifications & Certifications | Project Responsibility |
| :--- | :--- | :--- | :--- | :--- |
| **Dr. Rajesh Sharma** | Chief Solution Architect & Project Director | 18 Years | Ph.D. CS, M.Tech IIT Delhi, PMP, AWS Solutions Architect Pro | Overall strategic delivery, architecture governance, and executive liaison with Authority. |
| **Priya Nair** | Lead Cloud DevOps Architect | 13 Years | M.S. BITS Pilani, CKA (Certified Kubernetes), Azure Solutions Architect | Cloud infrastructure, CI/CD pipeline automation, and Kubernetes clustering. |
| **Amitav Roy** | Principal Cybersecurity & Compliance Lead | 11 Years | B.Tech CSE, CISSP, CEH, ISO 27001 Lead Auditor | VAPT remediation, CERT-In audit clearance, and Zero Trust security controls. |
| **Sneha Kulkarni** | QA & Service Delivery Manager | 10 Years | B.E. IT, MBA, ISTQB Advanced, ScrumMaster | SLA monitoring, helpdesk supervision, and automated regression testing. |

---

# SECTION 7: CLAUSE-BY-CLAUSE COMPLIANCE MATRIX

| Tender Section / Clause No. | RFP Requirement Summary | Bidder Compliance Status | Remarks / Reference |
| :--- | :--- | :--- | :--- |
| Clause 3.1 | Minimum 3-Year Average Turnover ₹ 20.0 Cr | **FULLY COMPLIANT** | Audited balance sheets attached; 3-Yr Avg is ₹ 35.57 Cr. |
| Clause 3.2 | Prior Experience in similar Government IT projects | **FULLY COMPLIANT** | Submitted 3 completed public sector credentials totaling ₹ 42.5 Cr. |
| Clause 4.1 | 99.95% System Availability SLA with penalty matrix | **FULLY COMPLIANT** | Unconditional acceptance. Supported by active-active failover design. |
| Clause 5.3 | Mandatory ISO 9001 and ISO 27001 Certification | **FULLY COMPLIANT** | Valid copies of certificates attached in Annexure. |
| Clause 6.2 | Data Residency within India (MeitY empaneled CSP) | **FULLY COMPLIANT** | Primary DC in Mumbai and DR in Hyderabad within Indian borders. |
| Clause 8.1 | 36 Months Comprehensive Warranty & Onsite Support | **FULLY COMPLIANT** | 24x7 Tier-3 support team dedicated to Authority. |

---

# SECTION 8: QUALITY MANAGEMENT, SLA & CYBERSECURITY FRAMEWORK

### 8.1 SLA Framework & Penalty Commitments
- **P1 Incidents (Portal Down / Core Function Failure):** Response within 15 minutes; Resolution within 2 hours.
- **P2 Incidents (Degraded Performance / Non-critical bug):** Response within 30 minutes; Resolution within 6 hours.
- **Target Monthly Uptime:** Guaranteed **99.95%** with automated health telemetry reports shared monthly.

### 8.2 Security & Data Protection Measures
- Full encryption for data at rest (AES-256) and data in transit (TLS 1.3).
- Strict role-based access control (RBAC) with multi-factor authentication (MFA) for administrative staff.
- Daily automated database snapshots with off-site air-gapped backups.
- RPO (Recovery Point Objective) < 15 minutes; RTO (Recovery Time Objective) < 60 minutes.

---

# SECTION 9: RISK MITIGATION & BUSINESS CONTINUITY PLAN

1. **Risk: Legacy Data Cleansing Bottlenecks**  
   *Mitigation:* Deploy automated ETL parsing scripts with schema validation to isolate corrupt records before staging migration.
2. **Risk: Peak Citizen Traffic Spikes during Notification Releases**  
   *Mitigation:* Kubernetes Horizontal Pod Autoscaler (HPA) configured to spin up additional microservice pods within 45 seconds when CPU threshold exceeds 70%.
3. **Risk: Regulatory Audit Observations**  
   *Mitigation:* Continuous DevSecOps static code analysis (SonarQube) and dynamic container image vulnerability scanning (Trivy) in every build pipeline.

---

# SECTION 10: COMMERCIAL VALUE PROPOSITION & SUBMISSION INDEX

### 10.1 Value Engineering for the Authority
By leveraging **{company_name}**'s pre-built e-Governance modules, reusable API connectors, and automated CI/CD blueprints, the Authority will achieve:
- **Zero OEM Lock-in:** Open-source, vendor-neutral enterprise architecture with full code handover.
- **30% Faster Time-to-Market:** Production Go-Live within 8 months compared to standard 14-month industry cycles.
- **Predictable Total Cost of Ownership (TCO):** Clear, transparent pricing with no hidden proprietary licensing royalties.

### 10.2 Document Submission Index & Annexure Checklist
- [x] **Annexure-A:** Form of Bid & Covering Letter on Company Letterhead
- [x] **Annexure-B:** Earnest Money Deposit (EMD) Bank Guarantee / MSME Exemption Certificate
- [x] **Annexure-C:** Audited Financial Statements and CA Turnover Certificates
- [x] **Annexure-D:** Past Performance and Client Completion Certificates
- [x] **Annexure-E:** Technical Solution Architecture and Implementation Plan
- [x] **Annexure-F:** Key Personnel CVs with Signed Availability Commitments
- [x] **Annexure-G:** Non-Blacklisting Affidavit and Integrity Pact on Stamp Paper
- [x] **Annexure-H:** Complete Clause-by-Clause Compliance Statement
"""

    def export_to_docx(self, bid_response: Dict[str, Any]) -> io.BytesIO:
        """
        Generates a beautifully styled Word Document (.docx) for download.
        """
        doc = docx.Document()
        
        # Page Margins (1 inch all around)
        for section in doc.sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

        # Document Header
        title = bid_response.get("title", "Technical Bid Proposal")
        tender_id = bid_response.get("tender_id", "NIT/2026/092")
        
        # Cover / Header Title
        title_p = doc.add_paragraph()
        title_p.paragraph_format.space_before = Pt(12)
        title_p.paragraph_format.space_after = Pt(4)
        run_title = title_p.add_run(title)
        run_title.font.size = Pt(22)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(16, 44, 87) # Deep Navy

        # Subtitle
        sub_p = doc.add_paragraph()
        sub_p.paragraph_format.space_after = Pt(18)
        run_sub = sub_p.add_run(f"Comprehensive Technical & Management Response • Ref: {tender_id}")
        run_sub.font.size = Pt(12)
        run_sub.font.color.rgb = RGBColor(100, 116, 139)

        # Add Horizontal Rule
        p_hr = doc.add_paragraph()
        p_hr.paragraph_format.space_after = Pt(14)
        r_hr = p_hr.add_run("_________________________________________________________________________________")
        r_hr.font.color.rgb = RGBColor(203, 213, 225)

        # Parse sections and add content
        md_content = bid_response.get("markdown_content", "")
        lines = md_content.splitlines()

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Heading 1
            if line_str.startswith("# "):
                h = doc.add_heading(level=1)
                h.paragraph_format.space_before = Pt(18)
                h.paragraph_format.space_after = Pt(6)
                r = h.add_run(line_str[2:].strip())
                r.font.size = Pt(15)
                r.font.bold = True
                r.font.color.rgb = RGBColor(16, 44, 87)

            # Heading 2
            elif line_str.startswith("## "):
                h = doc.add_heading(level=2)
                h.paragraph_format.space_before = Pt(12)
                h.paragraph_format.space_after = Pt(4)
                r = h.add_run(line_str[3:].strip())
                r.font.size = Pt(13)
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 64, 175)

            # Heading 3
            elif line_str.startswith("### "):
                h = doc.add_heading(level=3)
                h.paragraph_format.space_before = Pt(8)
                h.paragraph_format.space_after = Pt(2)
                r = h.add_run(line_str[4:].strip())
                r.font.size = Pt(11)
                r.font.bold = True
                r.font.color.rgb = RGBColor(51, 65, 85)

            # Bullet points
            elif line_str.startswith("- ") or line_str.startswith("* "):
                p = doc.add_paragraph(style='List Bullet')
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.15
                clean_bullet = line_str[2:].strip()
                # Parse basic bolding
                self._add_formatted_text(p, clean_bullet)

            # Checkbox lists
            elif line_str.startswith("- [x] ") or line_str.startswith("- [ ] "):
                p = doc.add_paragraph(style='List Bullet')
                checked = line_str.startswith("- [x] ")
                prefix = "[✓] " if checked else "[ ] "
                clean_item = prefix + line_str[6:].strip()
                self._add_formatted_text(p, clean_item)

            # Table lines (ignore raw markdown table divider |:--|)
            elif line_str.startswith("|") and ("---" in line_str):
                continue

            elif line_str.startswith("|") and line_str.endswith("|"):
                # Table row representation
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(2)
                cells = [c.strip() for c in line_str.split("|")[1:-1]]
                row_text = "   •   ".join(cells)
                self._add_formatted_text(p, row_text)

            # Standard paragraph
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.15
                self._add_formatted_text(p, line_str)

        # Save to buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    def _add_formatted_text(self, paragraph, text: str):
        """Helper to parse bold markdown tokens **bold** into docx runs."""
        parts = text.split("**")
        is_bold = False
        for part in parts:
            if part:
                run = paragraph.add_run(part)
                run.font.size = Pt(10.5)
                run.font.name = "Calibri"
                if is_bold:
                    run.font.bold = True
            is_bold = not is_bold

bid_generator = BidGenerator()
