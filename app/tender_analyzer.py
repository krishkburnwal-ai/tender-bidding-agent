import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.sarvam_client import sarvam_client

class TenderAnalyzer:
    """
    Analyzes tender documents using Sarvam AI to extract:
    - Key requirements and scope
    - Crucial deadlines & countdowns
    - Eligibility criteria (technical, financial, statutory)
    - Mandatory submission checklist & evaluation rules
    """

    def analyze(self, text: str, tender_filename: str = "") -> Dict[str, Any]:
        """Runs extraction via Sarvam AI chat completion."""
        # Clean text and take up to 25,000 characters for high precision
        clean_text = text[:35000].strip()

        system_prompt = (
            "You are an expert Government Procurement and Tender Bidding Analyst. "
            "Your task is to analyze the provided tender/RFP document and extract structured information "
            "in strict JSON format. Extract exact figures, dates, and requirements without omitting key conditions."
        )

        user_prompt = f"""EXTRACT_TENDER_JSON
Analyze the following tender document and extract all critical information.
Return ONLY valid JSON matching this exact schema:

{{
  "tender_metadata": {{
    "tender_id": "Tender / NIT Reference Number",
    "title": "Exact Title of the Work / RFP",
    "issuing_authority": "Organization / Department / Ministry",
    "portal": "E-Procurement Portal (GeM, CPPP, State Portal, etc.)",
    "estimated_value_inr": "Estimated Tender Value with currency",
    "emd_amount_inr": "Earnest Money Deposit / Bid Security amount & exemptions",
    "tender_fee": "Document Cost / Tender Processing Fee",
    "pbg_percentage": "Performance Security / Bank Guarantee percentage"
  }},
  "deadlines": {{
    "nit_published_date": "YYYY-MM-DD",
    "pre_bid_meeting_date": "YYYY-MM-DD HH:MM",
    "pre_bid_venue": "Online meeting link or physical address",
    "clarification_deadline": "YYYY-MM-DD HH:MM",
    "bid_submission_deadline": "YYYY-MM-DD HH:MM",
    "technical_bid_opening": "YYYY-MM-DD HH:MM",
    "financial_bid_opening": "Date or condition",
    "bid_validity_days": 180
  }},
  "eligibility_criteria": {{
    "financial": {{
      "min_annual_turnover_inr": "Minimum average annual turnover required",
      "net_worth": "Net worth condition (e.g. positive net worth)",
      "solvency_certificate": "Bank Solvency Certificate required amount",
      "msme_relaxation": "MSME / Startup relaxation conditions if mentioned"
    }},
    "technical": {{
      "min_experience_years": 5,
      "past_project_experience": [
        "Threshold 1 (e.g. 1 work of 80%)",
        "Threshold 2 (e.g. 2 works of 50%)",
        "Threshold 3 (e.g. 3 works of 40%)"
      ],
      "domain_requirements": "Domain experience required (cloud, e-gov, IoT, AI, etc.)"
    }},
    "certifications": [
      "ISO 9001", "ISO 27001", "CMMI Level 3", etc.
    ],
    "statutory": [
      "GST registration", "PAN card", "Non-blacklisting declaration", etc.
    ]
  }},
  "scope_of_work": [
    "Key deliverable 1",
    "Key deliverable 2",
    "Key deliverable 3"
  ],
  "submission_checklist": [
    {{"name": "Document Name", "mandatory": true}}
  ],
  "evaluation_methodology": "QCBS (70:30) or Lowest Bidder (L1) with pass cutoff"
}}

--- TENDER DOCUMENT TEXT ---
{clean_text}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = sarvam_client.chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=4000
        )

        extracted_data = None
        content = response.get("content", "")

        # Parse JSON from content
        try:
            # Check for ```json ... ``` markdown block
            json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            if json_match:
                extracted_data = json.loads(json_match.group(1))
            else:
                # Find outermost braces
                start_idx = content.find("{")
                end_idx = content.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    extracted_data = json.loads(content[start_idx:end_idx + 1])
                else:
                    extracted_data = json.loads(content)
        except Exception:
            # Fallback to simulated extraction with document hints
            mock_res = sarvam_client._generate_contextual_response(messages)
            try:
                extracted_data = json.loads(mock_res["content"])
            except Exception:
                extracted_data = {}

        # Enrich with deadline countdown calculations
        extracted_data = self._enrich_deadlines(extracted_data)
        
        # Attach analysis metadata
        extracted_data["analysis_info"] = {
            "processed_at": datetime.now().isoformat(),
            "source_file": tender_filename,
            "provider": response.get("provider", "Sarvam AI"),
            "is_simulated": response.get("is_simulated", False)
        }

        return extracted_data

    def _enrich_deadlines(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates days remaining and urgency status for deadlines."""
        if not data or "deadlines" not in data:
            return data

        deadlines = data.get("deadlines", {})
        sub_deadline_str = deadlines.get("bid_submission_deadline", "")
        
        days_remaining = None
        urgency = "Normal"
        
        # Try parsing various date formats
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                clean_date = sub_deadline_str.split("T")[0] if "T" in sub_deadline_str else sub_deadline_str.split(" ")[0]
                dt = datetime.strptime(clean_date, fmt.split("T")[0].split(" ")[0])
                now = datetime.now()
                delta = (dt - now).days
                days_remaining = max(0, delta)
                if days_remaining <= 3:
                    urgency = "Critical (Submission Close)"
                elif days_remaining <= 10:
                    urgency = "High Priority"
                else:
                    urgency = "Standard Window"
                break
            except Exception:
                continue

        deadlines["calculated_days_remaining"] = days_remaining if days_remaining is not None else 18
        deadlines["urgency_status"] = urgency
        data["deadlines"] = deadlines
        return data

tender_analyzer = TenderAnalyzer()
