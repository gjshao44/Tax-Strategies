# v0.2 Release Notes

## Retirement Tax Strategy Planner

### Overview

v0.2 is a major UI reorganization around the **5 key retirement tax questions**, replacing the single-tab optimizer with a guided, question-per-tab structure. Each tab follows a consistent pattern: inputs, key insight with "Apply to Plan" button, interactive chart, and reference data.

### New Tab Structure

| # | Tab | Question |
|---|-----|----------|
| 1 | When to Retire? | Compare retirement years — net worth impact of working longer |
| 2 | When to Claim SS? | Social Security claiming age optimizer for both spouses |
| 3 | Roth Conversion? | Optimal annual conversion amount and golden window |
| 4 | Tax-Exempt Bonds? | **NEW** — Muni allocation optimizer with tax-equivalent yield |
| 5 | Capital Gains? | **NEW** — 0% bracket harvesting optimizer |
| 6 | Scenarios | **Renamed/restyled** — Withdrawal strategy & Monte Carlo stress tests |
| 7 | Plan Summary | **Renamed/restyled** — Combined plan result with KPI dashboard |
| 8 | Data Management | Import/export profiles |

### New Features

- **Tax-Exempt Bonds tab:** Tax-equivalent yield calculator, muni allocation comparison (0–100%), MAGI/IRMAA impact analysis, TEY reference table across all brackets
- **Capital Gains tab:** 0% bracket capacity calculator, optimal harvest simulation (capped at 10% of brokerage), actual incremental tax from full simulation
- **"Apply to Plan" pattern:** Every optimization tab offers a one-click button to push the recommended value to your sidebar settings
- **Interactive tooltips:** All charts use nearest-point selection with hover tooltips (Altair)
- **Scenario tab improvements:** Withdrawal strategy descriptions, growth profile explanations with upside/downside framing, multi-select to isolate profiles, per-profile apply buttons
- **Plan Summary improvements:** Strategy vs. Do Nothing vs. Best Roth trajectory chart, key insight at top, About/Methodology moved to bottom reference

### Renamed & Reorganized

- App title: "Retirement Tax Strategy Planner" (was "Comprehensive Retirement Wealth & Tax Optimizer")
- "What-If Analysis" → "Scenarios" (moved before Plan Summary)
- "Detailed Roadmap" → "Plan Summary"
- Scenario labels: "Your Plan" / "Best Roth" / "Do Nothing" (was "Strategy" / "Optimum" / "Idle")

### Bug Fixes & Polish

- Fixed LaTeX rendering issues — removed `$` from all `st.markdown`/`st.success`/`st.info` calls
- Fixed retirement tab not accounting for additional earning years
- Fixed apples-to-apples comparison (all scenarios end at same year)
- Fixed SS spousal benefit calculation (simplified to independent amounts)
- Removed redundant sidebar SS expander (SS tab + Apply handles it)
- Consolidated "Final Salary" and "Working Salary" into single input
- Default simulation horizon bumped from 20 to 25 years
- Capital gains harvest capped at 10% of brokerage balance for realism
- Privacy notice removed from top (already in sidebar footer)

### Bilingual Support

All new content (tabs, insights, descriptions, buttons) available in both English and Chinese.
