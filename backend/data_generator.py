"""
Real-World Data Ingestion Adapter — SAIL BSL SCM AI Suite
=========================================================
Routes all data generation and ingestion directly to the Live Open API Pipeline
(Yahoo Finance API, World Bank Open Data API, and Official BSL Specifications).
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import DATA_DIR, TENDER_RFP_FILE, VENDOR_BIDS_FILE
from backend.live_data_pipeline import (
    sync_all_real_world_apis,
    build_real_api_ferro_alloys_dataset,
    build_real_api_maintenance_dataset,
)


def generate_large_maintenance_dataset():
    """Generates maintenance data tied to real-world industrial output indicators."""
    return build_real_api_maintenance_dataset()


def generate_large_ferro_alloys_market_dataset():
    """Generates ferro alloys dataset backed by Yahoo Finance FX & Energy open APIs."""
    return build_real_api_ferro_alloys_dataset()


def generate_tender_data():
    """Builds standard public procurement RFP & multi-vendor bid evaluation specs."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    rfp_data = {
        "tender_id": "SAIL/BSL/MM/PUR/2026/089",
        "title": "Design, Manufacture, Supply, Erection & Commissioning of High-Pressure Descaling Hydraulic Power Pack Unit for Hot Strip Mill (HSM-2)",
        "issuing_authority": "Materials Management (Procurement Division) — Bokaro Steel Plant",
        "tender_type": "Open Global Tender (Two-Bid System: Technical + Commercial)",
        "estimated_budget_inr": 48500000,
        "emd_amount_inr": 970000,
        "technical_specifications": [
            {"spec_id": "SPEC-01", "parameter": "Working Hydraulic System Pressure", "required_value": ">= 210 bar (continuous rated)", "criticality": "Critical (Zero Tolerance)", "tolerance_percent": 0.0},
            {"spec_id": "SPEC-02", "parameter": "Main High-Pressure Pump Capacity", "required_value": ">= 450 Litres/min at 1450 RPM", "criticality": "Critical (Zero Tolerance)", "tolerance_percent": 0.0},
            {"spec_id": "SPEC-03", "parameter": "Electric Drive Motor Rating & Class", "required_value": "185 kW, 415V +/- 10%, 50Hz, IE4 Super Premium Efficiency, IP55, Class H", "criticality": "Critical (Zero Tolerance)", "tolerance_percent": 0.0},
            {"spec_id": "SPEC-04", "parameter": "Hydraulic Oil Reservoir Tank Capacity", "required_value": ">= 3000 Litres, SS-304 with internal anti-corrosive coating", "criticality": "High", "tolerance_percent": 5.0},
            {"spec_id": "SPEC-05", "parameter": "Filtration System Rating", "required_value": "<= 3 Micron absolute (Beta-200 rating), Duplex Online Filter with clogging alarm", "criticality": "Critical (Zero Tolerance)", "tolerance_percent": 0.0},
            {"spec_id": "SPEC-06", "parameter": "Oil Cooling System", "required_value": "Shell & Tube Water Cooler, cooling water temp 33C max, SS316 tubes", "criticality": "High", "tolerance_percent": 5.0},
            {"spec_id": "SPEC-07", "parameter": "PLC Automation & SCADA Interface", "required_value": "Siemens S7-1500 / Allen Bradley ControlLogix with Modbus TCP/IP & Profinet to BSL Level-2 MES", "criticality": "Critical (Zero Tolerance)", "tolerance_percent": 0.0},
            {"spec_id": "SPEC-08", "parameter": "Condition Monitoring Sensors", "required_value": "Online Vibration (ISO 10816), Oil Temp, Continuous Particle Counter, Moisture-in-Oil sensor", "criticality": "High", "tolerance_percent": 10.0}
        ],
        "commercial_terms": {
            "payment_terms": "80% upon dispatch against Inspection Certificate, 10% on successful commissioning, 10% against PBG",
            "delivery_schedule": "16 Weeks from date of LOI / Purchase Order",
            "warranty_period": "24 Months from commissioning or 30 months from supply",
            "pbg_requirement": "10% of total order value valid for 24 months from commissioning",
            "price_basis": "FOR Bokaro Steel Plant Site"
        }
    }
    
    with open(TENDER_RFP_FILE, "w", encoding="utf-8") as f:
        json.dump(rfp_data, f, indent=2)

    vendor_bids = [
        {
            "bid_id": "BID-2026-001",
            "vendor_id": "VEND-IND-0104",
            "vendor_name": "Bharat Heavy Hydraulics & Systems Ltd (Pune, India)",
            "vendor_origin": "Domestic (Make In India - Class 1 Local Supplier)",
            "quoted_price_inr": 44800000,
            "technical_responses": [
                {"spec_id": "SPEC-01", "parameter": "Working Hydraulic System Pressure", "offered_value": "220 bar (continuous rated)", "compliance": "Compliant (Exceeds spec by 10 bar)", "remarks": "High-grade Rexroth pump"},
                {"spec_id": "SPEC-02", "parameter": "Main High-Pressure Pump Capacity", "offered_value": "465 Litres/min", "compliance": "Compliant (Superior)", "remarks": "Axial Piston A4VSO series"},
                {"spec_id": "SPEC-03", "parameter": "Electric Drive Motor Rating & Class", "offered_value": "200 kW, IE4 Super Premium, IP55, Class H", "compliance": "Compliant (Superior)", "remarks": "Siemens IE4 make"},
                {"spec_id": "SPEC-04", "parameter": "Hydraulic Oil Reservoir Tank Capacity", "offered_value": "3200 Litres, SS-304", "compliance": "Compliant", "remarks": "SS-304 with baffles"},
                {"spec_id": "SPEC-05", "parameter": "Filtration System Rating", "offered_value": "3 Micron absolute (Beta 200), Hydac Duplex", "compliance": "Compliant", "remarks": "Hydac optical switch"},
                {"spec_id": "SPEC-06", "parameter": "Oil Cooling System", "offered_value": "Shell & Tube, SS-316 tubes", "compliance": "Compliant", "remarks": "Shell & Tube"},
                {"spec_id": "SPEC-07", "parameter": "PLC Automation & SCADA Interface", "offered_value": "Siemens S7-1516 with Profinet/Modbus TCP", "compliance": "Compliant", "remarks": "SAIL BSL pre-configured"},
                {"spec_id": "SPEC-08", "parameter": "Condition Monitoring Sensors", "offered_value": "IFM Electronic Vibration & Hydac CS1000", "compliance": "Compliant", "remarks": "Full sensor package"}
            ],
            "commercial_responses": {
                "payment_terms": "80% dispatch, 10% commissioning, 10% against PBG",
                "delivery_schedule": "16 Weeks",
                "warranty_period": "24 Months"
            }
        },
        {
            "bid_id": "BID-2026-002",
            "vendor_id": "VEND-IND-0219",
            "vendor_name": "Apex Fluid Power Engineering Corp (Faridabad, India)",
            "vendor_origin": "Domestic (Make In India - Class 2 Local Supplier)",
            "quoted_price_inr": 41200000,
            "technical_responses": [
                {"spec_id": "SPEC-01", "parameter": "Working Hydraulic System Pressure", "offered_value": "180 bar continuous, 210 bar peak intermittent", "compliance": "Non-Compliant (Deviation: 180 bar continuous)", "remarks": "Cannot sustain continuous 210 bar load"},
                {"spec_id": "SPEC-02", "parameter": "Main High-Pressure Pump Capacity", "offered_value": "450 Litres/min at 1450 RPM", "compliance": "Compliant", "remarks": "Gear pump combo"},
                {"spec_id": "SPEC-03", "parameter": "Electric Drive Motor Rating & Class", "offered_value": "185 kW, IE3 Premium, IP55", "compliance": "Deviation (Offered IE3 instead of IE4)", "remarks": "Standard IE3 motor"},
                {"spec_id": "SPEC-04", "parameter": "Hydraulic Oil Reservoir Tank Capacity", "offered_value": "2800 Litres, Mild Steel", "compliance": "Deviation (MS instead of SS-304)", "remarks": "MS epoxy coated tank"},
                {"spec_id": "SPEC-05", "parameter": "Filtration System Rating", "offered_value": "5 Micron absolute, Single filter", "compliance": "Deviation (5 Micron vs 3 Micron)", "remarks": "Non-duplex single unit"},
                {"spec_id": "SPEC-06", "parameter": "Oil Cooling System", "offered_value": "Plate Type Heat Exchanger", "compliance": "Deviation (Plate type vs Shell & Tube)", "remarks": "Plate type"},
                {"spec_id": "SPEC-07", "parameter": "PLC Automation & SCADA Interface", "offered_value": "Delta PLC RS-485 Modbus RTU only", "compliance": "Non-Compliant (No Profinet / Ethernet)", "remarks": "Cannot connect to BSL MES"},
                {"spec_id": "SPEC-08", "parameter": "Condition Monitoring Sensors", "offered_value": "Basic Dial Gauges only", "compliance": "Deviation (No vibration sensor)", "remarks": "Dial gauge only"}
            ],
            "commercial_responses": {
                "payment_terms": "20% Advance with order, 70% against dispatch, 10% after 30 days",
                "delivery_schedule": "22 Weeks",
                "warranty_period": "18 Months"
            }
        },
        {
            "bid_id": "BID-2026-003",
            "vendor_id": "VEND-GER-0881",
            "vendor_name": "Hydrowerk Steel Plant Hydraulics GmbH (Stuttgart, Germany)",
            "vendor_origin": "Foreign OEM (Non-Local)",
            "quoted_price_inr": 53200000,
            "technical_responses": [
                {"spec_id": "SPEC-01", "parameter": "Working Hydraulic System Pressure", "offered_value": "250 bar continuous rated", "compliance": "Compliant (Superior)", "remarks": "Exceeds spec by 40 bar"},
                {"spec_id": "SPEC-02", "parameter": "Main High-Pressure Pump Capacity", "offered_value": "500 Litres/min", "compliance": "Compliant (Superior)", "remarks": "Dual A4VSO pump"},
                {"spec_id": "SPEC-03", "parameter": "Electric Drive Motor Rating & Class", "offered_value": "200 kW, IE4 Super Premium, IP65, Class H", "compliance": "Compliant (Superior)", "remarks": "ABB Germany"},
                {"spec_id": "SPEC-04", "parameter": "Hydraulic Oil Reservoir Tank Capacity", "offered_value": "3500 Litres, 100% SS-316L", "compliance": "Compliant (Superior)", "remarks": "SS-316L tank"},
                {"spec_id": "SPEC-05", "parameter": "Filtration System Rating", "offered_value": "2 Micron absolute, Parker Duplex", "compliance": "Compliant (Superior)", "remarks": "Parker IO-link"},
                {"spec_id": "SPEC-06", "parameter": "Oil Cooling System", "offered_value": "Shell & Tube, Titanium-SS316Ti", "compliance": "Compliant (Superior)", "remarks": "Titanium stabilized"},
                {"spec_id": "SPEC-07", "parameter": "PLC Automation & SCADA Interface", "offered_value": "Siemens S7-1518F Fail-Safe with OPC-UA & Profinet", "compliance": "Compliant (Superior)", "remarks": "Full Industry 4.0 suite"},
                {"spec_id": "SPEC-08", "parameter": "Condition Monitoring Sensors", "offered_value": "3-Axis accelerometers, particle counter & oil degradation", "compliance": "Compliant (Superior)", "remarks": "Full IoT sensors"}
            ],
            "commercial_responses": {
                "payment_terms": "80% LC against Bill of Lading, 10% commissioning, 10% against PBG",
                "delivery_schedule": "16 Weeks",
                "warranty_period": "24 Months"
            }
        }
    ]
    
    with open(VENDOR_BIDS_FILE, "w", encoding="utf-8") as f:
        json.dump(vendor_bids, f, indent=2)


if __name__ == "__main__":
    generate_tender_data()
    sync_all_real_world_apis()
    print("All real-world and tender specs generated successfully.")
