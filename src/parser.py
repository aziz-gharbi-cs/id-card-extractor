import re
from mrz.checker.td1 import TD1CodeChecker
from mrz.checker.td2 import TD2CodeChecker
from mrz.checker.td3 import TD3CodeChecker

class IDParser:
    def parse(self, text):
        raise NotImplementedError

class MRZParser(IDParser):
    def find_mrz_candidates(self, text):
        """
        Extracts lines that look like MRZ lines (uppercased, digits, <).
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        candidates = []
        for line in lines:
            # Clean up common OCR mistakes for MRZ chars
            # But relying on raw OCR is usually better unless it's very noisy
            clean_line = line.replace(' ', '')
            # MRZ lines usually contain '<<' or at least multiple '<' 
            # and are uppercase alphanumeric.
            if len(clean_line) > 20 and '<' in clean_line:
                candidates.append(clean_line)
        return candidates

    def parse(self, text):
        candidates = self.find_mrz_candidates(text)
        if not candidates:
            return None
        
        # Try to match patterns from the bottom up
        # TD3: 2 lines of 44 chars
        # TD1: 3 lines of 30 chars
        
        mrz_data = {"raw": candidates, "parsed": {}, "type": "Unknown", "valid": False}
        
        # We try to construct a valid block from the last few candidates
        reversed_cand = list(reversed(candidates))
        
        # Check for TD3 (Passport) - 2 lines
        for i in range(len(reversed_cand) - 1):
            line2 = reversed_cand[i]
            line1 = reversed_cand[i+1]
            
            # Simple length heuristic (allow some margin for OCR noise if we handled it, 
            # but mrz library is strict. We just pass it and see if it works)
            # We strictly pass the string.
            
            # Try TD3
            try:
                td3_check = TD3CodeChecker(line1 + "\n" + line2)
                if td3_check.valid:
                    mrz_data["parsed"] = td3_check.fields()
                    mrz_data["type"] = "TD3 (Passport)"
                    mrz_data["valid"] = True
                    return mrz_data
            except Exception:
                pass
                
        # Check for TD1 (ID Card) - 3 lines
        for i in range(len(reversed_cand) - 2):
            line3 = reversed_cand[i]
            line2 = reversed_cand[i+1]
            line1 = reversed_cand[i+2]
            
            try:
                td1_check = TD1CodeChecker(line1 + "\n" + line2 + "\n" + line3)
                if td1_check.valid:
                    mrz_data["parsed"] = td1_check.fields()
                    mrz_data["type"] = "TD1 (Identity Card)"
                    mrz_data["valid"] = True
                    return mrz_data
            except Exception:
                pass

        return mrz_data

class RegexParser(IDParser):
    def parse(self, text):
        extracted = {}
        
        # Date Pattern: DD/MM/YYYY or DD-MM-YYYY or YYYY-MM-DD
        # We capture them and try to deduce what they are contextually
        
        # Explicit labels (most reliable)
        # Name
        name_match = re.search(r'(?:Name|Surname|Given Names)\s*[:.]?\s*([A-Z\s]+)', text, re.IGNORECASE)
        if name_match:
            extracted['full_name'] = {"value": name_match.group(1).strip(), "confidence": 0.7}
            
        # DOB
        dob_match = re.search(r'(?:DOB|Date of Birth|Birth)\s*[:.]?\s*(\d{2}[-/.]\d{2}[-/.]\d{4}|\d{4}[-/.]\d{2}[-/.]\d{2})', text, re.IGNORECASE)
        if dob_match:
            extracted['date_of_birth'] = {"value": dob_match.group(1), "confidence": 0.8}
            
        # ID Number (Generic look for a long alphanum string that is NOT a date)
        # This is hard to do generally without context.
        
        return extracted

class CombinedParser:
    def __init__(self):
        self.mrz_parser = MRZParser()
        self.regex_parser = RegexParser()
    
    def parse(self, text):
        final_result = {
            "document_type": "Unknown",
            "fields": {},
            "mrz": {}
        }
        
        # Run MRZ Parser
        mrz_result = self.mrz_parser.parse(text)
        if mrz_result and mrz_result.get("valid"):
            final_result["mrz"] = mrz_result
            final_result["document_type"] = mrz_result.get("type", "Unknown")
            
            # Populate basic fields from MRZ if valid
            fields = mrz_result.get("parsed", {})
            if "surname" in fields and "name" in fields:
                final_result["fields"]["full_name"] = {"value": f"{fields.get('surname', '')} {fields.get('name', '')}", "confidence": 1.0}
            if "birth_date" in fields:
                final_result["fields"]["date_of_birth"] = {"value": fields.get("birth_date"), "confidence": 1.0}
            if "expiry_date" in fields:
                final_result["fields"]["expiration_date"] = {"value": fields.get("expiry_date"), "confidence": 1.0}
            if "nationality" in fields:
                 final_result["fields"]["nationality"] = {"value": fields.get("nationality"), "confidence": 1.0}
            if "sex" in fields:
                 final_result["fields"]["gender"] = {"value": fields.get("sex"), "confidence": 1.0}
            if "document_number" in fields:
                 final_result["fields"]["id_number"] = {"value": fields.get("document_number"), "confidence": 1.0}

        # Run Regex Parser as fallback or augmentation
        regex_result = self.regex_parser.parse(text)
        
        # Merge (prefer MRZ if it exists, otherwise Regex)
        for key, val in regex_result.items():
            if key not in final_result["fields"]:
                final_result["fields"][key] = val
        
        return final_result
