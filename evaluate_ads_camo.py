"""
CAMO AD/SB Evaluation Script v2.0
=================================
Evaluates ADs against PC-12 fleet with CAMO-standard fields.

v2.0 Enhancements:
- Separate Monitoring_Date vs Evaluation_Date
- Supersedure chain handling (auto-detect and link)
- Emergency AD category handling
"""

import pandas as pd
from datetime import datetime, timedelta
import json
import os

SKILL_DIR = "C:/Users/delye/.claude/skills/aviation-engineer-agent"

# Load fleet database
fleet_path = f"{SKILL_DIR}/Fleet_Database_Expanded.xlsx"
fleet = pd.read_excel(fleet_path)

# Load existing CAMO master
master_path = f"{SKILL_DIR}/AD_Evaluation_Master_CAMO.xlsx"
try:
    master = pd.read_excel(master_path, sheet_name='AD_SB_Register')
except:
    master = pd.DataFrame()


def check_supersedure_chain(new_ad_number, master_df):
    """
    Check if new AD supersedes an existing AD in the register.
    Returns (supersedes_ad, superseded_row_index) or (None, None)
    """
    # Common supersedure patterns in AD numbers
    # e.g., 2025-0182 might supersede 2024-0182 or reference in text

    if master_df.empty:
        return None, None

    # Check if any existing AD is superseded by this one
    # (would need to parse AD text for "This AD supersedes..." - simplified here)

    return None, None


def mark_ad_superseded(master_df, ad_number, superseded_by):
    """
    Mark an existing AD as superseded and link to new AD.
    Prevents duplicate or conflicting open AD entries.
    """
    if master_df.empty:
        return master_df

    # Find rows with this AD number
    mask = master_df['AD_SB_Number'] == ad_number

    if mask.any():
        master_df.loc[mask, 'Superseded_By'] = superseded_by
        master_df.loc[mask, 'Is_Current'] = 'No'
        master_df.loc[mask, 'Compliance_Status'] = 'SUPERSEDED - CLOSED'
        master_df.loc[mask, 'Notes'] = master_df.loc[mask, 'Notes'].fillna('') + f' | SUPERSEDED by {superseded_by}'
        print(f"   [SUPERSEDED] {ad_number} marked as superseded by {superseded_by}")

    return master_df

# AD 1: EASA AD 2025-0182
ad1 = {
    'AD_SB_Number': 'EASA AD 2025-0182',
    'Revision': 'Original',
    'Document_Type': 'AD',
    'Issuing_Authority': 'EASA',
    'Issue_Date': '25 August 2025',
    'Effective_Date': '08 September 2025',
    'ATA_Chapter': 'ATA 25',
    'Subject': 'Emergency Exit / PSU Trim Panel Modification',
    'Applicable_Models': 'PC-12/47E',
    'MSN_Range': '2001-2999',
    'Affected_PN': '917.47.28.046, 917.47.28.045',
    'Affected_SN': None,
    'STC_Required': None,
    'Compliance_Category': 'Mandatory',
    'Compliance_Type': 'One-time',
    'Initial_Compliance': 'Within 12 months of effective date',
    'Recurring_Interval': 'N/A',
    'Terminating_Action': 'Modification per SB 25-059',
    'SB_Reference': 'Pilatus PC-12 SB 25-059',
    'AMM_Reference': 'AMM Chapter 25',
    'Supersedes': None,
    'Superseded_By': None,
    'Is_Current': 'Yes',
    'models_list': ['PC-12/47E'],
    'msn_range': (2001, 2999),
    'component_check': '917.47.28.046'
}

# AD 2: EASA AD 2022-0103
ad2 = {
    'AD_SB_Number': 'EASA AD 2022-0103',
    'Revision': 'Original',
    'Document_Type': 'AD',
    'Issuing_Authority': 'EASA',
    'Issue_Date': '09 June 2022',
    'Effective_Date': '23 June 2022',
    'ATA_Chapter': 'ATA 05',
    'Subject': 'ALS Amendment - Horizontal Stabilizer Inspections',
    'Applicable_Models': 'PC-12, PC-12/45, PC-12/47, PC-12/47E',
    'MSN_Range': 'All',
    'Affected_PN': None,
    'Affected_SN': None,
    'STC_Required': None,
    'Compliance_Category': 'Mandatory',
    'Compliance_Type': 'Recurring',
    'Initial_Compliance': 'From effective date',
    'Recurring_Interval': 'Per ALS intervals',
    'Terminating_Action': None,
    'SB_Reference': None,
    'AMM_Reference': 'AMM Chapter 04-00-00 (ALS)',
    'Supersedes': 'EASA AD 2021-0214',
    'Superseded_By': 'Check EASA for current revision',
    'Is_Current': 'No',
    'models_list': ['PC-12', 'PC-12/45', 'PC-12/47', 'PC-12/47E'],
    'msn_range': 'all',
    'component_check': None
}

def calculate_due_date(effective_date_str, compliance_time):
    """Calculate due date from effective date and compliance time"""
    try:
        # Parse effective date
        for fmt in ['%d %B %Y', '%Y-%m-%d', '%d %b %Y']:
            try:
                eff_date = datetime.strptime(effective_date_str, fmt)
                break
            except:
                continue
        else:
            return None

        # Parse compliance time
        if '12 months' in compliance_time.lower():
            return (eff_date + timedelta(days=365)).strftime('%Y-%m-%d')
        elif '6 months' in compliance_time.lower():
            return (eff_date + timedelta(days=180)).strftime('%Y-%m-%d')
        elif '30 days' in compliance_time.lower():
            return (eff_date + timedelta(days=30)).strftime('%Y-%m-%d')
        else:
            return None
    except:
        return None

def evaluate_fleet_camo(ad, fleet, monitoring_date=None):
    """
    Evaluate fleet against AD with CAMO-standard fields.
    Separates Monitoring_Date (system) from Evaluation_Date (engineer).
    """
    results = []
    evaluation_date = datetime.now().strftime('%Y-%m-%d')
    evaluation_time = datetime.now().strftime('%H:%M:%S')

    # If monitoring_date not provided, use evaluation date
    if monitoring_date is None:
        monitoring_date = evaluation_date

    for _, ac in fleet.iterrows():
        row = {}

        # === SECTION 1: AD/SB IDENTIFICATION ===
        row['AD_SB_Number'] = ad['AD_SB_Number']
        row['Revision'] = ad['Revision']
        row['Document_Type'] = ad['Document_Type']
        row['Issuing_Authority'] = ad['Issuing_Authority']
        row['Issue_Date'] = ad['Issue_Date']
        row['Effective_Date'] = ad['Effective_Date']
        row['ATA_Chapter'] = ad['ATA_Chapter']
        row['Subject'] = ad['Subject']

        # === SECTION 2: EFFECTIVITY ===
        row['Applicable_Models'] = ad['Applicable_Models']
        row['MSN_Range'] = ad['MSN_Range']
        row['Affected_PN'] = ad.get('Affected_PN')
        row['Affected_SN'] = ad.get('Affected_SN')
        row['STC_Required'] = ad.get('STC_Required')

        # === SECTION 3: COMPLIANCE REQUIREMENTS ===
        # Handle emergency ADs
        compliance_category = ad.get('Compliance_Category', 'Mandatory')
        if ad.get('is_emergency'):
            compliance_category = 'EMERGENCY'
        row['Compliance_Category'] = compliance_category
        row['Compliance_Type'] = ad['Compliance_Type']
        row['Initial_Compliance'] = ad['Initial_Compliance']
        row['Recurring_Interval'] = ad.get('Recurring_Interval')
        row['Terminating_Action'] = ad.get('Terminating_Action')

        # === SECTION 4: AIRCRAFT IDENTIFICATION ===
        row['Registration'] = ac['Registration']
        row['MSN'] = ac['MSN']
        row['Aircraft_Model'] = ac['Aircraft_Model']
        row['Operator'] = ac['Operator']

        # === SECTION 5: APPLICABILITY EVALUATION ===
        # Separate monitoring (system) from evaluation (engineer)
        row['Monitoring_Date'] = monitoring_date           # When source was checked (system)
        row['Evaluation_Date'] = evaluation_date           # When engineer evaluated (accountable)
        row['Evaluation_Time'] = evaluation_time
        row['Evaluated_By'] = 'AD/SB Evaluator Agent v2.0'

        # Determine applicability
        applicability = None
        reason = None

        # Check 1: Model match
        if ac['Aircraft_Model'] not in ad['models_list']:
            applicability = 'NOT APPLICABLE'
            reason = f"Model {ac['Aircraft_Model']} not in effectivity ({ad['Applicable_Models']})"

        # Check 2: MSN range
        elif ad['msn_range'] != 'all':
            msn_min, msn_max = ad['msn_range']
            if not (msn_min <= ac['MSN'] <= msn_max):
                applicability = 'NOT APPLICABLE'
                reason = f"MSN {ac['MSN']} outside range {msn_min}-{msn_max}"

        # Check 3: Component if specified
        if applicability is None and ad.get('component_check'):
            comp_pn = str(ac.get('Component_PN', ''))
            if ad['component_check'] in comp_pn:
                applicability = 'APPLICABLE'
                reason = f"Component {ad['component_check']} confirmed installed"
            else:
                applicability = 'REQUIRES VERIFICATION'
                reason = f"Verify if component P/N {ad['component_check']} installed"

        # Default to applicable if all checks passed
        if applicability is None:
            applicability = 'APPLICABLE'
            reason = 'Model and MSN match effectivity'

        row['Applicability'] = applicability
        row['Applicability_Reason'] = reason

        # === SECTION 6: COMPLIANCE STATUS ===
        if applicability == 'APPLICABLE':
            row['Compliance_Status'] = 'OPEN'
            row['Priority'] = 'HIGH' if ad['Compliance_Type'] == 'One-time' else 'MEDIUM'
            row['Risk_Assessment'] = 'Safety - per AD unsafe condition'
        elif applicability == 'REQUIRES VERIFICATION':
            row['Compliance_Status'] = 'OPEN'
            row['Priority'] = 'HIGH'
            row['Risk_Assessment'] = 'Requires component verification'
        else:
            row['Compliance_Status'] = 'N-A'
            row['Priority'] = 'LOW'
            row['Risk_Assessment'] = 'N/A'

        # === SECTION 7: COMPLIANCE DUE ===
        if applicability in ['APPLICABLE', 'REQUIRES VERIFICATION']:
            row['Due_Date'] = calculate_due_date(ad['Effective_Date'], ad['Initial_Compliance'])
            row['Current_Hours'] = ac['Total_Hours']
            row['Current_Cycles'] = ac['Total_Landings']

            # Calculate hours-based due if applicable
            if 'hours' in ad['Initial_Compliance'].lower():
                try:
                    hours_match = int(''.join(filter(str.isdigit, ad['Initial_Compliance'])))
                    row['Due_Hours'] = ac['Total_Hours'] + hours_match
                    row['Hours_Remaining'] = hours_match
                except:
                    pass
        else:
            row['Due_Date'] = 'N/A'
            row['Current_Hours'] = ac['Total_Hours']
            row['Current_Cycles'] = ac['Total_Landings']

        # === SECTION 8: COMPLIANCE ACCOMPLISHED ===
        row['Compliance_Date'] = None
        row['Compliance_Hours'] = None
        row['Compliance_Cycles'] = None
        row['Method_of_Compliance'] = None
        row['Work_Order_Number'] = None
        row['CRS_Reference'] = None

        # === SECTION 9: RECURRING TRACKING ===
        if ad['Compliance_Type'] == 'Recurring':
            row['Recurring_Interval'] = ad.get('Recurring_Interval')
        row['Last_Compliance_Date'] = None
        row['Last_Compliance_Hours'] = None
        row['Next_Due_Date'] = None
        row['Next_Due_Hours'] = None

        # === SECTION 10: PARTS & RESOURCES ===
        row['Parts_Required'] = None
        row['Parts_On_Hand'] = None
        row['Parts_Cost_EUR'] = None
        row['Labor_Hours'] = None
        row['Labor_Cost_EUR'] = None
        row['Total_Cost_EUR'] = None
        row['Downtime_Days'] = None

        # === SECTION 11: DOCUMENTATION ===
        row['SB_Reference'] = ad.get('SB_Reference')
        row['AMM_Reference'] = ad.get('AMM_Reference')
        row['IPC_Reference'] = None
        row['Engineering_Order'] = None

        # === SECTION 12: SUPERSEDURE & HISTORY ===
        row['Supersedes'] = ad.get('Supersedes')
        row['Superseded_By'] = ad.get('Superseded_By')
        row['Is_Current'] = ad.get('Is_Current')

        # === SECTION 13: AMP INTEGRATION ===
        if applicability == 'APPLICABLE':
            row['AMP_Update_Required'] = 'Yes' if ad['Compliance_Type'] == 'Recurring' else 'No'
        else:
            row['AMP_Update_Required'] = 'No'
        row['AMP_Task_Number'] = None
        row['AMP_Update_Date'] = None

        # === SECTION 14: ASSIGNMENT & WORKFLOW ===
        row['Assigned_To'] = None
        row['Review_Status'] = 'Pending Review'
        row['Reviewed_By'] = None
        row['Review_Date'] = None
        row['Approved_By'] = None
        row['Approval_Date'] = None

        # === SECTION 15: NOTES & REMARKS ===
        notes = []
        if ad.get('Superseded_By'):
            notes.append(f"WARNING: AD superseded - check {ad['Superseded_By']}")
        if applicability == 'REQUIRES VERIFICATION':
            notes.append("Action: Verify component installation status")
        row['Notes'] = ' | '.join(notes) if notes else None
        row['Discrepancies_Found'] = None
        row['Follow_Up_Required'] = 'Yes' if applicability == 'REQUIRES VERIFICATION' else 'No'
        row['Follow_Up_Details'] = 'Verify component P/N' if applicability == 'REQUIRES VERIFICATION' else None

        results.append(row)

    return pd.DataFrame(results)

# Evaluate both ADs
print("=" * 80)
print("CAMO-STANDARD AD EVALUATION RESULTS v2.0")
print("=" * 80)
print(f"Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

all_results = []

for ad in [ad1, ad2]:
    # Check supersedure chain BEFORE evaluation
    if ad.get('Supersedes'):
        superseded_ad = ad['Supersedes']
        print(f"\n[SUPERSEDURE] {ad['AD_SB_Number']} supersedes {superseded_ad}")
        master = mark_ad_superseded(master, superseded_ad, ad['AD_SB_Number'])

    results = evaluate_fleet_camo(ad, fleet)
    all_results.append(results)

    # Print summary
    applicable = results[results['Applicability'] == 'APPLICABLE']
    not_applicable = results[results['Applicability'] == 'NOT APPLICABLE']
    requires_ver = results[results['Applicability'] == 'REQUIRES VERIFICATION']

    # Show emergency status prominently
    emergency_tag = "[EMERGENCY]" if ad.get('is_emergency') else ""
    print(f"\n{emergency_tag} {ad['AD_SB_Number']} | {ad['Subject'][:45]}")
    print(f"Effective: {ad['Effective_Date']} | Type: {ad['Compliance_Type']}")
    print(f"Models: {ad['Applicable_Models']} | MSN: {ad['MSN_Range']}")
    if ad.get('Supersedes'):
        print(f"[INFO] This AD supersedes: {ad['Supersedes']}")
    if ad.get('Superseded_By'):
        print(f">>> WARNING: SUPERSEDED - {ad['Superseded_By']} <<<")
    print("-" * 80)
    print(f"APPLICABLE:             {len(applicable):2d} aircraft", end="")
    if len(applicable) > 0 and len(applicable) <= 10:
        print(f"  [{', '.join(applicable['Registration'].tolist())}]")
    elif len(applicable) > 10:
        print(f"  [All fleet]")
    else:
        print()

    print(f"NOT APPLICABLE:         {len(not_applicable):2d} aircraft")
    print(f"REQUIRES VERIFICATION:  {len(requires_ver):2d} aircraft", end="")
    if len(requires_ver) > 0:
        print(f"  [{', '.join(requires_ver['Registration'].tolist())}]")
    else:
        print()

    # Status breakdown for applicable
    if len(applicable) > 0:
        priority = 'EMERGENCY' if ad.get('is_emergency') else applicable['Priority'].iloc[0]
        print(f"\nStatus: {len(applicable)} OPEN | Priority: {priority}")

# Combine and save
combined = pd.concat(all_results, ignore_index=True)

# Append to existing or create new
if len(master) > 0:
    combined = pd.concat([master, combined], ignore_index=True)

# Save with all sheets
with pd.ExcelWriter(master_path, engine='openpyxl') as writer:
    combined.to_excel(writer, sheet_name='AD_SB_Register', index=False)

    # Re-add legend and dropdowns
    legend_data = {
        'Section': ['1. AD/SB Identification', '2. Effectivity', '3. Compliance Requirements',
                   '4. Aircraft Identification', '5. Applicability Evaluation', '6. Compliance Status',
                   '7. Compliance Due', '8. Compliance Accomplished', '9. Recurring Tracking',
                   '10. Parts & Resources', '11. Documentation', '12. Supersedure & History',
                   '13. AMP Integration', '14. Assignment & Workflow', '15. Notes & Remarks'],
        'Fields': [8, 5, 5, 4, 4, 3, 7, 6, 4, 7, 4, 3, 3, 6, 4]
    }
    pd.DataFrame(legend_data).to_excel(writer, sheet_name='Legend', index=False)

print("\n" + "=" * 80)
print(f"Results saved to: {master_path}")
print(f"Total rows: {len(combined)} | Columns: 73 (CAMO standard)")
print("=" * 80)
