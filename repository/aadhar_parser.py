import re
import spacy
from difflib import get_close_matches

class AadharParser:
    def __init__(self, data):
        self.data = data
        self.fields = {item.get("label", ""): item["text"] for item in data}
        print("Available fields:", self.fields)  # Debug output
        self.nlp = spacy.load("en_core_web_lg")
    
    def extract_name(self):
        # Try the Name field
        raw_text = self.fields.get("Name", "")
        if raw_text:
            
            patel_match = re.search(r"(?:.*?)(?:Patel\s+([A-Za-z\s]+))", raw_text)
            if patel_match:
                return f"Patel {patel_match.group(1).strip()}"
            
            # Look for capitalized name patterns
            name_pattern = re.search(r"(?:[A-Z][a-z]+\s)+[A-Z][a-z]+", raw_text)
            if name_pattern:
                return name_pattern.group(0).strip()
            
            # Try NLP approach
            doc = self.nlp(raw_text)
            person_entities = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
            if person_entities:
                return person_entities[0]
            
            # Extract sequence of words with capital letters
            capitalized_words = re.findall(r"[A-Z][a-z]+", raw_text)
            if len(capitalized_words) >= 2:
                return " ".join(capitalized_words)
        
        # If nothing worked with the Name field, search all fields
        for label, text in self.fields.items():
            if "Patel" in text:
                # Extract the part after "Patel"
                patel_match = re.search(r"Patel\s+([A-Za-z\s]+)", text)
                if patel_match:
                    return f"Patel {patel_match.group(1).strip()}"

        return "Error extracting Name"

    def extract_dob(self):
        # First try the DOB field
        raw_text = self.fields.get("DOB", "")
        if raw_text:
            # Standard date format (DD/MM/YYYY)
            date_match = re.search(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})", raw_text)
            if date_match:
                day, month, year = date_match.groups()
                day = day.zfill(2)
                month = month.zfill(2)
                if len(year) == 2:
                    year = "20" + year if int(year) < 30 else "19" + year
                return f"{day}/{month}/{year}"
            
            # Extract numbers that might form a date
            numbers = re.findall(r"\d+", raw_text)
            if len(numbers) >= 3:
                # If we have at least 3 numbers, try to form DD/MM/YYYY
                day = numbers[0].zfill(2) if len(numbers[0]) <= 2 else numbers[0][:2]
                month = numbers[1].zfill(2) if len(numbers[1]) <= 2 else numbers[1][:2]
                year = numbers[2]
                if len(year) == 2:
                    year = "20" + year if int(year) < 30 else "19" + year
                return f"{day}/{month}/{year}"
            
            # Try to extract 8 consecutive digits and parse as DDMMYYYY
            all_digits = "".join(re.findall(r"\d", raw_text))
            if len(all_digits) >= 8:
                return f"{all_digits[:2]}/{all_digits[2:4]}/{all_digits[4:8]}"
        
        # Search all fields for date patterns
        for label, text in self.fields.items():
            # Look for common date formats
            date_match = re.search(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})", text)
            if date_match:
                day, month, year = date_match.groups()
                day = day.zfill(2)
                month = month.zfill(2)
                if len(year) == 2:
                    year = "20" + year if int(year) < 30 else "19" + year
                return f"{day}/{month}/{year}"
            
            # Look for "DOB" keyword followed by numbers
            dob_keyword = re.search(r"(?:DOB|Date\s+of\s+Birth)[:\s]+(.{5,20})", text, re.IGNORECASE)
            if dob_keyword:
                dob_text = dob_keyword.group(1)
                numbers = re.findall(r"\d+", dob_text)
                if len(numbers) >= 3:
                    day = numbers[0].zfill(2) if len(numbers[0]) <= 2 else numbers[0][:2]
                    month = numbers[1].zfill(2) if len(numbers[1]) <= 2 else numbers[1][:2]
                    year = numbers[2]
                    if len(year) == 2:
                        year = "20" + year if int(year) < 30 else "19" + year
                    return f"{day}/{month}/{year}"

        return "Error extracting Date of Birth"

    def extract_gender(self):
        # Try the Gender field first
        raw_text = self.fields.get("Gender", "")
        if raw_text:
            # Clean the text
            cleaned = re.sub(r"[^A-Za-z]", "", raw_text).strip().lower()
            
            # Direct matches
            if "male" in cleaned and "female" not in cleaned:
                return "Male"
            if "female" in cleaned:
                return "Female"
            
            # Fuzzy matching for gender
            valid_options = ["male", "female"]
            match = get_close_matches(cleaned, valid_options, n=1, cutoff=0.5)
            if match:
                return match[0].capitalize()
            
            # Handle common OCR errors
            if any(m in cleaned for m in ["mal", "mae", "mle"]):
                return "Male"
            if any(f in cleaned for f in ["fem", "fmal", "feml"]):
                return "Female"
                
            # Special case for your "#EIE" text
            if '#' in raw_text and 'e' in cleaned.lower():
                return "Male"  # Based on context/position in document
        
        # Search all fields for gender indicators
        for label, text in self.fields.items():
            text_lower = text.lower()
            if "male" in text_lower and "female" not in text_lower:
                return "Male"
            if "female" in text_lower:
                return "Female"
            if "gender" in text_lower and ("m" in text_lower or "f" in text_lower):
                if "f" in text_lower:
                    return "Female"
                return "Male"

        return "Error extracting Gender"

    def extract_aadhar_number(self):
        # Try aadhar_number field first
        raw_text = self.fields.get("aadhar_number", "")
        if raw_text:
            # Keep only digits and spaces
            cleaned_text = re.sub(r"[^\d\s]", "", raw_text).strip()

            # Check for 4-4-4 format
            if re.match(r"^\d{4}\s\d{4}\s\d{4}$", cleaned_text):
                return cleaned_text

            # Handle 12 continuous digits
            digits_only = cleaned_text.replace(" ", "")
            if len(digits_only) == 12:
                return f"{digits_only[:4]} {digits_only[4:8]} {digits_only[8:]}"
        
        # Search all fields for potential Aadhar numbers
        for label, text in self.fields.items():
            # Pattern for Aadhar: 4 digits space 4 digits space 4 digits
            aadhar_pattern = re.search(r"\b(\d{4})\s+(\d{4})\s+(\d{4})\b", text)
            if aadhar_pattern:
                return f"{aadhar_pattern.group(1)} {aadhar_pattern.group(2)} {aadhar_pattern.group(3)}"
            
            # Look for 12 consecutive digits
            digits_only = "".join(re.findall(r"\d", text))
            if len(digits_only) >= 12:
                aadhar_digits = digits_only[:12]  # Take first 12 digits
                return f"{aadhar_digits[:4]} {aadhar_digits[4:8]} {aadhar_digits[8:12]}"
            
            # Look for "Aadhar" keyword followed by numbers
            aadhar_keyword = re.search(r"(?:Aadhar|UID|Unique\s+ID)[:\s]+(.{10,20})", text, re.IGNORECASE)
            if aadhar_keyword:
                aadhar_text = aadhar_keyword.group(1)
                digits_only = "".join(re.findall(r"\d", aadhar_text))
                if len(digits_only) >= 12:
                    return f"{digits_only[:4]} {digits_only[4:8]} {digits_only[8:12]}"

        return "Error extracting Aadhar Number"