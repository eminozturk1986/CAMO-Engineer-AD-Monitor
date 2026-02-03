import pandas as pd
from datetime import datetime, timedelta

# Load fleet database
fleet_path = "C:/Users/delye/.claude/skills/aviation-engineer-agent/Fleet_Database_Expanded.xlsx"
fleet = pd.read_excel(fleet_path)

# Load existing CAMO master
master_path = "C:/Users/delye/.claude/skills/aviation-engineer-agent/AD_Evaluation_Master_CAMO.xlsx"
try:
    master = pd.read_excel(master_path, sheet_name='AD_SB_Register')
except:
    master = pd.DataFrame()

# AD 1: EASA AD 2021-0110-CN (Cancellation Notice)
ad1 = {
    'AD_SB_Number': 'EASA AD 2021-0110-CN',
    'Revision': 'Cancellation Notice',
    'Document_Type': 'AD-CN',
    'Issuing_Authority': 'EASA',
    'Issue_Date': '03 November 2021',
    'Effective_Date': '03 November 2021',
    'ATA_Chapter': 'ATA 32',
    'Subject': 'CANCELLED: NLG Fork Assembly - Inspection/Replacement',
    'Applicable_Models': 'PC-12, PC-12/45, PC-12/47, PC-12/47E',
    'MSN_Range': 'All',
    'Affected_PN': '532.20.12.112, 532.20.12.044, 532.20.12.145',
    'Affected_SN': 'Per SB 32-029 section 1.A',
    'STC_Required': None,
    'Compliance_Category': 'Cancelled',
    'Compliance_Type': 'Cancelled',
    'Initial_Compliance': 'None - AD Cancelled',
    'Recurring_Interval': 'N/A',
    'Terminating_Action': 'AD 2021-0110 cancelled - no unsafe condition',
    'SB_Reference': 'Pilatus SB 32-029 Rev 1',
    'AMM_Reference': None,
    'Supersedes': None,
    'Superseded_By': None,
    'Is_Current': 'Yes',
    'Cancels': 'EASA AD 2021-0110',
    'models_list': ['PC-12', 'PC-12/45', 'PC-12/47', 'PC-12/47E'],
    'msn_range': 'all',
    'component_check': None
}

# AD 2: EASA AD 2016-0083 (SUPERSEDED)
ad2 = {
    'AD_SB_Number': 'EASA AD 2016-0083',
    'Revision': 'Original',
    'Document_Type': 'AD',
    'Issuing_Authority': 'EASA',
    'Issue_Date': '28 April 2016',
    'Effective_Date': '12 May 2016',
    'ATA_Chapter': 'ATA 04',
    'Subject': 'ALS Amendment - MLG Bolt Inspections',
    'Applicable_Models': 'PC-12, PC-12/45, PC-12/47, PC-12/47E',
    'MSN_Range': 'All',
    'Affected_PN': None,
    'Affected_SN': None,
    'STC_Required': None,
    'Compliance_Category': 'Mandatory',
    'Compliance_Type': 'Recurring',
    'Initial_Compliance': 'From effective date per ALS',
    'Recurring_Interval': '6-year and 10-year MLG bolt inspections, annual shock absorber bolt inspection',
    'Terminating_Action': None,
    'SB_Reference': 'Pilatus SL 186',
    'AMM_Reference': 'AMM report 02049 issue 31, AMM report 02300 issue 14',
    'Supersedes': 'EASA AD 2014-0170',
    'Superseded_By': 'Check EASA for current ALS AD (likely 2022-0103 or later)',
    'Is_Current': 'No',
    'models_list': ['PC-12', 'PC-12/45', 'PC-12/47', 'PC-12/47E'],
    'msn_range': 'all',
    'component_check': None
}

def evaluate_fleet_camo(ad, fleet):
    """Evaluate fleet against AD with CAMO-standard fields"""
    results = []
    today = datetime.now().strftime('%Y-%m-%d')

    for _, ac in fleet.iterrows():
        row = {}

        # Section 1: AD/SB Identification
        row['AD_SB_Number'] = ad['AD_SB_Number']
        row['Revision'] = ad['Revision']
        row['Document_Type'] = ad['Document_Type']
        row['Issuing_Authority'] = ad['Issuing_Authority']
        row['Issue_Date'] = ad['Issue_Date']
        row['Effective_Date'] = ad['Effective_Date']
        row['ATA_Chapter'] = ad['ATA_Chapter']
        row['Subject'] = ad['Subject']

        # Section 2: Effectivity
        row['Applicable_Models'] = ad['Applicable_Models']
        row['MSN_Range'] = ad['MSN_Range']
        row['Affected_PN'] = ad.get('Affected_PN')
        row['Affected_SN'] = ad.get('Affected_SN')
        row['STC_Required'] = ad.get('STC_Required')

        # Section 3: Compliance Requirements
        row['Compliance_Category'] = ad['Compliance_Category']
        row['Compliance_Type'] = ad['Compliance_Type']
        row['Initial_Compliance'] = ad['Initial_Compliance']
        row['Recurring_Interval'] = ad.get('Recurring_Interval')
        row['Terminating_Action'] = ad.get('Terminating_Action')

        # Section 4: Aircraft Identification
        row['Registration'] = ac['Registration']
        row['MSN'] = ac['MSN']
        row['Aircraft_Model'] = ac['Aircraft_Model']
        row['Operator'] = ac['Operator']

        # Section 5: Applicability Evaluation
        row['Evaluation_Date'] = today
        row['Evaluated_By'] = 'AD/SB Evaluator Agent v3.0'

        # Special handling for Cancellation Notice
        if ad['Document_Type'] == 'AD-CN':
            applicability = 'CANCELLED'
            reason = f"AD {ad.get('Cancels', 'unknown')} cancelled - no action required"
            row['Applicability'] = applicability
            row['Applicability_Reason'] = reason
            row['Compliance_Status'] = 'TERMINATED'
            row['Priority'] = 'LOW'
            row['Risk_Assessment'] = 'No unsafe condition - AD cancelled'
            row['Due_Date'] = 'N/A'
            row['Notes'] = f"Cancellation Notice: {ad.get('Cancels')} no longer required. Reason: No unsafe condition exists."
        else:
            # Standard evaluation logic
            applicability = None
            reason = None

            # Check 1: Model match
            if ac['Aircraft_Model'] not in ad['models_list']:
                applicability = 'NOT APPLICABLE'
                reason = f"Model {ac['Aircraft_Model']} not in effectivity"
            # Check 2: MSN range
            elif ad['msn_range'] != 'all':
                msn_min, msn_max = ad['msn_range']
                if not (msn_min <= ac['MSN'] <= msn_max):
                    applicability = 'NOT APPLICABLE'
                    reason = f"MSN {ac['MSN']} outside range"
            # Check 3: Component if specified
            if applicability is None and ad.get('component_check'):
                comp_pn = str(ac.get('Component_PN', ''))
                if ad['component_check'] in comp_pn:
                    applicability = 'APPLICABLE'
                    reason = f"Component confirmed"
                else:
                    applicability = 'REQUIRES VERIFICATION'
                    reason = f"Verify component installation"

            if applicability is None:
                applicability = 'APPLICABLE'
                reason = 'Model and MSN match'

            row['Applicability'] = applicability
            row['Applicability_Reason'] = reason

            # Section 6: Compliance Status
            if applicability == 'APPLICABLE':
                row['Compliance_Status'] = 'OPEN'
                row['Priority'] = 'MEDIUM' if ad['Compliance_Type'] == 'Recurring' else 'HIGH'
                row['Risk_Assessment'] = 'Per AD unsafe condition'
            else:
                row['Compliance_Status'] = 'N-A'
                row['Priority'] = 'LOW'
                row['Risk_Assessment'] = 'N/A'

            # Section 7: Due dates
            row['Due_Date'] = 'Per ALS intervals' if ad['Compliance_Type'] == 'Recurring' else 'N/A'

            # Notes
            notes = []
            if ad.get('Superseded_By'):
                notes.append(f"SUPERSEDED - check {ad['Superseded_By']}")
            row['Notes'] = ' | '.join(notes) if notes else None

        # Common fields
        row['Current_Hours'] = ac['Total_Hours']
        row['Current_Cycles'] = ac['Total_Landings']
        row['SB_Reference'] = ad.get('SB_Reference')
        row['AMM_Reference'] = ad.get('AMM_Reference')
        row['Supersedes'] = ad.get('Supersedes')
        row['Superseded_By'] = ad.get('Superseded_By')
        row['Is_Current'] = ad.get('Is_Current')
        row['AMP_Update_Required'] = 'No' if ad['Document_Type'] == 'AD-CN' else ('Yes' if ad['Compliance_Type'] == 'Recurring' and applicability == 'APPLICABLE' else 'No')
        row['Review_Status'] = 'Pending Review'
        row['Follow_Up_Required'] = 'No'

        results.append(row)

    return pd.DataFrame(results)

# Evaluate both ADs
print("=" * 80)
print("CAMO-STANDARD AD EVALUATION RESULTS")
print("=" * 80)

all_results = []

for ad in [ad1, ad2]:
    results = evaluate_fleet_camo(ad, fleet)
    all_results.append(results)

    # Count by applicability
    if ad['Document_Type'] == 'AD-CN':
        cancelled = len(results)
        print(f"\n{ad['AD_SB_Number']} | {ad['Subject'][:40]}")
        print(f"Type: CANCELLATION NOTICE | Cancels: {ad.get('Cancels', 'N/A')}")
        print(f"Models: {ad['Applicable_Models']} | MSN: {ad['MSN_Range']}")
        print("-" * 80)
        print(f"CANCELLED/TERMINATED:  {cancelled:2d} aircraft [All fleet - NO ACTION REQUIRED]")
        print(f"\nStatus: All TERMINATED | No compliance action needed")
    else:
        applicable = results[results['Applicability'] == 'APPLICABLE']
        not_applicable = results[results['Applicability'] == 'NOT APPLICABLE']
        requires_ver = results[results['Applicability'] == 'REQUIRES VERIFICATION']

        print(f"\n{ad['AD_SB_Number']} | {ad['Subject'][:40]}")
        print(f"Type: {ad['Compliance_Type']} | Effective: {ad['Effective_Date']}")
        print(f"Models: {ad['Applicable_Models']} | MSN: {ad['MSN_Range']}")
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
        print(f"REQUIRES VERIFICATION:  {len(requires_ver):2d} aircraft")
        if len(applicable) > 0:
            print(f"\nStatus: {len(applicable)} OPEN | Priority: {applicable['Priority'].iloc[0]}")

# Combine and save
combined = pd.concat(all_results, ignore_index=True)

if len(master) > 0:
    combined = pd.concat([master, combined], ignore_index=True)

with pd.ExcelWriter(master_path, engine='openpyxl') as writer:
    combined.to_excel(writer, sheet_name='AD_SB_Register', index=False)

print("\n" + "=" * 80)
print(f"Results saved to: {master_path}")
print(f"Total rows: {len(combined)} (added 40 new rows)")
print("=" * 80)
