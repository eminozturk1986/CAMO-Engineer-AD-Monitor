# Aviation Engineer - AD/SB Evaluator Agent v5.1

## Purpose
Token-efficient AD/SB evaluation for PC-12 fleet with CAMO-standard compliance tracking.
Supports both **EASA** and **FAA** Airworthiness Directives.

## v5.1 Enhancements (CAMO Compliance)
- **Emergency AD Interrupt Logic** - Auto-detect EMERGENCY/IMMEDIATE/BEFORE FURTHER FLIGHT keywords
- **No Applicable AD Evidence** - Audit trail when no fleet ADs found
- **Separate Monitoring vs Evaluation Dates** - System vs accountable engineer dates
- **Supersedure Chain Handling** - Auto-link superseded ADs

## Quick Start Commands

| You Say | What Happens |
|---------|--------------|
| "Check latest EASA bi-weekly" | EASA HTML fetch → filter → 0 tokens if no PC-12 |
| "Check latest FAA ADs" | Federal Register API → filter → 0 tokens if no PC-12 |
| "Check both EASA and FAA" | Run both checks in parallel |
| "Evaluate this AD" + [PDF path] | Full CAMO evaluation |
| "Evaluate all ADs in folder" | Batch process ADs/ folder |

---

## File Locations

```
C:\Users\delye\.claude\skills\aviation-engineer-agent\
├── SKILL.md                          # This file
├── ADs\                              # AD PDFs (EASA + FAA)
├── EASA_Reports\                     # EASA bi-weekly HTML archive
├── FAA_Reports\                      # FAA AD check archive (JSON)
├── Audit_Evidence\                   # No-applicable-AD evidence (NEW)
├── Fleet_Database_Expanded.xlsx      # 20 PC-12 aircraft
├── AD_Evaluation_Master_CAMO.xlsx    # CAMO register (2 sheets)
│   ├── AD_SB_Register                # EASA AD evaluations
│   └── FAA_AD_Register               # FAA AD evaluations
├── download_easa_biweekly.py         # EASA bi-weekly downloader
├── faa_ad_checker.py                 # FAA Federal Register checker v2.0
├── easa_biweekly_checker.py          # EASA bi-weekly checker v2.0
├── easa_html_scraper.py              # HTML metadata scraper
├── evaluate_ads_camo.py              # Full evaluation script v2.0
└── evaluate_new_ads.py               # AD evaluation helper
```

---

## NEW: Emergency AD Interrupt Logic

### Automatic Detection
When an AD contains these keywords, it **bypasses normal weekly batching**:
- `EMERGENCY`
- `IMMEDIATE`
- `BEFORE FURTHER FLIGHT`
- `BEFORE NEXT FLIGHT`
- `URGENT`
- `UNSAFE CONDITION`

### What Happens
1. System detects emergency keyword in AD title/abstract
2. AD marked with `compliance_category = EMERGENCY`
3. Detection time logged separately from evaluation time
4. **Same-day evaluation triggered** (bypasses batch)
5. PDF downloaded with priority
6. Alert displayed:

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
[!!!] EMERGENCY AD INTERRUPT - 1 EMERGENCY AD(s) DETECTED
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   >>> FAA AD 2026-00123: Pilatus PC-12 - Engine Mount...
       Emergency keyword: BEFORE FURTHER FLIGHT
       Detection time: 2026-02-03 14:32:15

   ACTION REQUIRED: Same-day evaluation mandatory
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

---

## NEW: No Applicable AD Evidence

### Purpose
CAMO auditors require proof that monitoring was performed **even when no action was required**.

### Generated When
- Monitoring check completes with 0 fleet-applicable ADs
- Saved to `Audit_Evidence/` folder

### Evidence Record Format
```json
{
  "record_type": "NO_APPLICABLE_AD_EVIDENCE",
  "authority": "EASA",
  "period_start": "2026-01-19",
  "period_end": "2026-02-02",
  "result": "NO_APPLICABLE_AD",
  "total_ads_checked": 24,
  "fleet_applicable_count": 0,
  "monitoring_date": "2026-02-03",
  "monitoring_time": "14:30:00",
  "system_identifier": "EASA Bi-Weekly Checker v2.0",
  "fleet_types_monitored": ["PC-12", "PC-12/45", "PC-12/47", "PC-12/47E", "Pilatus"],
  "statement": "Monitoring check completed for EASA ADs. Period: 2026-01-19 to 2026-02-02. Total ADs reviewed: 24. Fleet-applicable ADs found: 0. No action required."
}
```

### Archive Pattern
```
Audit_Evidence/no_applicable_ad_EASA_20260203.json
Audit_Evidence/no_applicable_ad_FAA_20260203.json
```

---

## NEW: Separate Monitoring vs Evaluation Dates

### Why This Matters
- **Monitoring** = when the authority source was checked (system-driven)
- **Evaluation** = when an engineer completed applicability/compliance assessment (accountable)

### Fields in Reports
| Field | Description | Set By |
|-------|-------------|--------|
| `monitoring_date` | Date source was checked | System (automatic) |
| `monitoring_time` | Time source was checked | System (automatic) |
| `monitoring_system` | System identifier | System (automatic) |
| `evaluation_date` | Date engineer evaluated | Engineer (accountable) |
| `evaluator` | Engineer name/ID | Engineer (accountable) |

### In Excel Register
| Column | Description |
|--------|-------------|
| `Monitoring_Date` | When AD source was monitored |
| `Evaluation_Date` | When CAMO engineer evaluated |
| `Evaluation_Time` | Time of evaluation |
| `Evaluated_By` | Responsible engineer |

---

## NEW: Supersedure Chain Handling

### Automatic Detection
When a new AD is detected that supersedes an existing AD:

1. System checks if new AD references superseded AD
2. Previous AD marked as `SUPERSEDED – CLOSED`
3. Link created: old AD → new AD
4. Prevents duplicate or conflicting open entries

### Example Output
```
[SUPERSEDURE] EASA AD 2025-0182 supersedes EASA AD 2021-0214
   [SUPERSEDED] EASA AD 2021-0214 marked as superseded by EASA AD 2025-0182
```

### Updated Fields
| Field | Old Value | New Value |
|-------|-----------|-----------|
| `Superseded_By` | NULL | EASA AD 2025-0182 |
| `Is_Current` | Yes | No |
| `Compliance_Status` | OPEN | SUPERSEDED - CLOSED |
| `Notes` | ... | ... \| SUPERSEDED by EASA AD 2025-0182 |

---

## EASA Bi-Weekly Check

### URL Pattern
```
https://ad.easa.europa.eu/blob/easa_biweekly_[START]_[END]_[NUM]-[YEAR].html/biweekly

Example: easa_biweekly_2026-01-05_2026-01-18_02-2026.html
```

### Workflow (v2.0)
```
1. Calculate current bi-weekly period
2. Record monitoring_date
3. Download HTML report (~10 KB)
4. Parse with Python (0 tokens)
5. Check for EMERGENCY keywords
6. Filter for PC-12/Pilatus (0 tokens)
7. Archive to EASA_Reports/
8. IF EMERGENCY AD → same-day evaluation
9. IF PC-12 ADs found → download PDF → full evaluation
10. IF no PC-12 ADs → generate audit evidence → done
```

---

## FAA AD Check

### API Endpoint
```
https://www.federalregister.gov/api/v1/documents.json?
  conditions[agencies][]=federal-aviation-administration
  &conditions[type][]=rule
  &per_page=100
  &order=newest
```

### Workflow (v2.0)
```
1. Query Federal Register API (last 14 days default)
2. Record monitoring_date
3. Filter response for Airworthiness Directives
4. Check for EMERGENCY keywords
5. Parse JSON with Python (0 tokens)
6. Filter for PC-12/Pilatus keywords (0 tokens)
7. Archive to FAA_Reports/
8. IF EMERGENCY AD → same-day evaluation
9. IF PC-12 ADs found → download PDF → full evaluation
10. IF no PC-12 ADs → generate audit evidence → done
```

---

## Token Savings Comparison

| Method | 24 ADs Checked | Tokens |
|--------|----------------|--------|
| Old (all PDFs) | 24 x 4000 | 96,000 |
| EASA HTML filter | HTML only | **0** |
| FAA API filter | JSON only | **0** |

---

## Fleet Configuration

**20 Aircraft Monitored:**
- PC-12 (2): MSN 147, 215
- PC-12/45 (3): MSN 312, 455, 489
- PC-12/47 (6): MSN 601-1389
- PC-12/47E (9): MSN 1601-2901

**Filter Keywords:** PC-12, PC12, PC-12/45, PC-12/47, PC-12/47E, Pilatus

**Emergency Keywords:** EMERGENCY, IMMEDIATE, BEFORE FURTHER FLIGHT, BEFORE NEXT FLIGHT, URGENT, UNSAFE CONDITION

---

## Master Excel Sheets

### Sheet 1: AD_SB_Register (EASA)
EASA AD/SB evaluations with 75 CAMO-standard fields (v2.0 adds Monitoring_Date, Evaluation_Time).

### Sheet 2: FAA_AD_Register
FAA AD evaluations with 32 fields (v2.0 adds monitoring/evaluation separation).

---

## Document Type Handling

| Source | Type | Example | Action |
|--------|------|---------|--------|
| EASA | AD | 2025-0182 | Full evaluation |
| EASA | Emergency AD | Contains keyword | **SAME-DAY** evaluation |
| EASA | AD-CN | 2021-0110-CN | Mark TERMINATED |
| EASA | AD (Superseded) | 2022-0103 | Mark SUPERSEDED-CLOSED |
| FAA | AD | 2025-01-01 | Full evaluation |
| FAA | Emergency AD | 2025-01-01-E | **SAME-DAY** evaluation |
| Both | SB | SB 25-059 | Evaluate if referenced |

---

## Applicability Logic

```
1. Model match?     → PC-12/47E in AD, fleet has PC-12/47E?
2. MSN in range?    → MSN 2001-2999, fleet MSN 2345?
3. Component P/N?   → Check Component_PN column
4. STC required?    → Check STC_List column

Result: APPLICABLE | NOT APPLICABLE | REQUIRES VERIFICATION
```

---

## Output Files

| File | Purpose |
|------|---------|
| `AD_Evaluation_Master_CAMO.xlsx` | All evaluations (2 sheets) |
| `EASA_Reports/*.html` | Archived EASA bi-weekly reports |
| `EASA_Reports/*.json` | EASA check summaries |
| `FAA_Reports/*.json` | FAA check archives |
| `Audit_Evidence/*.json` | No-applicable-AD evidence (NEW) |
| `ADs/*.pdf` | Downloaded AD PDFs (EASA + FAA) |

---

## Python Scripts

### faa_ad_checker.py (v2.0)
```python
# Run FAA check for last 14 days
python faa_ad_checker.py

# Run FAA check for last 30 days
python faa_ad_checker.py 30
```

### easa_biweekly_checker.py (v2.0)
```python
# Run EASA bi-weekly check
python easa_biweekly_checker.py
```

### download_easa_biweekly.py
```python
# Check specific EASA bi-weekly report
python download_easa_biweekly.py [URL]
```

---

## Audit Compliance Summary

| Requirement | Implementation |
|-------------|----------------|
| Emergency AD handling | Auto-detect keywords, same-day evaluation |
| Monitoring evidence | `monitoring_date`, `monitoring_time`, `monitoring_system` |
| Evaluation accountability | `evaluation_date`, `evaluator` fields |
| No-AD evidence | `Audit_Evidence/no_applicable_ad_*.json` |
| Supersedure tracking | Auto-detect, mark old AD closed, link new AD |
| Token efficiency | 0 tokens for HTML/JSON filtering |

---

## Important Notes

- **Token Efficiency:** Always use API/HTML check first
- **Zero Tokens:** HTML/JSON parsing uses Python, not LLM
- **PDF Only When Needed:** Only parse PDFs for applicable ADs
- **Emergency Priority:** Emergency ADs bypass normal batching
- **Audit Trail:** All reports and evidence saved for audits
- **Supersedure Chain:** Prevents duplicate open ADs
- **Decision Support:** Verify with qualified engineers
- **Dual Authority:** Track both EASA and FAA compliance
