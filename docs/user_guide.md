# 📘 Operational User & Business Guide
## SAIL Bokaro Steel Plant — SCM AI Innovation Suite

---

## 1. Introduction
The **SAIL BSL SCM AI Suite** is an intuitive, web-based analytics platform designed for materials management officers, maintenance engineers, and procurement committees. This guide outlines how to operate each module to achieve maximum business efficiency.

---

## 2. Navigating the Dashboard

### 2.1. Global Controls & Status Bar
* **Live Market Ticker:** Located in the header, displaying the real-time spot USD/INR exchange rate.
* **Sync Button (`⚡ Ingest Live Open API Data`):** Located in the left sidebar. Click to pull the latest open market series from Yahoo Finance and the World Bank into the local dataset.

---

### 2.2. Tab 1: Executive Overview & Strategic Roadmap
1. **Initiative KPIs:** Review overall POC health, annual value potential (₹8.64 Cr+), and license savings.
2. **Roadmap Matrix:** Check milestones for Maintenance, Materials Management, and Procurement departments.
3. **C&IT Integration Plan:** Review data flow, SAP integration paths, and security protocols.

---

### 2.3. Tab 2: AI Demand Forecasting (Maintenance Spares)
* **Goal:** Determine monthly procurement schedules and optimize safety stocks for critical spares.
* **Step-by-Step Instructions:**
  1. **Select Monitored Spare Part:** Use the dropdown at the top to choose a spare part (e.g. *Tuyere Coolers*, *Roller Bearings*, *Mud Gun Pistons*).
  2. **Set Forecast Horizon:** Use the slider to choose between 3 to 12 months forward forecasting.
  3. **Analyze Forecast Curve:** View historical consumption (grey) alongside the H2O forecast (blue) and 90% confidence bands.
  4. **Review Inventory Optimization:**
     * **AI Safety Stock:** Recommended units to keep on hand.
     * **Reorder Point (ROP):** Threshold inventory level that triggers a purchase requisition in SAP.
     * **Working Capital Freed:** Exact rupee savings compared to traditional 2-month static inventory buffers.
  5. **Export Monthly Schedule:** Use the table to plan monthly purchase quantities aligned with blast furnace overhaul dates.

---

### 2.4. Tab 3: AI Technical & Commercial Bid Evaluation
* **Goal:** Perform an audit of vendor bids, calculate commercial penalties, and generate the Comparative Statement of Tenders (CST).
* **Step-by-Step Instructions:**
  1. **Select Tender RFP Package:** Choose between *Hot Strip Mill Descaling Hydraulic Unit*, *Blast Furnace Refractory Castables*, or *SMS Continuous Caster Actuators*.
  2. **Review Initial Recommendation:** Check the **Recommended L1 Bidder**, award value, budget utilization, and direct savings.
  3. **Analyze the Comparative Statement (CST):**
     * Review the evaluated landed prices after automatic commercial loading penalties.
     * Check vendor qualification badges (✅ QUALIFIED, ❌ REJECTED, ⚠️ DISQUALIFIED).
  4. **Inspect Technical Compliance Matrix:** Verify clause-by-clause compliance tags (🟢 SUPERIOR, ✅ COMPLIANT, 🟡 PARTIAL, 🔴 DEVIATION).
  5. **Simulate Negotiations & Counter-Offers:**
     * Check **`🛠️ Live Bid Negotiation & Counter-Offer Simulator`**.
     * Adjust vendor discount sliders to model reverse auctions or price concessions.
     * Check **`Clear Technical Deviations`** if a vendor clarifies a specification shortfall during techno-commercial meetings.
     * Watch the CST rankings, evaluated prices, and purchase recommendations recalculate live!

---

### 2.5. Tab 4: AI Should-Cost Prediction & Negotiation Corridor (Ferro Alloys)
* **Goal:** Establish a data-backed negotiation baseline for bulk raw materials and alloys.
* **Step-by-Step Instructions:**
  1. **Select Commodity:** Choose an alloy (e.g. *Silico Manganese 60/14*, *Ferro Silicon 70%*, *HC Ferro Manganese*).
  2. **Choose Mode:**
     * **`🟢 Real-Time Live Feed`:** Automatically calculates the negotiation corridor using live USD/INR and energy indices.
     * **`🛠️ Custom What-If Simulator`:** Allows manual adjustment of power tariffs, coke prices, and exchange rates.
  3. **Negotiate with P10 / P50 / P90 Corridors:**
     * **P10 (Aggressive Opening Bid):** Use to open reverse auctions or counter vendor quotations.
     * **P50 (Fair Market Should-Cost):** Target purchase order settlement rate.
     * **P90 (Walk-Away Ceiling):** Maximum acceptable ceiling price.
  4. **Review Cost Driver Breakdown:** Inspect the pie chart to understand which input factor (power, ore, coke, FX) is driving current market price variations.

---

## 3. Best Practices & Troubleshooting
* **When to Sync Data:** Click `⚡ Ingest Live Open API Data` at the start of every procurement cycle to refresh the macroeconomic series.
* **Air-Gapped Operation:** If operating without internet access, the platform automatically utilizes the pre-cached historical datasets in `data/` without degradation.
