import re
import spacy

class MarksheetParser12:
    def __init__(self, data):
        self.data = data
        self.fields = {item.get("label", ""): item["text"] for item in data}
        # Print for debugging purposes - keep this to see what data we're working with
        print("Available fields:", self.fields)
        self.nlp = spacy.load("en_core_web_lg")

    def extract_name(self):
        raw_text = self.fields.get("Name")
        if not raw_text:
            return "Name Not Found"

        lines = raw_text.split("\n")
        for line in lines:
            cleaned = re.sub(r"[^A-Za-z\s]", "", line).strip()
            if cleaned and cleaned.replace(" ", "").isupper():
                return cleaned  
        return "Error extracting Name"
    
    def extract_seat_no(self):
        # Get text from Seat_no field
        seat_text = self.fields.get("Seat_no", "")
        print(f"Seat text: '{seat_text}'")
        
        # Direct method for your specific format
        if seat_text:
            # Get just the digits
            digits = re.sub(r"[^0-9]", "", seat_text)
            if digits and len(digits) == 6:
                return f"B {digits}"
            
            # If that didn't work, try to find any pattern that looks like a seat number
            match = re.search(r"([A-Z])?\s*(\d{6})", seat_text)
            if match:
                letter = match.group(1) if match.group(1) else "B"
                return f"{letter} {match.group(2)}"
        
        # Try looking in other fields
        for field_name, text in self.fields.items():
            if "seat" in field_name.lower() or "no" in field_name.lower():
                match = re.search(r"([A-Z])?\s*(\d{6})", text)
                if match:
                    letter = match.group(1) if match.group(1) else "B"
                    return f"{letter} {match.group(2)}"
        
        return "Error extracting Seat Number"

    def extract_month_year(self):
        month_text = self.fields.get("Month_year", "")
        if not month_text:
            return "Month-Year Not Found"
        
        # Your format appears to be straightforward
        if "-" in month_text and any(month in month_text.upper() for month in 
                                   ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", 
                                    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]):
            return month_text.upper()
        
        return "Error extracting Month-Year"

    def extract_percentile_rank(self):
        percentile_text = self.fields.get("Percentile_rank", "")
        print(f"Percentile text: '{percentile_text}'")
        
        if percentile_text:
            
            if " " in percentile_text:
                parts = percentile_text.strip().split()
                if len(parts) == 2 and all(part.isdigit() for part in parts):
                    return f"{parts[0]}.{parts[1]}"
            
            # Check for decimal numbers
            decimal_match = re.search(r"\d+[.,]\d+", percentile_text)
            if decimal_match:
                return decimal_match.group(0).replace(",", ".")
            
            # Try combining numbers if there are multiple
            digits = re.findall(r"\d+", percentile_text)
            if len(digits) >= 2:
                return f"{digits[0]}.{digits[1]}"
        
        # Try to find percentile in other fields
        for field_name, text in self.fields.items():
            if "percentile" in field_name.lower() or "rank" in field_name.lower():
                # Look for decimal numbers
                decimal_match = re.search(r"\d+[.,]\d+", text)
                if decimal_match:
                    return decimal_match.group(0).replace(",", ".")
                
                # Look for space-separated numbers
                numbers = re.findall(r"\d+", text)
                if len(numbers) >= 2:
                    return f"{numbers[0]}.{numbers[1]}"
        
        return "Error extracting Percentile Rank"