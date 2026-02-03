# Aviation Engineer Agent - Quick Reference v5.1

## Usage
```
"Evaluate [AD PDF] against fleet using aviation-engineer-agent skill"
"Check latest EASA bi-weekly"
"Check latest FAA ADs"
```

## File Paths
| File | Path |
|------|------|
| AD Folder | `~/.claude/skills/aviation-engineer-agent/ADs/` |
| Fleet DB | `~/.claude/skills/aviation-engineer-agent/Fleet_Database_Expanded.xlsx` |
| Master | `~/.claude/skills/aviation-engineer-agent/AD_Evaluation_Master_CAMO.xlsx` |
| Audit Evidence | `~/.claude/skills/aviation-engineer-agent/Audit_Evidence/` |

## v5.1 New Features

### Emergency AD Interrupt
Keywords that trigger **same-day evaluation**:
```
EMERGENCY | IMMEDIATE | BEFORE FURTHER FLIGHT
BEFORE NEXT FLIGHT | URGENT | UNSAFE CONDITION
```

### Audit Evidence
When no fleet-applicable ADs found:
```
Audit_Evidence/no_applicable_ad_EASA_20260203.json
Audit_Evidence/no_applicable_ad_FAA_20260203.json
```

### Monitoring vs Evaluation Dates
| Field | Who Sets | Purpose |
|-------|----------|---------|
| `monitoring_date` | System | When source checked |
| `evaluation_date` | Engineer | When evaluated (accountable) |

### Supersedure Chain
```
New AD 2025-0182 supersedes 2021-0214
→ Old AD marked: SUPERSEDED - CLOSED
→ Linked: Superseded_By = 2025-0182
```

## Fleet Summary (20 Aircraft)
```
PC-12      2 aircraft  MSN 147-215
PC-12/45   3 aircraft  MSN 312-489
PC-12/47   6 aircraft  MSN 601-1389
PC-12/47E  9 aircraft  MSN 1601-2901
```

## Applicability Logic
```
1. Model match?    → No  → NOT APPLICABLE
2. MSN in range?   → No  → NOT APPLICABLE
3. Component P/N?  → Unknown → REQUIRES VERIFICATION
4. STC required?   → Missing → NOT APPLICABLE
5. All pass        → APPLICABLE
```

## Status Values
| Status | Meaning |
|--------|---------|
| OPEN | Awaiting compliance |
| COMPLIED | Done |
| N-A | Not applicable |
| TERMINATED | Completed by terminating action |
| DEFERRED | Deferred with approval |
| SUPERSEDED - CLOSED | Replaced by newer AD |

## Priority
| Type | Priority |
|------|----------|
| Emergency AD | **EMERGENCY** (same-day) |
| One-time + Component | CRITICAL |
| One-time | HIGH |
| Recurring + Component | HIGH |
| Recurring | MEDIUM |
| Recommended | LOW |

## Output Columns (75 total)
```
Section 1:  AD/SB Identification (8)
Section 2:  Effectivity (5)
Section 3:  Compliance Requirements (5)
Section 4:  Aircraft Identification (4)
Section 5:  Applicability Evaluation (6) ← +Monitoring_Date, Evaluation_Time
Section 6:  Compliance Status (3)
Section 7:  Compliance Due (7)
Section 8:  Compliance Accomplished (6)
Section 9:  Recurring Tracking (4)
Section 10: Parts & Resources (7)
Section 11: Documentation (4)
Section 12: Supersedure & History (3)
Section 13: AMP Integration (3)
Section 14: Assignment & Workflow (6)
Section 15: Notes & Remarks (4)
```

## Expected Output
```
AD: EASA AD 2025-0182 | PSU Trim Panel Modification
Type: One-time | Priority: HIGH
Models: PC-12/47E | MSN: 2001-2999

Fleet (20 aircraft):
APPLICABLE:            3 [D-FNEW, N2750EX, N2901NG]
NOT APPLICABLE:       14
REQUIRES VERIFICATION: 3 [N2050PA, N2345ST, OE-NEW]

Status: 3 OPEN
Results appended to AD_Evaluation_Master_CAMO.xlsx
```

## Emergency AD Output
```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
[!!!] EMERGENCY AD INTERRUPT - 1 EMERGENCY AD(s)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
>>> FAA AD 2026-00123: PC-12 - Engine Mount...
    Emergency keyword: BEFORE FURTHER FLIGHT
    Detection time: 2026-02-03 14:32:15

ACTION REQUIRED: Same-day evaluation mandatory
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

## Add New Aircraft
Edit `Fleet_Database_Expanded.xlsx`:
- Required: Registration, MSN, Aircraft_Model, Total_Hours, Total_Landings, Operator
- Optional: Component_PN, Component_SN, STC_List

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Model not matching | Check exact variant (PC-12/47 ≠ PC-12/47E) |
| MSN range parsing | Verify format: "2001-2999" or "all" |
| Component unknown | Flag as REQUIRES VERIFICATION |
| Emergency missed | Check EMERGENCY_KEYWORDS list |
| No audit evidence | Verify Audit_Evidence/ folder exists |

---
**Version:** 5.1 CAMO Standard | **Updated:** Feb 3, 2026
