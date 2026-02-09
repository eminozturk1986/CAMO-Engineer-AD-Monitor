"""
AD/SB Evaluator - Main Implementation
This script evaluates Airworthiness Directives and Service Bulletins against a fleet database.
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import PyPDF2
import pdfplumber

class ADSBEvaluator:
    """Main class for evaluating AD/SB applicability against fleet."""
    
    def __init__(self, fleet_database_path: str):
        """Initialize with fleet database."""
        self.fleet_df = pd.read_excel(fleet_database_path)
        self.validate_fleet_database()
        
    def validate_fleet_database(self):
        """Validate that fleet database has required columns."""
        required_cols = ['Registration', 'MSN', 'Aircraft_Model', 'Total_Hours', 'Total_Landings']
        missing = [col for col in required_cols if col not in self.fleet_df.columns]
        if missing:
            raise ValueError(f"Fleet database missing required columns: {missing}")
    
    def extract_ad_info_from_pdf(self, pdf_path: str) -> Dict:
        """Extract key information from AD/SB PDF."""
        ad_info = {
            'document_number': '',
            'document_type': '',
            'issuing_authority': '',
            'subject': '',
            'models': [],
            'msn_ranges': [],
            'component_pns': [],
            'stc_list': [],
            'compliance_time': '',
            'compliance_type': '',  # hours, calendar, landings, immediate
            'required_actions': '',
            'is_recurring': False
        }
        
        text = self._extract_text_from_pdf(pdf_path)
        
        # Extract document number
        ad_info['document_number'] = self._extract_document_number(text)
        
        # Extract document type (AD vs SB)
        ad_info['document_type'] = self._extract_document_type(text)
        
        # Extract issuing authority
        ad_info['issuing_authority'] = self._extract_issuing_authority(text)
        
        # Extract subject
        ad_info['subject'] = self._extract_subject(text)
        
        # Extract applicability (models, MSN ranges)
        ad_info['models'], ad_info['msn_ranges'] = self._extract_applicability(text)
        
        # Extract component P/Ns if component-specific
        ad_info['component_pns'] = self._extract_component_pns(text)
        
        # Extract STC requirements
        ad_info['stc_list'] = self._extract_stc_requirements(text)
        
        # Extract compliance information
        ad_info['compliance_time'], ad_info['compliance_type'], ad_info['is_recurring'] = self._extract_compliance(text)
        
        # Extract required actions
        ad_info['required_actions'] = self._extract_required_actions(text)
        
        return ad_info
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using multiple methods."""
        text = ""
        
        # Check if it's a text file (for testing)
        if pdf_path.endswith('.txt'):
            with open(pdf_path, 'r') as f:
                return f.read()
        
        # Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            if text.strip():
                return text
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2...")
        
        # Fallback to PyPDF2
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PyPDF2 also failed: {e}")
            raise ValueError("Could not extract text from PDF. File may be scanned/image-based.")
        
        return text
    
    def _extract_document_number(self, text: str) -> str:
        """Extract AD/SB document number."""
        # Common patterns: AD 2021-24-01, 2008-02-03, SB 32-020
        patterns = [
            r'AD\s*(\d{4}-\d{2}-\d{2})',
            r'Amendment\s*(\d{2}-\d+)',
            r'Docket\s*No\.\s*FAA-(\d{4}-\d+)',
            r'Service\s*Bulletin\s*No[.:]?\s*([\w-]+)',
            r'SB\s*([\w-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "UNKNOWN"
    
    def _extract_document_type(self, text: str) -> str:
        """Determine if document is AD or SB."""
        text_lower = text.lower()
        if 'airworthiness directive' in text_lower or re.search(r'\bAD\b', text):
            return 'AD'
        elif 'service bulletin' in text_lower:
            return 'SB'
        return 'UNKNOWN'
    
    def _extract_issuing_authority(self, text: str) -> str:
        """Extract issuing authority (FAA, EASA, FOCA, etc.)."""
        authorities = ['FAA', 'EASA', 'FOCA', 'Federal Aviation Administration', 
                      'European Union Aviation Safety Agency', 'Federal Office for Civil Aviation']
        
        for auth in authorities:
            if auth in text:
                if 'FAA' in auth or 'Federal Aviation Administration' in auth:
                    return 'FAA'
                elif 'EASA' in auth or 'European' in auth:
                    return 'EASA'
                elif 'FOCA' in auth or 'Federal Office for Civil Aviation' in auth:
                    return 'FOCA'
        
        return 'UNKNOWN'
    
    def _extract_subject(self, text: str) -> str:
        """Extract subject/description."""
        # Look for subject line or first paragraph after applicability
        subject_match = re.search(r'SUBJECT[:\s]+(.+?)(?:\n\n|APPLICABILITY)', text, re.IGNORECASE | re.DOTALL)
        if subject_match:
            return subject_match.group(1).strip()[:200]  # Limit to 200 chars
        
        # Fallback: extract from summary
        summary_match = re.search(r'SUMMARY[:\s]+(.+?)(?:\n\n|DATES)', text, re.IGNORECASE | re.DOTALL)
        if summary_match:
            return summary_match.group(1).strip()[:200]
        
        return "Subject not found in PDF"
    
    def _extract_applicability(self, text: str) -> Tuple[List[str], List[Tuple[int, int]]]:
        """Extract aircraft models and MSN ranges."""
        models = []
        msn_ranges = []
        
        # Find applicability section
        applicability_section = re.search(
            r'(?:APPLICABILITY|This AD applies to)[:\s]+(.+?)(?:\n\n|COMPLIANCE|SUBJECT)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if not applicability_section:
            return models, msn_ranges
        
        app_text = applicability_section.group(1)
        
        # Extract models (e.g., PC-12/47, PC-12/45, PC-12 Series)
        model_patterns = [
            r'Model[s]?\s+([\w\-/]+(?:\s+and\s+[\w\-/]+)*)',
            r'(PC-12/\d+[A-Z]*)',
            r'(Falcon\s+\w+)',
            r'(Citation\s+\w+)'
        ]
        
        for pattern in model_patterns:
            matches = re.finditer(pattern, app_text, re.IGNORECASE)
            for match in matches:
                model = match.group(1).strip()
                if model and model not in models:
                    models.append(model)
        
        # Extract MSN ranges
        # Patterns: "MSN 101 through 749", "serial numbers 1200-1300", "S/N 101 through 544, and 546 through 888"
        msn_patterns = [
            r'(?:MSN|serial\s+number[s]?|S/N)\s+(\d+)\s+through\s+(\d+)',
            r'(?:MSN|serial\s+number[s]?|S/N)\s+(\d+)\s*-\s*(\d+)',
            r'manufacturer\s+serial\s+number[s]?\s+\(MSN[s]?\)\s+(\d+)\s+through\s+(\d+)'
        ]
        
        for pattern in msn_patterns:
            matches = re.finditer(pattern, app_text, re.IGNORECASE)
            for match in matches:
                start_msn = int(match.group(1))
                end_msn = int(match.group(2))
                msn_ranges.append((start_msn, end_msn))
        
        # Check for "all serial numbers"
        if re.search(r'all\s+serial\s+number[s]?', app_text, re.IGNORECASE):
            msn_ranges = [(0, 999999)]  # Special marker for "all"
        
        return models, msn_ranges
    
    def _extract_component_pns(self, text: str) -> List[str]:
        """Extract component part numbers if AD is component-specific."""
        component_pns = []
        
        # Look for P/N patterns
        pn_patterns = [
            r'[Pp]art\s+[Nn]umber\s+\(?P/N\)?\s*([\w\.-]+)',
            r'P/N\s*([\w\.-]+)',
            r'part\s+number[s]?\s+([\w\.-]+(?:\s+or\s+[\w\.-]+)*)'
        ]
        
        for pattern in pn_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                pn = match.group(1).strip()
                if pn and pn not in component_pns:
                    component_pns.append(pn)
        
        return component_pns[:10]  # Limit to first 10 P/Ns
    
    def _extract_stc_requirements(self, text: str) -> List[str]:
        """Extract STC requirements if AD is STC-specific."""
        stc_list = []
        
        # Look for STC patterns
        stc_pattern = r'(?:STC|Supplemental\s+Type\s+Certificate)\s+No\.\s*(SA\d+[A-Z]{2})'
        
        matches = re.finditer(stc_pattern, text, re.IGNORECASE)
        for match in matches:
            stc = match.group(1)
            if stc not in stc_list:
                stc_list.append(stc)
        
        return stc_list
    
    def _extract_compliance(self, text: str) -> Tuple[str, str, bool]:
        """Extract compliance time, type, and whether it's recurring."""
        compliance_time = ""
        compliance_type = ""
        is_recurring = False
        
        # Find compliance section
        compliance_section = re.search(
            r'(?:COMPLIANCE|Required)[:\s]+(.+?)(?:\n\n|REQUIRED\s+ACTIONS|$)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if not compliance_section:
            return "Not specified", "unknown", False
        
        comp_text = compliance_section.group(1)
        
        # Check for recurring
        if re.search(r'repetitively|recurring|repeat|periodic', comp_text, re.IGNORECASE):
            is_recurring = True
        
        # Extract time-based compliance (hours)
        hours_match = re.search(r'within\s+(\d+)\s+hours?\s+(?:time-in-service|TIS|flight\s+hours)', comp_text, re.IGNORECASE)
        if hours_match:
            compliance_time = hours_match.group(1) + " hours"
            compliance_type = "hours"
            return compliance_time, compliance_type, is_recurring
        
        # Extract calendar-based compliance (days)
        days_match = re.search(r'within\s+(\d+)\s+days?', comp_text, re.IGNORECASE)
        if days_match:
            compliance_time = days_match.group(1) + " days"
            compliance_type = "calendar"
            return compliance_time, compliance_type, is_recurring
        
        # Extract cycle-based compliance (landings)
        cycles_match = re.search(r'within\s+(\d+)\s+(?:landings?|cycles?)', comp_text, re.IGNORECASE)
        if cycles_match:
            compliance_time = cycles_match.group(1) + " landings"
            compliance_type = "landings"
            return compliance_time, compliance_type, is_recurring
        
        # Check for immediate compliance
        if re.search(r'before\s+(?:next\s+)?flight|immediate', comp_text, re.IGNORECASE):
            compliance_time = "Before next flight"
            compliance_type = "immediate"
            return compliance_time, compliance_type, is_recurring
        
        return "Not specified", "unknown", is_recurring
    
    def _extract_required_actions(self, text: str) -> str:
        """Extract required actions summary."""
        actions_section = re.search(
            r'(?:REQUIRED\s+ACTIONS?|Actions?)[:\s]+(.+?)(?:\n\n|ALTERNATIVE|$)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if actions_section:
            actions = actions_section.group(1).strip()
            # Limit to first 500 chars
            return actions[:500] + ("..." if len(actions) > 500 else "")
        
        return "Actions not clearly specified in PDF"
    
    def check_msn_in_range(self, msn: int, msn_ranges: List[Tuple[int, int]]) -> bool:
        """Check if MSN is within any of the specified ranges."""
        if not msn_ranges:
            return True  # If no range specified, assume all applicable
        
        for start, end in msn_ranges:
            if start <= msn <= end:
                return True
        return False
    
    def check_model_match(self, aircraft_model: str, ad_models: List[str]) -> bool:
        """Check if aircraft model matches AD applicability."""
        if not ad_models:
            return True  # If no model specified, assume all applicable
        
        aircraft_model_clean = aircraft_model.upper().replace(" ", "").replace("-", "")
        
        for ad_model in ad_models:
            ad_model_clean = ad_model.upper().replace(" ", "").replace("-", "")
            
            # Check for exact match
            if aircraft_model_clean == ad_model_clean:
                return True
            
            # Check for series match (e.g., "PC-12 Series" matches "PC-12/47")
            if "SERIES" in ad_model_clean:
                base_model = ad_model_clean.replace("SERIES", "").strip()
                if aircraft_model_clean.startswith(base_model):
                    return True
        
        return False
    
    def check_component_match(self, aircraft_components: str, ad_component_pns: List[str]) -> Optional[bool]:
        """Check if aircraft has the specified component P/N installed."""
        if not ad_component_pns:
            return None  # Not component-specific
        
        if pd.isna(aircraft_components) or not aircraft_components:
            return None  # Cannot verify - need manual check
        
        # Parse component P/Ns from aircraft (format: "NLG:532.20.12.289|MLG:532.30.14.125")
        aircraft_pn_list = []
        for comp in str(aircraft_components).split('|'):
            if ':' in comp:
                pn = comp.split(':')[1].strip()
                aircraft_pn_list.append(pn)
        
        # Check if any AD component P/N is installed
        for ad_pn in ad_component_pns:
            if ad_pn in aircraft_pn_list:
                return True
        
        return False
    
    def check_stc_match(self, aircraft_stcs: str, ad_stcs: List[str]) -> Optional[bool]:
        """Check if aircraft has required STC installed."""
        if not ad_stcs:
            return None  # Not STC-specific
        
        if pd.isna(aircraft_stcs) or not aircraft_stcs or aircraft_stcs == "None":
            return False  # No STCs installed
        
        # Parse aircraft STCs (format: "SA00634DE, SA01234AB")
        aircraft_stc_list = [stc.strip() for stc in str(aircraft_stcs).split(',')]
        
        # Check if any required STC is installed
        for ad_stc in ad_stcs:
            if ad_stc in aircraft_stc_list:
                return True
        
        return False
    
    def evaluate_applicability(self, ad_info: Dict) -> pd.DataFrame:
        """Evaluate AD/SB applicability against entire fleet."""
        results = []
        
        for idx, aircraft in self.fleet_df.iterrows():
            result = {
                'Registration': aircraft['Registration'],
                'MSN': aircraft['MSN'],
                'Aircraft_Model': aircraft['Aircraft_Model'],
                'Applicability': 'NOT APPLICABLE',
                'Compliance_Deadline': 'N/A',
                'Required_Action': 'None',
                'AMP_Update_Required': 'No',
                'Notes': ''
            }
            
            # Step 1: Check model match
            if not self.check_model_match(aircraft['Aircraft_Model'], ad_info['models']):
                result['Notes'] = 'Model not in AD applicability'
                results.append(result)
                continue
            
            # Step 2: Check MSN range
            if not self.check_msn_in_range(aircraft['MSN'], ad_info['msn_ranges']):
                result['Notes'] = f"MSN {aircraft['MSN']} not in affected range"
                results.append(result)
                continue
            
            # Step 3: Check component P/N (if component-specific)
            component_check = self.check_component_match(
                aircraft.get('Component_PN', ''), 
                ad_info['component_pns']
            )
            if component_check is False:
                result['Notes'] = 'Required component P/N not installed'
                results.append(result)
                continue
            elif component_check is None and ad_info['component_pns']:
                result['Applicability'] = 'REQUIRES VERIFICATION'
                result['Notes'] = 'Component P/N verification needed'
                results.append(result)
                continue
            
            # Step 4: Check STC (if STC-specific)
            stc_check = self.check_stc_match(
                aircraft.get('STC_List', ''),
                ad_info['stc_list']
            )
            if stc_check is False and ad_info['stc_list']:
                result['Notes'] = f"Required STC {ad_info['stc_list']} not installed"
                results.append(result)
                continue
            
            # If we get here, it's APPLICABLE
            result['Applicability'] = 'APPLICABLE'
            
            # Calculate compliance deadline
            result['Compliance_Deadline'] = self._calculate_compliance_deadline(
                aircraft, ad_info['compliance_time'], ad_info['compliance_type']
            )
            
            # Set required action
            result['Required_Action'] = ad_info['required_actions'][:100] + "..."
            
            # Determine if AMP update required
            if ad_info['is_recurring']:
                result['AMP_Update_Required'] = 'Yes'
                result['Notes'] = 'Recurring inspection - add to AMP'
            else:
                result['AMP_Update_Required'] = 'No'
                result['Notes'] = 'One-time compliance'
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def _calculate_compliance_deadline(self, aircraft: pd.Series, compliance_time: str, compliance_type: str) -> str:
        """Calculate when compliance is due."""
        if compliance_type == 'immediate':
            return 'IMMEDIATE - Before next flight'
        
        if compliance_type == 'hours':
            hours_match = re.search(r'(\d+)', compliance_time)
            if hours_match:
                compliance_hours = int(hours_match.group(1))
                deadline_hours = aircraft['Total_Hours'] + compliance_hours
                return f"{deadline_hours} hours"
        
        if compliance_type == 'landings':
            landings_match = re.search(r'(\d+)', compliance_time)
            if landings_match:
                compliance_landings = int(landings_match.group(1))
                deadline_landings = aircraft['Total_Landings'] + compliance_landings
                return f"{deadline_landings} landings"
        
        if compliance_type == 'calendar':
            days_match = re.search(r'(\d+)', compliance_time)
            if days_match:
                compliance_days = int(days_match.group(1))
                deadline_date = datetime.now() + timedelta(days=compliance_days)
                return deadline_date.strftime('%Y-%m-%d')
        
        return compliance_time
    
    def generate_report(self, ad_info: Dict, evaluation_df: pd.DataFrame, output_path: str):
        """Generate Excel evaluation report."""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Evaluation Summary
            evaluation_df.to_excel(writer, sheet_name='Evaluation Summary', index=False)
            
            # Sheet 2: Document Details
            doc_details = pd.DataFrame({
                'Field': [
                    'Document Number',
                    'Document Type',
                    'Issuing Authority',
                    'Subject',
                    'Applicable Models',
                    'MSN Ranges',
                    'Component P/Ns',
                    'Required STCs',
                    'Compliance Time',
                    'Compliance Type',
                    'Is Recurring',
                    'Required Actions'
                ],
                'Value': [
                    ad_info['document_number'],
                    ad_info['document_type'],
                    ad_info['issuing_authority'],
                    ad_info['subject'],
                    ', '.join(ad_info['models']) if ad_info['models'] else 'All',
                    str(ad_info['msn_ranges']),
                    ', '.join(ad_info['component_pns']) if ad_info['component_pns'] else 'N/A',
                    ', '.join(ad_info['stc_list']) if ad_info['stc_list'] else 'N/A',
                    ad_info['compliance_time'],
                    ad_info['compliance_type'],
                    'Yes' if ad_info['is_recurring'] else 'No',
                    ad_info['required_actions']
                ]
            })
            doc_details.to_excel(writer, sheet_name='Document Details', index=False)
        
        print(f"\nReport generated: {output_path}")
    
    def print_summary(self, evaluation_df: pd.DataFrame, ad_info: Dict):
        """Print evaluation summary to console."""
        total = len(evaluation_df)
        applicable = len(evaluation_df[evaluation_df['Applicability'] == 'APPLICABLE'])
        not_applicable = len(evaluation_df[evaluation_df['Applicability'] == 'NOT APPLICABLE'])
        requires_verification = len(evaluation_df[evaluation_df['Applicability'] == 'REQUIRES VERIFICATION'])
        immediate = len(evaluation_df[evaluation_df['Compliance_Deadline'].str.contains('IMMEDIATE', na=False)])
        amp_required = len(evaluation_df[evaluation_df['AMP_Update_Required'] == 'Yes'])
        
        print(f"\n{'='*60}")
        print(f"AD/SB EVALUATION SUMMARY")
        print(f"{'='*60}")
        print(f"Document: {ad_info['document_type']} {ad_info['document_number']}")
        print(f"Authority: {ad_info['issuing_authority']}")
        print(f"Subject: {ad_info['subject'][:60]}...")
        print(f"\nFleet Evaluation:")
        print(f"  Total Aircraft: {total}")
        print(f"  ✓ APPLICABLE: {applicable}")
        print(f"  ✗ NOT APPLICABLE: {not_applicable}")
        print(f"  ? REQUIRES VERIFICATION: {requires_verification}")
        print(f"\nCompliance:")
        print(f"  IMMEDIATE ACTION: {immediate} aircraft")
        print(f"  AMP UPDATE REQUIRED: {amp_required} aircraft")
        print(f"{'='*60}\n")


# Main execution function
def main(ad_pdf_path: str, fleet_db_path: str, output_path: str = None):
    """Main execution function."""
    try:
        # Initialize evaluator
        print("Loading fleet database...")
        evaluator = ADSBEvaluator(fleet_db_path)
        
        # Extract AD information
        print("Extracting AD/SB information from PDF...")
        ad_info = evaluator.extract_ad_info_from_pdf(ad_pdf_path)
        
        # Evaluate applicability
        print("Evaluating applicability against fleet...")
        evaluation_df = evaluator.evaluate_applicability(ad_info)
        
        # Generate report
        if output_path is None:
            doc_num = ad_info['document_number'].replace('/', '_').replace(' ', '_')
            output_path = f"AD_SB_Evaluation_{doc_num}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        evaluator.generate_report(ad_info, evaluation_df, output_path)
        
        # Print summary
        evaluator.print_summary(evaluation_df, ad_info)
        
        return output_path
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python ad_sb_evaluator.py <ad_pdf_path> <fleet_db_path> [output_path]")
        sys.exit(1)
    
    ad_pdf = sys.argv[1]
    fleet_db = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else None
    
    main(ad_pdf, fleet_db, output)
