# Aviation Engineer AD/SB Evaluator Agent v5.1

A Claude Code skill for token-efficient Airworthiness Directive (AD) and Service Bulletin (SB) evaluation for PC-12 fleet management with CAMO-standard compliance tracking.

## Features

- **Dual Authority Support**: Monitors both EASA and FAA Airworthiness Directives
- **Token Efficient**: Uses HTML/JSON parsing (0 LLM tokens) for filtering
- **Emergency AD Detection**: Auto-detects EMERGENCY/IMMEDIATE/BEFORE FURTHER FLIGHT keywords
- **CAMO Compliance**: 75-field evaluation register with audit trail
- **Supersedure Tracking**: Automatic chain handling for superseded ADs
- **Audit Evidence**: Generates proof of monitoring when no ADs apply

## Quick Start

```bash
# In Claude Code, invoke the skill:
/aviation-engineer-agent

# Then use these commands:
"Check latest EASA bi-weekly"
"Check latest FAA ADs"
"Evaluate this AD against fleet"
```

## Installation

1. Clone this repository to your Claude Code skills folder:
   ```bash
   git clone https://github.com/YOUR_USERNAME/aviation-engineer-agent.git ~/.claude/skills/aviation-engineer-agent
   ```

2. Install Python dependencies:
   ```bash
   pip install pandas openpyxl requests beautifulsoup4
   ```

3. Create your fleet database (`Fleet_Database_Expanded.xlsx`) with columns:
   - Registration, MSN, Aircraft_Model, Total_Hours, Total_Landings, Operator
   - Optional: Component_PN, Component_SN, STC_List

4. Create required folders:
   ```bash
   mkdir ADs EASA_Reports FAA_Reports Audit_Evidence
   ```

## File Structure

```
aviation-engineer-agent/
├── SKILL.md                      # Claude Code skill definition
├── QUICKREF.md                   # Quick reference guide
├── README.md                     # This file
├── .gitignore                    # Git ignore rules
│
├── faa_ad_checker.py             # FAA Federal Register API checker
├── easa_biweekly_checker.py      # EASA bi-weekly HTML checker
├── evaluate_ads_camo.py          # EASA AD fleet evaluation
├── evaluate_faa_ads.py           # FAA AD fleet evaluation
├── evaluate_new_ads.py           # AD evaluation helper
├── easa_html_scraper.py          # HTML metadata scraper
├── download_easa_biweekly.py     # EASA report downloader
│
├── ADs/                          # Downloaded AD PDFs (gitignored)
├── EASA_Reports/                 # EASA bi-weekly archives (gitignored)
├── FAA_Reports/                  # FAA check archives (gitignored)
├── Audit_Evidence/               # No-applicable-AD evidence (gitignored)
│
├── Fleet_Database_Expanded.xlsx  # Your fleet data (gitignored)
└── AD_Evaluation_Master_CAMO.xlsx # Evaluation register (gitignored)
```

## Workflow

### EASA Bi-Weekly Check
```
1. Fetch HTML report from ad.easa.europa.eu
2. Parse for PC-12/Pilatus keywords (0 tokens)
3. Check for EMERGENCY keywords
4. Download PDFs only for applicable ADs
5. Archive report + generate audit evidence
```

### FAA AD Check
```
1. Query Federal Register API
2. Filter for Airworthiness Directives
3. Check for EMERGENCY keywords
4. Download PDFs only for applicable ADs
5. Evaluate against fleet → write to Excel
6. Archive report + generate audit evidence
```

## Emergency AD Handling

Keywords that trigger **same-day evaluation**:
- `EMERGENCY`
- `IMMEDIATE`
- `BEFORE FURTHER FLIGHT`
- `BEFORE NEXT FLIGHT`
- `URGENT`
- `UNSAFE CONDITION`

## Token Efficiency

| Scenario | Old Method | New Method |
|----------|------------|------------|
| Bi-weekly check (24 ADs, 0 PC-12) | 96,000 tokens | **0 tokens** |
| Bi-weekly check (24 ADs, 2 PC-12) | 96,000 tokens | **8,000 tokens** |

## Fleet Configuration

Default configuration for PC-12 variants:
- PC-12
- PC-12/45
- PC-12/47
- PC-12/47E

Modify `FLEET_KEYWORDS` in the Python scripts to adapt for other aircraft types.

## CAMO Compliance Features

| Feature | Implementation |
|---------|----------------|
| Emergency AD handling | Auto-detect keywords, same-day evaluation |
| Monitoring evidence | `monitoring_date`, `monitoring_time` fields |
| Evaluation accountability | `evaluation_date`, `evaluator` fields |
| No-AD evidence | JSON records in `Audit_Evidence/` |
| Supersedure tracking | Auto-link old AD → new AD |

## Output

### Excel Sheets
- **AD_SB_Register**: EASA AD evaluations (75 columns)
- **FAA_AD_Register**: FAA AD evaluations (38 columns)

### Applicability Status
- `APPLICABLE` - AD applies to aircraft
- `NOT APPLICABLE` - AD does not apply
- `REQUIRES VERIFICATION` - Component check needed
- `SUPERSEDED - CLOSED` - Replaced by newer AD

## Requirements

- Python 3.8+
- pandas
- openpyxl
- requests
- beautifulsoup4

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v5.1 | Feb 3, 2026 | Emergency AD interrupt, audit evidence, supersedure chain |
| v5.0 | Feb 2, 2026 | FAA support, dual authority monitoring |
| v4.0 | Feb 1, 2026 | Bi-weekly HTML check, token optimization |
| v3.0 | Feb 1, 2026 | CAMO-standard 73 fields |

## License

MIT License

## Disclaimer

This tool is for **decision support only**. All AD/SB evaluations must be verified by qualified CAMO engineers before implementation. The authors are not responsible for compliance decisions made based on this tool's output.

## Contributing

Contributions welcome! Please submit issues and pull requests.
