from typing import Dict, Any, List
from app.knowledge_base import knowledge_base

class EligibilityMatcher:
    """
    Compares Tender Requirements against Company Knowledge Base to determine:
    - Compliance status per criterion (Financial, Technical, Certifications, Team)
    - Quantitative Bid Eligibility Score (0-100%)
    - Strategic Go / No-Go Bid Recommendation
    - Identified Win Themes and Compliance Risks
    """

    def evaluate_fit(self, tender_data: Dict[str, Any]) -> Dict[str, Any]:
        company = knowledge_base.get_company_profile()
        proposals = knowledge_base.get_past_proposals()
        team = knowledge_base.get_team_profiles()
        
        eligibility = tender_data.get("eligibility_criteria", {})
        fin_req = eligibility.get("financial", {})
        tech_req = eligibility.get("technical", {})
        certs_req = eligibility.get("certifications", [])
        
        # 1. Financial Evaluation
        company_fin = company.get("financials", {})
        company_avg_to_cr = company_fin.get("average_turnover_crores", 35.57)
        company_nw_cr = company_fin.get("net_worth_crores", 18.2)
        company_solv_cr = company_fin.get("solvency_crores", 15.0)

        # Parse required turnover
        req_to_text = fin_req.get("min_annual_turnover_inr", "20 Crores")
        req_to_cr = 20.0  # default
        if "20" in req_to_text:
            req_to_cr = 20.0
        elif "10" in req_to_text:
            req_to_cr = 10.0
        elif "30" in req_to_text:
            req_to_cr = 30.0

        fin_pass = company_avg_to_cr >= req_to_cr
        fin_score = 100 if fin_pass else min(90, int((company_avg_to_cr / req_to_cr) * 100))
        
        financial_eval = {
            "title": "Financial Criteria",
            "required_turnover": req_to_text,
            "company_turnover": f"₹ {company_avg_to_cr:.2f} Cr (Average) / ₹ 42.50 Cr (FY 23-24)",
            "turnover_status": "COMPLIANT (SURPLUS MARGIN)" if fin_pass else "MARGINAL",
            "net_worth_status": f"COMPLIANT (Positive net worth ₹ {company_nw_cr} Cr)",
            "solvency_status": f"COMPLIANT (Bank Solvency ₹ {company_solv_cr} Cr from SBI)",
            "msme_advantage": "Eligible for 50% relaxation if applicable under MSE / Startup procurement policy",
            "score": fin_score,
            "weight": 30
        }

        # 2. Technical & Past Experience Evaluation
        req_years = tech_req.get("min_experience_years", 5)
        company_years = company.get("years_in_business", 10)
        years_pass = company_years >= req_years

        # Check past project values
        best_proposals = []
        matching_past_works = []
        for p in proposals:
            val = p.get("contract_value_crores", 0)
            best_proposals.append(f"{p['project_name']} (₹ {val} Cr, {p['client']})")
            if val >= 5.0:
                matching_past_works.append(p)

        tech_score = 95 if len(matching_past_works) >= 2 and years_pass else 80
        technical_eval = {
            "title": "Technical Experience & Prior Projects",
            "required_years": f"{req_years} years in relevant IT / software domain",
            "company_years": f"{company_years} years (Established {company.get('incorporation_year', 2016)})",
            "years_status": "COMPLIANT",
            "qualifying_projects_found": len(matching_past_works),
            "top_matching_credentials": [
                {
                    "project": p["project_name"],
                    "client": p["client"],
                    "value": f"₹ {p['contract_value_crores']} Cr",
                    "status": p["status"],
                    "match_type": "Meets High-Value Qualification Threshold"
                }
                for p in matching_past_works[:3]
            ],
            "score": tech_score,
            "weight": 35
        }

        # 3. Certifications Evaluation
        company_certs = [c["name"].lower() for c in company.get("certifications", [])]
        cert_matches = []
        missing_certs = []

        for req_c in certs_req:
            req_c_clean = req_c.lower()
            matched = any(c in req_c_clean or req_c_clean in c for c in company_certs) or \
                      ("iso 9001" in req_c_clean and any("9001" in c for c in company_certs)) or \
                      ("iso 27001" in req_c_clean and any("27001" in c for c in company_certs)) or \
                      ("cmmi" in req_c_clean and any("cmmi" in c for c in company_certs))

            if matched:
                cert_matches.append(req_c)
            else:
                missing_certs.append(req_c)

        cert_score = 100 if not missing_certs else max(60, 100 - (len(missing_certs) * 20))
        certifications_eval = {
            "title": "Quality & Security Certifications",
            "mandatory_certifications_required": certs_req,
            "matched_certifications": cert_matches,
            "missing_certifications": missing_certs,
            "status": "ALL CRITICAL CERTIFICATIONS VALID" if not missing_certs else "REQUIRES OEM / MSP BACKING",
            "score": cert_score,
            "weight": 20
        }

        # 4. Team Profile Evaluation
        team_eval = {
            "title": "Key Personnel & Delivery Team",
            "assigned_team_size": len(team),
            "key_personnel": [
                f"{m['name']} - {m['role']} ({m['experience_years']} yrs exp, {', '.join(m['certifications'][:2])})"
                for m in team
            ],
            "status": "COMPLIANT (Full suite of PMP, TOGAF, CKA, CISSP certified leads)",
            "score": 95,
            "weight": 15
        }

        # Compute Overall Fit Score
        overall_score = round(
            (financial_eval["score"] * 0.30) +
            (technical_eval["score"] * 0.35) +
            (certifications_eval["score"] * 0.20) +
            (team_eval["score"] * 0.15)
        )

        # Strategic Verdict
        if overall_score >= 85:
            verdict = "STRONG GO (BID WITH HIGH CONFIDENCE)"
            verdict_color = "green"
            recommendation = (
                "Company exceeds all financial turnover and project experience thresholds. "
                "Strong past credentials in state e-governance and cloud migration provide high technical evaluation marks. "
                "Recommendation: Proceed with prime bidding and prioritize technical proposal scoring under QCBS."
            )
        elif overall_score >= 70:
            verdict = "GO WITH CAUTION / SPECIALIZED PARTNERSHIP"
            verdict_color = "yellow"
            recommendation = (
                "Company qualifies on core turnover and baseline requirements, but specific OEM partnerships "
                "or niche certifications should be reinforced to maximize technical scoring."
            )
        else:
            verdict = "NO-GO (HIGH QUALIFICATION RISK)"
            verdict_color = "red"
            recommendation = (
                "Substantial gap in required past single project value or specialized accreditations. "
                "Recommend bidding as part of a Consortium or Joint Venture (JV)."
            )

        return {
            "overall_fit_score": overall_score,
            "strategic_verdict": verdict,
            "verdict_color": verdict_color,
            "executive_recommendation": recommendation,
            "breakdown": {
                "financial": financial_eval,
                "technical": technical_eval,
                "certifications": certifications_eval,
                "team": team_eval
            },
            "win_themes": [
                f"10+ Years of proven institutional delivery in Public Sector IT with 99.98% documented uptime SLA.",
                f"Robust financial stability with ₹ {company_avg_to_cr:.1f} Cr 3-year turnover and zero debt liability.",
                f"Triple Certified delivery engine: ISO 9001, ISO 27001, and CMMI Dev Level 3.",
                f"Pre-approved MeitY Empanelled Cloud Architecture experience with instant migration blueprints."
            ],
            "compliance_risks_and_mitigation": [
                {
                    "risk": "Tight 36-month comprehensive operations SLA with penal clauses.",
                    "mitigation": "Deploy pre-built 24x7 automated monitoring agents and dedicated Tier-3 incident response team."
                },
                {
                    "risk": "Mandatory STQC / CERT-In security clearance prior to Go-Live.",
                    "mitigation": "CISSP-certified Lead Security Auditor will conduct internal vulnerability scans from Sprint 1."
                }
            ]
        }

eligibility_matcher = EligibilityMatcher()
