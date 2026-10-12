# TenderAI - Autonomous Tender Bidding Agent (Powered by Sarvam AI)

An intelligent, enterprise-grade AI bidding agent prototype built with **Sarvam AI** for analyzing government & commercial tender RFPs/NITs, evaluating eligibility criteria against company credentials, and generating publication-ready bid responses grounded in corporate past performance.

---

## 🌟 Key Capabilities

### 1. 📋 Tender Document Ingestion & Deep Analysis
- **Universal File Parser:** Ingests tender documents in **PDF**, **Microsoft Word (.docx)**, and **Plain Text/Markdown (.txt)**.
- **Sarvam AI Extraction Engine (`sarvam-105b`):**
  - **Tender Basics:** NIT / Tender Reference ID, Issuing Authority / Ministry, E-Procurement Portal (GeM, CPPP, State), Estimated Contract Value, EMD / Bid Security, Tender Fee, Performance Bank Guarantee (PBG %).
  - **Deadlines & Timelines:** Bid submission deadline, Pre-bid meeting date/venue, Query submission deadline, Technical & Financial opening dates, Bid validity period with automated days-remaining countdown and urgency badges.
  - **Pre-Qualification Criteria:** Financial eligibility (3-year average turnover, net worth, solvency certificate), Technical qualifications (minimum experience years, single/multiple project threshold values), Quality & Security certifications (ISO 9001, ISO 27001, CMMI Level 3), and Statutory declarations.
  - **Scope of Work & Deliverables:** Architectural requirements, cloud migration specifications, SLA commitments (99.95% uptime), and STQC / CERT-In security audits.
  - **Submission Checklist:** Mandatory Annexures, Affidavits, Integrity Pact, EMD receipt, and Technical proposal forms.
  - **Evaluation Model:** QCBS (Quality and Cost Based Selection e.g. 70:30) vs Lowest Bidder (L1) scoring rules.

### 2. ⚖️ Automated Eligibility & Go/No-Go Decision Engine
- **4-Pillar Quantitative Fit Analysis:**
  - **Financial Match:** Compares tender turnover against company turnover history (FY21-22, FY22-23, FY23-24) and bank solvency.
  - **Technical Track Record Match:** Checks past completed project values against tender single/multiple project criteria.
  - **Certifications Compliance:** Matches ISO 9001, ISO 27001, CMMI Level 3/5, SOC 2, and MeitY Cloud MSP credentials.
  - **Governance & Team Match:** Evaluates qualifications of designated Project Director, Cloud Architect, Cybersecurity Lead, and QA Manager.
- **Quantitative Fit Score (0–100%)** with visual gauge and clear strategic verdict: `STRONG GO`, `GO WITH CAUTION`, or `NO-GO`.
- **Strategic Win Themes & Risk Mitigation Matrix** identifying key competitive advantages.

### 3. ✍️ 10-Section Technical Bid Proposal Generator
- Synthesizes an RFP-compliant, procurement-grade proposal package:
  1. **Section 1:** Formal Covering Letter & Tender Declaration (with corporate seal & tender ref)
  2. **Section 2:** Executive Summary & Assignment Understanding
  3. **Section 3:** Bidder Profile & Relevant Public Sector Track Record (citing past winning proposals with client names and values)
  4. **Section 4:** Proposed Technical Architecture & Solution Methodology (Cloud VPC, Kubernetes, High-Availability DB, Microservices, DPI: Aadhaar, DigiLocker, Payment Gateway)
  5. **Section 5:** Work Breakdown Structure (WBS), Milestones & Gantt Roadmap
  6. **Section 6:** Key Personnel Deployment & Governance Matrix
  7. **Section 7:** Clause-by-Clause Compliance Matrix (Unconditional acceptance with nil deviations)
  8. **Section 8:** Quality Management, SLA (99.95% uptime) & Cyber Security Framework
  9. **Section 9:** Risk Mitigation & Business Continuity Plan (RPO < 15 min, RTO < 1 hr)
  10. **Section 10:** Commercial Value Proposition & Mandatory Submission Index
- **Exports:** Download as Microsoft Word (`.docx`), Markdown (`.md`), or print-ready PDF view.

### 4. 🌐 Sarvam AI Indic & Audio Studio
- **Neural Indic Translation (`mayura:v1`):** Translates tender requirements and bid executive summaries into 10 Indian languages: **Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada, Malayalam, Odia, and Punjabi**.
- **Executive Audio Briefing (`bulbul:v2`):** Generates voice briefings of critical deadlines and compliance requirements using Indian voices (*Manisha* or *Rohit*).

### 5. 🏢 Dynamic Company Knowledge Base
- Fully persistent corporate repository for company financials, ISO/CMMI certificates, library of past winning bids, and CVs of key personnel.

---

## 🛠️ Architecture Overview

```
tender-bidding-agent/
├── app/
│   ├── config.py             # Environment settings & persistent API key management
│   ├── sarvam_client.py      # Sarvam AI Chat, Mayura Translation, and Bulbul TTS client
│   ├── document_parser.py    # Universal extractor for PDF, DOCX, and TXT files
│   ├── tender_analyzer.py    # Structured tender RFP extractor and deadline calculator
│   ├── eligibility_matcher.py# 4-Pillar fit scoring and Go/No-Go decision engine
│   ├── bid_generator.py      # 10-section bid proposal writer and DOCX exporter
│   ├── knowledge_base.py     # Company profile, past proposals & team CV storage
│   ├── main.py               # FastAPI REST API & routes
│   ├── static/
│   │   ├── css/styles.css    # Styling, prose overrides, print CSS
│   │   └── js/app.js         # Reactive UI, AJAX workflows, audio playback
│   ├── templates/
│   │   └── index.html        # Modern executive dashboard (Tailwind CSS)
│   └── data/
│       ├── company_profile.json
│       ├── past_proposals.json
│       ├── team_profiles.json
│       └── sample_tenders/
│           ├── tender_egov_cloud_portal.txt
│           └── tender_smart_city_iot.txt
├── run.bat                   # 1-Click Windows Batch Launcher
├── run.ps1                   # PowerShell Launcher
├── requirements.txt          # Python dependencies
└── .env.example              # Sample environment configuration
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (Virtual environment pre-configured in `sarvam-starter\.venv`)

### 2. Configure Your Sarvam API Key
You can configure your Sarvam API Key in any of two ways:
1. **Directly in the Web UI:** Click the settings gear in the top-right header and paste your key.
2. **Via `.env` file:** Copy `.env.example` to `.env` and enter your key:
   ```env
   SARVAM_API_KEY=your_sarvam_api_key_here
   SARVAM_CHAT_MODEL=sarvam-105b
   ```
*(Note: If no API key is entered, the prototype operates with its built-in domain reasoning engine so you can test all features immediately!)*

### 3. Launching the Prototype

**Option A: 1-Click Windows Launcher**
Double click `run.bat` or run:
```cmd
run.bat
```

**Option B: PowerShell**
```powershell
.\run.ps1
```

**Option C: Direct Python / Uvicorn**
```bash
.\sarvam-starter\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once started, open your web browser at:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 💡 Quick Walkthrough

1. **Step 1 - Select or Upload Tender:** In the **Tender Analyzer** tab, click **Load** on the pre-loaded *"Tender Egov Cloud Portal"* sample (or upload your own PDF/DOCX file).
2. **Step 2 - Analyze:** Click **"Analyze with Sarvam AI"**. The system extracts metadata, deadlines, countdowns, eligibility criteria, scope, and mandatory checklist.
3. **Step 3 - Evaluate Eligibility:** Switch to **"Eligibility & Go/No-Go"** to review the 94% fit score, traffic light status on Financial & Experience criteria, and strategic recommendation.
4. **Step 4 - Generate Bid:** In **"Bid Response Studio"**, select tone and click **"Generate Bid Proposal with Sarvam AI"**. View the 10-section proposal and click **"Download Word (.docx)"**.
5. **Step 5 - Indic Translation & Audio:** Go to **"Indic & Audio Studio"** to translate the RFP brief into Hindi/Tamil/Telugu, and listen to the voice audio summary.
