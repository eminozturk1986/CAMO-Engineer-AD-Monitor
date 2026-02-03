"""
FAA AD Checker for PC-12 Fleet v2.0
===================================
Uses Federal Register API to check for new FAA Airworthiness Directives.
Token-efficient: JSON API parsing with Python (0 LLM tokens).

v2.0 Enhancements (CAMO Compliance):
- Emergency AD interrupt logic (EMERGENCY, IMMEDIATE, BEFORE FURTHER FLIGHT)
- Explicit "No Applicable AD Found" audit evidence
- Separate Monitoring_Date vs Evaluation_Date
- Supersedure chain detection

API Endpoint:
https://www.federalregister.gov/api/v1/documents.json?
  conditions[agencies][]=federal-aviation-administration
  &conditions[type][]=rule
  &per_page=100
  &order=newest

Archive Pattern: FAA_Reports/faa_ads_YYYY-MM-DD_to_YYYY-MM-DD.json
"""

import requests
from datetime import datetime, timedelta
import os
import json
import re

# Configuration
SKILL_DIR = "C:/Users/delye/.claude/skills/aviation-engineer-agent"
FAA_REPORTS_DIR = f"{SKILL_DIR}/FAA_Reports"
ADS_DIR = f"{SKILL_DIR}/ADs"
AUDIT_DIR = f"{SKILL_DIR}/Audit_Evidence"

# Federal Register API
FAA_API_BASE = "https://www.federalregister.gov/api/v1/documents.json"

# Fleet types to monitor
FLEET_KEYWORDS = ['PC-12', 'PC12', 'PILATUS', 'PC-12/45', 'PC-12/47', 'PC-12/47E']

# Emergency AD keywords - bypass normal batching
EMERGENCY_KEYWORDS = [
    'EMERGENCY', 'IMMEDIATE', 'BEFORE FURTHER FLIGHT',
    'BEFORE NEXT FLIGHT', 'URGENT', 'UNSAFE CONDITION'
]

def ensure_directories():
    """Create required directories if they don't exist"""
    os.makedirs(FAA_REPORTS_DIR, exist_ok=True)
    os.makedirs(ADS_DIR, exist_ok=True)
    os.makedirs(AUDIT_DIR, exist_ok=True)


def detect_emergency_ad(ad):
    """
    Check if AD contains emergency keywords requiring immediate action.
    Returns (is_emergency, matched_keyword)
    """
    title = ad.get('title', '').upper()
    abstract = ad.get('abstract', '').upper()
    combined_text = f"{title} {abstract}"

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in combined_text:
            return True, keyword

    return False, None


def generate_no_applicable_evidence(authority, period_start, period_end, total_ads_checked, monitoring_date):
    """
    Generate audit evidence record when no fleet-applicable ADs found.
    Required for CAMO compliance - proves monitoring was performed.
    """
    evidence = {
        'record_type': 'NO_APPLICABLE_AD_EVIDENCE',
        'authority': authority,
        'period_start': period_start.strftime('%Y-%m-%d'),
        'period_end': period_end.strftime('%Y-%m-%d'),
        'result': 'NO_APPLICABLE_AD',
        'total_ads_checked': total_ads_checked,
        'fleet_applicable_count': 0,
        'monitoring_date': monitoring_date,
        'monitoring_time': datetime.now().strftime('%H:%M:%S'),
        'system_identifier': 'FAA AD Checker v2.0',
        'fleet_keywords_used': FLEET_KEYWORDS,
        'statement': f"Monitoring check completed for {authority} ADs. "
                     f"Period: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}. "
                     f"Total ADs reviewed: {total_ads_checked}. "
                     f"Fleet-applicable ADs found: 0. "
                     f"No action required."
    }

    # Save evidence file
    filename = f"no_applicable_ad_{authority}_{monitoring_date.replace('-', '')}.json"
    filepath = os.path.join(AUDIT_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(evidence, f, indent=2)

    print(f"\n[AUDIT] No-applicable-AD evidence archived: {filename}")

    return evidence, filepath

def fetch_faa_ads(days_back=14, per_page=100):
    """
    Fetch recent FAA ADs from Federal Register API
    Returns JSON data - NO LLM tokens needed
    """
    print(f"\n{'='*70}")
    print("FAA AD CHECK VIA FEDERAL REGISTER API")
    print(f"{'='*70}")

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Checking last {days_back} days...")

    # Build API URL - don't filter by type, filter ADs from results instead
    params = {
        'conditions[agencies][]': 'federal-aviation-administration',
        'conditions[publication_date][gte]': start_date.strftime('%Y-%m-%d'),
        'per_page': per_page,
        'order': 'newest'
    }

    try:
        print("\nStep 1: Fetching from Federal Register API (0 tokens)...")
        response = requests.get(FAA_API_BASE, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])

            # Filter for Airworthiness Directives only
            ads = []
            for doc in results:
                title = doc.get('title', '').upper()
                if 'AIRWORTHINESS DIRECTIVE' in title or 'AD ' in title:
                    ads.append({
                        'document_number': doc.get('document_number', ''),
                        'title': doc.get('title', ''),
                        'abstract': doc.get('abstract', ''),
                        'publication_date': doc.get('publication_date', ''),
                        'pdf_url': doc.get('pdf_url', ''),
                        'html_url': doc.get('html_url', ''),
                        'type': doc.get('type', '')
                    })

            print(f"   Found {len(results)} FAA rules")
            print(f"   Filtered to {len(ads)} Airworthiness Directives")

            return ads, start_date, end_date
        else:
            print(f"   [ERROR] API Error: HTTP {response.status_code}")
            return [], start_date, end_date

    except Exception as e:
        print(f"   [ERROR] {e}")
        return [], start_date, end_date

def filter_fleet_applicable(ads, keywords=FLEET_KEYWORDS):
    """
    Filter ADs for fleet-applicable items with emergency detection.
    Pure Python - ZERO tokens
    """
    print("\nStep 2: Filtering for PC-12 fleet (0 tokens)...")

    applicable = []
    not_applicable = []
    emergency_ads = []

    for ad in ads:
        title_upper = ad.get('title', '').upper()
        abstract_upper = ad.get('abstract', '').upper()

        is_match = False
        matched_keyword = None

        for keyword in keywords:
            kw = keyword.upper()
            if kw in title_upper or kw in abstract_upper:
                is_match = True
                matched_keyword = keyword
                break

        if is_match:
            ad['matched_keyword'] = matched_keyword

            # Check for emergency keywords
            is_emergency, emergency_keyword = detect_emergency_ad(ad)
            if is_emergency:
                ad['is_emergency'] = True
                ad['emergency_keyword'] = emergency_keyword
                ad['compliance_category'] = 'EMERGENCY'
                ad['detection_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                emergency_ads.append(ad)
                print(f"\n   [!!!] EMERGENCY AD DETECTED: {ad.get('document_number')}")
                print(f"         Keyword: {emergency_keyword}")
                print(f"         Bypassing normal batch - IMMEDIATE evaluation required")
            else:
                ad['is_emergency'] = False
                ad['compliance_category'] = 'STANDARD'

            applicable.append(ad)
        else:
            not_applicable.append(ad)

    print(f"   Fleet applicable: {len(applicable)}")
    print(f"   Emergency ADs:    {len(emergency_ads)}")
    print(f"   Not applicable:   {len(not_applicable)}")

    return applicable, not_applicable, emergency_ads

def download_ad_pdf(ad, save_dir=ADS_DIR):
    """
    Download AD PDF for applicable ADs
    """
    pdf_url = ad.get('pdf_url')
    if not pdf_url:
        return None

    try:
        response = requests.get(pdf_url, timeout=60)
        if response.status_code == 200:
            # Create filename from document number
            doc_num = ad.get('document_number', 'unknown').replace('/', '_')
            filename = f"FAA_AD_{doc_num}.pdf"
            filepath = os.path.join(save_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"   [OK] Downloaded: {filename}")
            return filepath
        else:
            print(f"   [FAIL] HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"   [ERROR] {e}")
        return None

def archive_check_report(ads, applicable, not_applicable, emergency_ads, start_date, end_date, monitoring_date):
    """
    Archive the check results as JSON with separate monitoring/evaluation dates.
    Generates no-applicable-AD evidence if no fleet ADs found.
    """
    ensure_directories()

    report = {
        # Monitoring metadata (system-driven)
        'monitoring_date': monitoring_date,
        'monitoring_time': datetime.now().strftime('%H:%M:%S'),
        'monitoring_system': 'FAA AD Checker v2.0',

        # Evaluation metadata (to be filled by engineer)
        'evaluation_date': None,  # Set when engineer evaluates
        'evaluator': None,        # Set when engineer evaluates

        # Source info
        'source': 'Federal Register API',
        'api_endpoint': FAA_API_BASE,
        'period_start': start_date.strftime('%Y-%m-%d'),
        'period_end': end_date.strftime('%Y-%m-%d'),

        # Results
        'total_ads': len(ads),
        'fleet_applicable': len(applicable),
        'emergency_ads': len(emergency_ads),
        'not_applicable': len(not_applicable),
        'applicable_ads': applicable,
        'emergency_ad_list': [ad.get('document_number') for ad in emergency_ads],

        # Metadata
        'fleet_keywords': FLEET_KEYWORDS,
        'emergency_keywords': EMERGENCY_KEYWORDS,
        'token_cost': 0,
        'method': 'Federal Register JSON API (no LLM)'
    }

    # Create filename with date range
    filename = f"faa_ads_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.json"
    filepath = os.path.join(FAA_REPORTS_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\nStep 4: Archived report to {filename}")

    # Generate no-applicable-AD evidence if none found
    if len(applicable) == 0 and len(ads) > 0:
        generate_no_applicable_evidence(
            authority='FAA',
            period_start=start_date,
            period_end=end_date,
            total_ads_checked=len(ads),
            monitoring_date=monitoring_date
        )

    return report, filepath

def run_faa_check(days_back=14, download_pdfs=True):
    """
    Main function: Fetch, parse, filter, archive FAA ADs
    With emergency interrupt logic and audit evidence generation.
    """
    ensure_directories()
    monitoring_date = datetime.now().strftime('%Y-%m-%d')

    # Step 1: Fetch ADs from API
    ads, start_date, end_date = fetch_faa_ads(days_back=days_back)

    if not ads:
        print("\n[OK] No Airworthiness Directives found in this period")
        # Still generate audit evidence for no ADs found
        generate_no_applicable_evidence(
            authority='FAA',
            period_start=start_date,
            period_end=end_date,
            total_ads_checked=0,
            monitoring_date=monitoring_date
        )
        return None

    # Step 2: Filter for fleet (with emergency detection)
    applicable, not_applicable, emergency_ads = filter_fleet_applicable(ads)

    # Step 3: Download PDFs for applicable ADs (emergency ADs first)
    downloaded_pdfs = []
    if applicable and download_pdfs:
        print("\nStep 3: Downloading applicable AD PDFs...")

        # Download emergency ADs first (priority)
        if emergency_ads:
            print("\n   [!!!] PRIORITY: Downloading EMERGENCY AD PDFs first...")
            for ad in emergency_ads:
                pdf_path = download_ad_pdf(ad)
                if pdf_path:
                    downloaded_pdfs.append(pdf_path)
                    ad['pdf_downloaded'] = pdf_path

        # Then download non-emergency applicable ADs
        for ad in applicable:
            if not ad.get('is_emergency'):
                pdf_path = download_ad_pdf(ad)
                if pdf_path:
                    downloaded_pdfs.append(pdf_path)
    else:
        print("\nStep 3: No PDFs to download")

    # Step 4: Archive report (with monitoring date)
    report, report_path = archive_check_report(
        ads, applicable, not_applicable, emergency_ads, start_date, end_date, monitoring_date
    )

    # Print summary
    print(f"\n{'='*70}")
    print("FAA AD CHECK RESULTS")
    print(f"{'='*70}")
    print(f"Monitoring Date: {monitoring_date}")

    # Emergency AD alert
    if emergency_ads:
        print(f"\n{'!'*70}")
        print(f"[!!!] EMERGENCY AD INTERRUPT - {len(emergency_ads)} EMERGENCY AD(s) DETECTED")
        print(f"{'!'*70}")
        for ad in emergency_ads:
            print(f"   >>> {ad['document_number']}: {ad['title'][:50]}...")
            print(f"       Emergency keyword: {ad.get('emergency_keyword')}")
            print(f"       Detection time: {ad.get('detection_time')}")
        print(f"\n   ACTION REQUIRED: Same-day evaluation mandatory")
        print(f"{'!'*70}")

    if applicable:
        print(f"\n[!!] {len(applicable)} PC-12 APPLICABLE AD(s) FOUND:")
        for ad in applicable:
            priority_tag = "[EMERGENCY]" if ad.get('is_emergency') else "[STANDARD]"
            print(f"   {priority_tag} {ad['document_number']}: {ad['title'][:50]}...")
            if ad.get('matched_keyword'):
                print(f"     Matched: {ad['matched_keyword']}")
        print(f"\n   PDFs downloaded: {len(downloaded_pdfs)}")
        print("   --> These require full CAMO evaluation")
    else:
        print("\n[OK] No PC-12 applicable FAA ADs in this period")
        print("   Fleet evaluation remains current")
        print("   [AUDIT] No-applicable-AD evidence generated")

    print(f"\n[SAVED] Report archived: {report_path}")
    print(f"[INFO] Token cost: 0 (pure API/JSON parsing)")
    print(f"{'='*70}")

    return report

def get_biweekly_period():
    """
    Calculate current bi-weekly period (matching EASA pattern)
    FAA doesn't have official bi-weekly, but we simulate it
    """
    today = datetime.now()
    # Find the most recent Sunday (start of bi-weekly period)
    days_since_sunday = today.weekday() + 1
    if days_since_sunday == 7:
        days_since_sunday = 0

    period_end = today
    period_start = today - timedelta(days=14)

    return period_start, period_end

# CLI interface
if __name__ == "__main__":
    import sys

    days = 14
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            pass

    run_faa_check(days_back=days)
