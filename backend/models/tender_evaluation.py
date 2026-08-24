import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from backend.config import TENDER_RFP_FILE, VENDOR_BIDS_FILE


class TenderEvaluationEngine:
    """
    AI-based Technical and Commercial Evaluation Engine for SAIL Bokaro.
    Supports automated multi-clause auditing, CST generation, and dynamic bid simulation.
    """
    
    SAMPLE_PACKAGES = {
        "PKG-01": {
            "name": "Hot Strip Mill Descaling Hydraulic Unit (₹4.85 Cr)",
            "tender_id": "SAIL/BSL/MM/PUR/2026/089",
            "title": "Design, Manufacture, Supply & Commissioning of High-Pressure Descaling Hydraulic Power Pack for HSM-2",
            "budget": 48500000,
            "issuing_authority": "Materials Management (Procurement Division) — Bokaro Steel Plant",
            "emd": 970000,
        },
        "PKG-02": {
            "name": "Blast Furnace Taphole & Trough Refractories (₹2.40 Cr)",
            "tender_id": "SAIL/BSL/BF/REF/2026/042",
            "title": "Supply of High-Grade Anhydrous Taphole Clay & SiC Trough Castables for BF-4 & BF-5",
            "budget": 24000000,
            "issuing_authority": "Blast Furnace Maintenance & MM — Bokaro Steel Plant",
            "emd": 480000,
        },
        "PKG-03": {
            "name": "SMS Continuous Casting Servo Actuators (₹3.60 Cr)",
            "tender_id": "SAIL/BSL/SMS/ELE/2026/115",
            "title": "Turnkey Supply of High-Precision Hydraulic Servo Actuators & PLC Interface for Caster-2",
            "budget": 36000000,
            "issuing_authority": "Steel Melting Shop & C&IT — Bokaro Steel Plant",
            "emd": 720000,
        },
    }

    def __init__(self):
        self.rfp_file = TENDER_RFP_FILE
        self.bids_file = VENDOR_BIDS_FILE
        self.rfp_data = None
        self.vendor_bids = None
        self.load_data()

    def load_data(self):
        if os.path.exists(self.rfp_file) and os.path.exists(self.bids_file):
            with open(self.rfp_file, "r", encoding="utf-8") as f:
                self.rfp_data = json.load(f)
            with open(self.bids_file, "r", encoding="utf-8") as f:
                self.vendor_bids = json.load(f)
        else:
            from backend.data_generator import generate_tender_data
            generate_tender_data()
            with open(self.rfp_file, "r", encoding="utf-8") as f:
                self.rfp_data = json.load(f)
            with open(self.bids_file, "r", encoding="utf-8") as f:
                self.vendor_bids = json.load(f)

    def get_available_packages(self) -> List[Dict[str, Any]]:
        return [{"key": k, "name": v["name"], "id": v["tender_id"]} for k, v in self.SAMPLE_PACKAGES.items()]

    def evaluate_tender(
        self,
        package_key: str = "PKG-01",
        price_modifiers: Optional[Dict[str, float]] = None,
        resolve_deviations: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        """
        Executes multi-vendor technical scoring, commercial term normalization,
        clause deviation detection, and generates Comparative Statement of Tenders (CST).
        Supports live price modifiers and deviation resolution for What-If negotiation.
        """
        self.load_data()
        rfp = dict(self.rfp_data)
        bids = [dict(b) for b in self.vendor_bids]
        
        # Apply package metadata if different package selected
        if package_key in self.SAMPLE_PACKAGES:
            pkg = self.SAMPLE_PACKAGES[package_key]
            rfp["tender_id"] = pkg["tender_id"]
            rfp["title"] = pkg["title"]
            rfp["estimated_budget_inr"] = pkg["budget"]
            rfp["issuing_authority"] = pkg["issuing_authority"]
            rfp["emd_amount_inr"] = pkg["emd"]

        budget = rfp["estimated_budget_inr"]
        price_modifiers = price_modifiers or {}
        resolve_deviations = resolve_deviations or {}

        evaluated_vendors = []

        for bid in bids:
            vid = bid["vendor_id"]
            vname = bid["vendor_name"]
            
            # Base quoted price with dynamic live modifier
            base_quote = bid["quoted_price_inr"]
            if package_key != "PKG-01":
                # Scale base quotes proportional to new package budget
                base_quote = int((bid["quoted_price_inr"] / 48500000) * budget)
            
            modifier = price_modifiers.get(vid, 1.0)
            quoted_price = int(base_quote * modifier)

            # 1. Technical Evaluation & Scoring
            tech_responses = bid.get("technical_responses") or bid.get("technical_specs_offered", [])
            total_specs = len(tech_responses)
            compliant_count = 0
            deviations = []
            highlights = []

            is_waived = resolve_deviations.get(vid, False)

            for idx, resp in enumerate(tech_responses):
                status = resp["compliance"]
                is_compliant = ("Compliant" in status or "Superior" in status) and ("Non-Compliant" not in status) and ("Deviation" not in status)
                
                if is_waived:
                    is_compliant = True
                    status = "Compliant (Clarified during TNC)"

                if is_compliant:
                    compliant_count += 1
                    if "Superior" in status:
                        highlights.append(f"{resp['parameter']}: {resp['offered_value']} (Superior to RFP)")
                else:
                    deviations.append({
                        "spec_id": resp.get("spec_id", f"SPEC-{idx+1:02d}"),
                        "parameter": resp["parameter"],
                        "offered_value": resp["offered_value"],
                        "status": status,
                        "remarks": resp.get("remarks", "Technical variance observed"),
                        "severity": "CRITICAL" if ("Non-Compliant" in status or "Deviation" in status) else "MODERATE",
                    })

            tech_score = round((compliant_count / max(1, total_specs)) * 100, 1)
            is_technically_qualified = len([d for d in deviations if d["severity"] == "CRITICAL"]) == 0

            # 2. Commercial Terms Evaluation & Financial Loading
            comm = bid.get("commercial_responses", {})
            comm_deviations = []
            commercial_loading_inr = 0
            is_commercially_disqualified = False

            # Check delivery schedule
            deliv = comm.get("delivery_schedule", "")
            if "22 Weeks" in deliv and not is_waived:
                loading = int(quoted_price * 0.03)
                commercial_loading_inr += loading
                comm_deviations.append({
                    "clause": "Delivery Schedule",
                    "bid_value": deliv,
                    "required_value": rfp["commercial_terms"].get("delivery_schedule", "16 Weeks"),
                    "impact": f"Loaded with +INR {loading:,} for delayed commissioning risk.",
                })

            # Check advance payment
            pay = comm.get("payment_terms", "")
            if "advance" in pay.lower() and not is_waived:
                is_commercially_disqualified = True
                comm_deviations.append({
                    "clause": "Payment Terms (Prohibited Advance)",
                    "bid_value": pay,
                    "required_value": rfp["commercial_terms"].get("payment_terms", ""),
                    "impact": "CRITICAL: Advance payment violates SAIL MM Manual Clause 14.2 without BG approval.",
                })

            # Check warranty
            warr = comm.get("warranty_period", "")
            if "18 Months" in warr and not is_waived:
                loading = int(quoted_price * 0.02)
                commercial_loading_inr += loading
                comm_deviations.append({
                    "clause": "Warranty Period",
                    "bid_value": warr,
                    "required_value": rfp["commercial_terms"].get("warranty_period", "24 Months"),
                    "impact": f"Loaded with +INR {loading:,} for warranty shortfall.",
                })

            evaluated_price = quoted_price + commercial_loading_inr
            price_variance_vs_budget = round(((quoted_price - budget) / budget) * 100, 1)

            # Final Qualification Status
            if not is_technically_qualified:
                overall_status = "REJECTED (Technical Deviations)"
                qualification_badge = "rejected"
            elif is_commercially_disqualified:
                overall_status = "DISQUALIFIED (Commercial Policy Violation)"
                qualification_badge = "disqualified"
            else:
                overall_status = "QUALIFIED"
                qualification_badge = "qualified"

            evaluated_vendors.append({
                "vendor_id": vid,
                "vendor_name": vname,
                "vendor_origin": bid["vendor_origin"],
                "quoted_price_inr": quoted_price,
                "commercial_loading_inr": commercial_loading_inr,
                "evaluated_landing_price_inr": evaluated_price,
                "variance_vs_budget_pct": price_variance_vs_budget,
                "technical_score_pct": tech_score,
                "is_technically_qualified": is_technically_qualified,
                "is_commercially_qualified": not is_commercially_disqualified,
                "overall_status": overall_status,
                "qualification_badge": qualification_badge,
                "technical_deviations": deviations,
                "commercial_deviations": comm_deviations,
                "technical_highlights": highlights,
                "full_technical_responses": tech_responses,
                "full_commercial_responses": comm,
            })

        # Rank valid qualified vendors by Evaluated Price (L1, L2, etc.)
        qualified_bids = [v for v in evaluated_vendors if v["overall_status"] == "QUALIFIED"]
        qualified_bids = sorted(qualified_bids, key=lambda x: x["evaluated_landing_price_inr"])

        for idx, q_bid in enumerate(qualified_bids):
            q_bid["rank"] = f"L{idx + 1}"

        for v in evaluated_vendors:
            if v["overall_status"] != "QUALIFIED":
                v["rank"] = "Disqualified"

        # Executive Purchase Committee Recommendation
        if qualified_bids:
            l1_vendor = qualified_bids[0]
            recommendation = {
                "recommended_vendor": l1_vendor["vendor_name"],
                "recommended_rank": l1_vendor["rank"],
                "order_value_inr": l1_vendor["quoted_price_inr"],
                "budget_utilization_pct": round((l1_vendor["quoted_price_inr"] / budget) * 100, 1),
                "savings_against_budget_inr": max(0, budget - l1_vendor["quoted_price_inr"]),
                "justification": f"Vendor {l1_vendor['vendor_name']} is the lowest evaluated qualified bidder ({l1_vendor['rank']}) with {l1_vendor['technical_score_pct']}% technical score, conforming commercial terms, and evaluated landed price of ₹{l1_vendor['evaluated_landing_price_inr']:,}.",
                "action_items": [
                    "Issue Letter of Intent (LOI) to L1 bidder.",
                    "Verify 10% Performance Bank Guarantee (PBG) with SBI / Nationalized Bank prior to signing.",
                    "Schedule Level-2 SCADA interface technical alignment meeting with C&IT, BSL.",
                ],
            }
        else:
            recommendation = {
                "recommended_vendor": "None",
                "recommended_rank": "N/A",
                "justification": "No vendor passed both technical and commercial compliance without critical deviations. Retender recommended.",
                "action_items": ["Initiate Retender through SAIL e-Procurement Portal."],
            }

        return {
            "tender_rfp_summary": {
                "tender_id": rfp["tender_id"],
                "title": rfp["title"],
                "issuing_authority": rfp["issuing_authority"],
                "estimated_budget_inr": budget,
                "emd_amount_inr": rfp["emd_amount_inr"],
                "total_technical_specs_count": len(rfp.get("technical_specifications", [])),
                "mandatory_technical_specs": rfp.get("technical_specifications", []),
                "standard_commercial_terms": rfp.get("commercial_terms", {}),
            },
            "comparative_statement_of_tenders": evaluated_vendors,
            "executive_purchase_recommendation": recommendation,
        }


if __name__ == "__main__":
    engine = TenderEvaluationEngine()
    res = engine.evaluate_tender()
    print("Default L1:", res["executive_purchase_recommendation"]["recommended_vendor"])
    
    # Simulate Apex Engineering price cut and deviation clearance
    res2 = engine.evaluate_tender(price_modifiers={"VEND-IND-0219": 0.85}, resolve_deviations={"VEND-IND-0219": True})
    print("Simulated L1:", res2["executive_purchase_recommendation"]["recommended_vendor"])
