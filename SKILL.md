# Aviation Engineer - AD/SB Evaluator Agent v6.3

## Purpose
Token-efficient AD/SB evaluation for PC-12 fleet with CAMO-standard compliance tracking.
Supports both **EASA** and **FAA** Airworthiness Directives, plus Service Bulletin tracking.

## v6.3 Enhancements — Fleet-Focused Dashboard Redesign
- **Fleet AD Compliance Matrix** - Replaced flat 100-AD table with matrix view: ADs on Y-axis, 20 aircraft on X-axis, grouped by variant (PC-12 | PC-12/45 | PC-12/47 | PC-12/47E)
- **Only Fleet-Applicable ADs** - Dashboard now shows only PC-12 fleet ADs (14 ADs) instead of all 100 EASA ADs
- **Variant-Based Applicability** - Matrix cells show N/A (`-` grey) for aircraft variants not covered by an AD
- **Latest Published ADs Banner** - Highlighted section at top showing ADs published in last 14 days (EASA bi-weekly cycle), with orange styling and variant tags
- **Click-to-Expand Detail Rows** - Click any AD row in the matrix to expand per-aircraft compliance details with dates
- **Column Highlighting** - Click an aircraft column header to highlight that aircraft across the entire matrix
- **14 Realistic PC-12 Fleet ADs** - Added to CSV with varying applicability: ~4 all-variant, ~3 PC-12/47+47E, ~3 PC-12/47E-only, ~2 PC-12+PC-12/45, ~2 mid-generation
- **Updated Statistics** - Stats now reflect fleet-applicable AD counts only (not full EASA register)
- **AD/SB Dropdown Selectors** - Dropdown lists to select a specific AD or SB (or "Show All") instead of search box
- **SB Compliance Matrix** - Redesigned to match AD matrix style: SBs on Y-axis (selectable via dropdown), aircraft on X-axis grouped by variant
- **EASA Prefix** - All AD numbers now display with "EASA" prefix (e.g., EASA 2026-0010) for clear authority identification
- **CSS Tooltips** - Hover on green "C" cells to see compliance date via styled tooltip (not browser title)
- **Unique Compliance Dates** - Each aircraft registration has a different compliance date per AD (realistic per-aircraft scheduling)
- **Filter Buttons** - Matrix supports filter by All/Open/Accomplished status

## v6.2 Enhancements
- **AD Compliance Status Tracking** - Each AD now has `Compliance_Status` (Open/Accomplished) and `Compliance_Date` fields
- **EASA AD Register in Dashboard** - Full 100-AD register table with sortable columns, filter buttons (All/Open/Accomplished), and search
- **Compliance Progress Bar** - Visual progress bar showing accomplished vs open ratio in dashboard
- **SB Per-Aircraft Compliance** - SB matrix now supports marking individual aircraft SBs as Complied (C) with accomplishment dates (hover tooltip)
- **CSV Data Source** - `easa_ads_100.csv` now includes `Compliance_Status` and `Compliance_Date` columns
- **Dashboard Filters** - Interactive filter buttons and search box for AD register table

## v6.1 Enhancements
- **SB Extraction Module** - Auto-extract SB references from AD text
- **SB Seed Database** - 7 known Pilatus SBs pre-populated
- **SB Compliance Tracking** - Track SB compliance per aircraft
- **SB Dashboard Section** - SB summary + per-aircraft matrix in HTML dashboard

## v6.0 Enhancements
- **Fleet Database Validation** - Auto-validate fleet data before every AD check
- **Compliance Deadline Calculator** - Calculate due dates per aircraft (calendar + FH-based)
- **Confidence Scoring** - 100-point applicability scoring with breakdown
- **Diff Reporting** - "What changed since last check" comparison
- **HTML Dashboard** - Visual compliance dashboard for management reporting

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
| "Evaluate this AD" + [PDF path] | Full CAMO evaluation with confidence scoring + SB extraction |
| "Evaluate all ADs in folder" | Batch process ADs/ folder |
| "Validate fleet database" | Check fleet data for errors/warnings |
| "Calculate compliance deadlines" | Calculate due dates for all open ADs |
| "Show changes since last check" | Generate diff report |
| "Generate compliance dashboard" | Create HTML dashboard with SB matrix |
| "Mark AD as accomplished" | Update AD compliance status and date |
| "Show open ADs" | Filter dashboard to show only open ADs |
| "Show accomplished ADs" | Filter dashboard to show completed ADs |
| "Show SB summary" | Display SB tracking status |
| "Extract SBs from AD" | Extract SB references from AD text |
| "Show fleet AD matrix" | Open fleet-focused AD compliance matrix dashboard |
| "Show latest fleet ADs" | Show ADs published in last bi-weekly cycle |
| "Filter open fleet ADs" | Filter AD matrix to show only open fleet ADs |

---

## File Locations

```
C:\Users\delye\.claude\skills\aviation-engineer-agent\
├── SKILL.md                          # This file
├── QUICKREF.md                       # Quick reference guide
├── ADs\                              # AD PDFs (EASA + FAA)
├── EASA_Reports\                     # EASA bi-weekly HTML archive + dashboards
├── FAA_Reports\                      # FAA AD check archive (JSON)
├── Audit_Evidence\                   # Validation + no-applicable-AD evidence
├── Fleet_Database_Expanded.xlsx      # 20 PC-12 aircraft
├── AD_Evaluation_Master_CAMO.xlsx    # CAMO register (3 sheets)
│   ├── AD_SB_Register                # EASA AD evaluations (with confidence + deadlines)
│   ├── FAA_AD_Register               # FAA AD evaluations (with confidence + deadlines)
│   └── SB_Register                   # Service Bulletin tracking (NEW v6.1)
├── sb_seed_database.xlsx             # 7 known Pilatus SBs (NEW v6.1)
├── dashboard.html                    # Latest HTML compliance dashboard (with SB section + AD register)
│
├── # Core Scripts
├── download_easa_biweekly.py         # EASA bi-weekly downloader
├── faa_ad_checker.py                 # FAA Federal Register checker v2.1
├── easa_biweekly_checker.py          # EASA bi-weekly checker v2.1
├── easa_html_scraper.py              # HTML metadata scraper
├── evaluate_ads_camo.py              # Full evaluation script v2.1 (with SB extraction)
├── evaluate_faa_ads.py               # FAA evaluation script v2.1
├── evaluate_new_ads.py               # AD evaluation helper
│
├── # v6.0 New Scripts
├── validate_fleet_db.py              # Fleet database validation
├── compliance_calculator.py          # Compliance deadline calculator
├── confidence_scoring.py             # Confidence scoring module
├── diff_report.py                    # Diff/change reporting
├── generate_dashboard.py             # HTML dashboard generator (with SB section)
│
├── # v6.1 New Scripts
└── sb_extractor.py                   # SB extraction and tracking module
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

### Sheet 3: SB_Register (NEW v6.1)
Service Bulletin tracking with 35 fields including:
- SB identification (number, revision, date)
- Source AD reference (which AD references this SB)
- ATA chapter and subject
- Compliance category (MANDATORY, RECOMMENDED, OPTIONAL)
- Compliance type (ONE-TIME, REPETITIVE)
- Fleet applicability (model, MSN range, applicable aircraft list)
- Status (OPEN, COMPLIED, N/A)

---

## NEW: Service Bulletin (SB) Tracking (v6.1)

### Automatic SB Extraction
When evaluating an AD, the system automatically extracts SB references from:
- AD subject/title
- Related documents section
- Terminating action text
- SB reference fields

### SB Seed Database
Pre-populated with 7 known Pilatus PC-12 SBs:
| SB Number | ATA | Subject |
|-----------|-----|---------|
| SB 71-009 | 71 | Engine Mount Inspection |
| SB 32-020 | 32 | Landing Gear Actuator |
| SB 32-027 | 32 | MLG Trunnion Inspection |
| SB 61-002 | 61 | Propeller Blade Life |
| SB 34-022 | 34 | TCAS Upgrade |
| SB 26-002 | 26 | Fire Extinguisher Replacement |
| SB 26-003 | 26 | Fire Detection System |

### SB Extraction Commands
```bash
# Extract SBs from AD text
python sb_extractor.py --scan-all

# Show SB summary
python sb_extractor.py --summary

# Show per-aircraft SB matrix
python sb_extractor.py --matrix

# Load seed database
python sb_extractor.py --load-seed
```

### SB Dashboard Section
The HTML dashboard includes:
- SB compliance summary cards (color-coded by category)
- Per-aircraft SB matrix (OPEN/COMPLIED/N/A status) with accomplishment date tooltips
- SB counts in statistics section

---

## NEW: AD Compliance Status Tracking (v6.2)

### CSV Data Structure
`easa_ads_100.csv` now includes two additional columns:
| Column | Values | Description |
|--------|--------|-------------|
| `Compliance_Status` | Open / Accomplished | Whether the AD has been complied with |
| `Compliance_Date` | YYYY-MM-DD or empty | Date when compliance was completed |

### Dashboard AD Register
The HTML dashboard now includes a full EASA AD Register table with:
- **8 sortable columns**: AD Number, Issue Date, ATA, Subject, Aircraft Types, AD Status, Compliance, Compliance Date
- **Filter buttons**: All (100), Open (80), Accomplished (20)
- **Search box**: Live search across AD number and subject
- **Color-coded badges**: Green for ACCOMPLISHED, Red for OPEN
- **Green-tinted rows** for accomplished ADs
- **Clickable AD numbers** linking directly to EASA AD detail pages
- **Compliance progress bar** showing accomplished vs open ratio

### SB Per-Aircraft Compliance
SB matrix cells can now show:
- `O` (red) = Open
- `C` (green) = Complied - hover to see accomplishment date
- `-` (grey) = Not Applicable

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
| `AD_Evaluation_Master_CAMO.xlsx` | All evaluations (3 sheets: AD_SB, FAA, SB) |
| `sb_seed_database.xlsx` | Known SBs reference database (v6.1) |
| `EASA_Reports/*.html` | Archived EASA bi-weekly reports |
| `EASA_Reports/*.json` | EASA check summaries |
| `FAA_Reports/*.json` | FAA check archives |
| `Audit_Evidence/*.json` | No-applicable-AD evidence |
| `ADs/*.pdf` | Downloaded AD PDFs (EASA + FAA) |
| `dashboard.html` | HTML compliance dashboard with SB section |

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

## TODO: Publish Dashboard on GitHub Pages

### Goal
Make `dashboard.html` publicly accessible as a live, interactive web page.

### Steps to Implement
1. **Create a GitHub repo** (e.g. `ad-sb-compliance-dashboard`)
   ```bash
   cd "C:\Users\delye\.claude\skills\aviation-engineer-agent"
   git init
   git add dashboard.html
   git commit -m "Initial dashboard publish"
   gh repo create ad-sb-compliance-dashboard --public --source=. --push
   ```

2. **Enable GitHub Pages**
   ```bash
   gh api repos/{owner}/ad-sb-compliance-dashboard/pages -X POST -f source.branch=main -f source.path=/
   ```
   Or manually: repo Settings → Pages → Source: Deploy from branch → Branch: `main` / `/ (root)`

3. **Access the live dashboard**
   - URL will be: `https://<username>.github.io/ad-sb-compliance-dashboard/dashboard.html`
   - Works immediately — no server needed, all client-side HTML/CSS/JS

### Notes
- The dashboard is fully self-contained (single HTML file, no dependencies)
- All interactivity (dropdowns, filters, expand rows, tooltips, column highlighting) works as-is
- To update: just push changes → GitHub Pages auto-deploys
- Consider renaming `dashboard.html` → `index.html` so the URL is cleaner (no filename needed)

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
