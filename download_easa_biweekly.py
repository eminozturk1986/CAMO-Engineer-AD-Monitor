"""
EASA Bi-Weekly Report Downloader & Archiver
============================================
Downloads official EASA bi-weekly HTML reports and archives them.
Parses for PC-12 applicable ADs without burning tokens.

Report URL Pattern:
https://ad.easa.europa.eu/blob/easa_biweekly_[START]_[END]_[NUM]-[YEAR].html/biweekly

Example:
https://ad.easa.europa.eu/blob/easa_biweekly_2025-12-22_2026-01-04_01-2026.html/biweekly
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import re
import json

# Configuration
SKILL_DIR = "C:/Users/delye/.claude/skills/aviation-engineer-agent"
REPORTS_DIR = f"{SKILL_DIR}/EASA_Reports"
ADS_DIR = f"{SKILL_DIR}/ADs"

# Fleet types to monitor
FLEET_KEYWORDS = ['PC-12', 'PC12', 'PILATUS', 'PC-12/45', 'PC-12/47', 'PC-12/47E']

def download_biweekly_report(report_url, save_dir=REPORTS_DIR):
    """
    Download EASA bi-weekly HTML report and save locally
    """
    try:
        response = requests.get(report_url, timeout=30)
        if response.status_code == 200:
            # Extract filename from URL
            # Pattern: easa_biweekly_2025-12-22_2026-01-04_01-2026.html
            match = re.search(r'easa_biweekly_[\d-]+_[\d-]+_[\d]+-[\d]+\.html', report_url)
            if match:
                filename = match.group()
            else:
                filename = f"easa_biweekly_{datetime.now().strftime('%Y%m%d')}.html"

            filepath = os.path.join(save_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)

            print(f"✓ Downloaded: {filename}")
            return filepath, response.text
        else:
            print(f"✗ Failed to download: HTTP {response.status_code}")
            return None, None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None, None

def parse_biweekly_html(html_content):
    """
    Parse EASA bi-weekly HTML to extract AD list
    Returns structured data - NO LLM tokens needed
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    ads = []

    # Find table rows (skip header)
    rows = soup.find_all('tr')

    for row in rows[1:]:  # Skip header row
        cells = row.find_all('td')
        if len(cells) >= 5:
            ad = {
                'ad_number': cells[0].get_text(strip=True),
                'issue_date': cells[1].get_text(strip=True),
                'holder': cells[2].get_text(strip=True),
                'type': cells[3].get_text(strip=True),
                'subject': cells[4].get_text(strip=True) if len(cells) > 4 else ''
            }
            ads.append(ad)

    return ads

def filter_fleet_applicable(ads, keywords=FLEET_KEYWORDS):
    """
    Filter ADs for fleet-applicable items
    Pure Python - ZERO tokens
    """
    applicable = []
    not_applicable = []

    for ad in ads:
        holder_upper = ad.get('holder', '').upper()
        type_upper = ad.get('type', '').upper()
        subject_upper = ad.get('subject', '').upper()

        is_match = False
        for keyword in keywords:
            kw = keyword.upper()
            if kw in holder_upper or kw in type_upper or kw in subject_upper:
                is_match = True
                break

        if is_match:
            applicable.append(ad)
        else:
            not_applicable.append(ad)

    return applicable, not_applicable

def generate_check_report(report_url, filepath, ads, applicable, not_applicable):
    """
    Generate JSON summary report
    """
    # Extract period from URL
    period_match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})', report_url)
    if period_match:
        period_start = period_match.group(1)
        period_end = period_match.group(2)
    else:
        period_start = period_end = datetime.now().strftime('%Y-%m-%d')

    report = {
        'check_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'source_url': report_url,
        'archived_file': filepath,
        'period_start': period_start,
        'period_end': period_end,
        'total_ads': len(ads),
        'fleet_applicable': len(applicable),
        'not_applicable': len(not_applicable),
        'applicable_ads': applicable,
        'fleet_keywords': FLEET_KEYWORDS,
        'token_cost': 0,
        'method': 'HTML parsing (no LLM)'
    }

    # Save JSON report
    json_filename = f"check_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    json_path = os.path.join(REPORTS_DIR, json_filename)

    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)

    return report, json_path

def run_biweekly_check(report_url):
    """
    Main function: Download, parse, filter, report
    """
    print("=" * 70)
    print("EASA BI-WEEKLY REPORT CHECK")
    print("=" * 70)

    # Step 1: Download HTML
    print("\nStep 1: Downloading bi-weekly report...")
    filepath, html_content = download_biweekly_report(report_url)

    if not html_content:
        print("Failed to download report")
        return None

    # Step 2: Parse HTML (zero tokens)
    print("\nStep 2: Parsing HTML (0 tokens)...")
    ads = parse_biweekly_html(html_content)
    print(f"   Found {len(ads)} ADs in report")

    # Step 3: Filter for fleet (zero tokens)
    print("\nStep 3: Filtering for PC-12 fleet (0 tokens)...")
    applicable, not_applicable = filter_fleet_applicable(ads)
    print(f"   Fleet applicable: {len(applicable)}")
    print(f"   Not applicable:   {len(not_applicable)}")

    # Step 4: Generate report
    print("\nStep 4: Generating summary report...")
    report, json_path = generate_check_report(
        report_url, filepath, ads, applicable, not_applicable
    )

    # Print summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    if applicable:
        print(f"\n⚠️  {len(applicable)} PC-12 APPLICABLE AD(s) FOUND:")
        for ad in applicable:
            print(f"   • {ad['ad_number']}: {ad['subject'][:50]}...")
        print("\n   → These require full PDF evaluation")
    else:
        print("\n✓ No PC-12 applicable ADs in this period")
        print("   Fleet evaluation remains current")

    print(f"\n📁 Archived: {filepath}")
    print(f"📊 Report:   {json_path}")
    print(f"🎯 Token cost: 0 (pure HTML parsing)")
    print("=" * 70)

    return report

# Example usage
if __name__ == "__main__":
    url = "https://ad.easa.europa.eu/blob/easa_biweekly_2025-12-22_2026-01-04_01-2026.html/biweekly"
    run_biweekly_check(url)
