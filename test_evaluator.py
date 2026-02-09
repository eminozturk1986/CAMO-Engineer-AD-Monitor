#!/usr/bin/env python3
"""
Test script for AD/SB Evaluator
Creates a sample AD and tests the evaluation system
"""

from ad_sb_evaluator import main
import tempfile
import os

# Create a sample AD text
sample_ad_text = """
AIRWORTHINESS DIRECTIVE 2026-01-TEST
Pilatus Aircraft Ltd.
Docket No. FAA-2026-0001

Federal Aviation Administration (FAA), Department of Transportation (DOT).
Final rule.

SUMMARY:
This airworthiness directive (AD) is prompted by reports of nose landing gear 
drag link failures. This AD requires inspection of the nose landing gear drag link 
for cracks and replacement if necessary.

APPLICABILITY:
This AD applies to Pilatus Aircraft Ltd. Model PC-12/47 airplanes, manufacturer 
serial numbers (MSN) 1200 through 1300, certificated in any category.

SUBJECT:
Nose Landing Gear Drag Link Inspection

COMPLIANCE:
Required within 100 hours time-in-service (TIS) after the effective date of this AD.

Repeat inspection every 100 hours TIS thereafter.

REQUIRED ACTIONS:
(a) Within 100 hours TIS after the effective date of this AD, inspect the nose 
landing gear drag link part number 532.20.12.289 for cracks using visual and 
dye penetrant inspection methods.

(b) If any cracks are found, before further flight, replace the drag link with 
an airworthy component.

(c) Repeat the inspection required by paragraph (a) every 100 hours TIS.

This is a recurring airworthiness limitation and must be incorporated into the 
Aircraft Maintenance Program (AMP).
"""

def create_sample_ad_pdf():
    """Create a simple text file as sample AD (PDF extraction would work similarly)"""
    fd, path = tempfile.mkstemp(suffix='.txt', prefix='TEST_AD_')
    with os.fdopen(fd, 'w') as f:
        f.write(sample_ad_text)
    return path

def test_evaluation():
    """Run test evaluation"""
    print("="*70)
    print("TESTING AD/SB EVALUATOR")
    print("="*70)
    
    # Create sample AD
    print("\n1. Creating sample AD...")
    ad_path = create_sample_ad_pdf()
    print(f"   Created: {ad_path}")
    
    # Path to fleet database
    fleet_db_path = '/mnt/skills/user/aviation-engineer-agent/Fleet_Database_SkyTech.xlsx'
    
    # Check if fleet database exists
    if not os.path.exists(fleet_db_path):
        print(f"\nERROR: Fleet database not found at {fleet_db_path}")
        print("Please ensure Fleet_Database_SkyTech.xlsx is in the skill directory")
        return
    
    print(f"\n2. Loading fleet database...")
    print(f"   Path: {fleet_db_path}")
    
    # Run evaluation
    print(f"\n3. Running evaluation...")
    output_path = main(ad_path, fleet_db_path)
    
    # Cleanup
    os.unlink(ad_path)
    
    if output_path:
        print(f"\n{'='*70}")
        print(f"TEST COMPLETED SUCCESSFULLY")
        print(f"{'='*70}")
        print(f"\nEvaluation report: {output_path}")
        print("\nExpected Result:")
        print("  - N847ST (MSN 1247): APPLICABLE")
        print("  - Compliance deadline: 3950 hours")
        print("  - AMP Update Required: Yes (recurring inspection)")
    else:
        print("\nTEST FAILED - See errors above")

if __name__ == "__main__":
    test_evaluation()
