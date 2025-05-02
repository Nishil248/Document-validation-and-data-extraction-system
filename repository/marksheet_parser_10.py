import re
import spacy

class MarksheetParser10:
    def __init__(self, data):
        self.data = data
        self.fields = {item.get("label", ""): item["text"] for item in data}
        self.nlp = spacy.load("en_core_web_lg")

    def extract_name(self):
        raw_text = self.fields.get("Name")
        if not raw_text:
            return "Name Not Found"

        lines = raw_text.split("\n")

        for line in lines:
            # Step 1: Remove all characters except letters and spaces
            cleaned = re.sub(r"[^A-Za-z\s]", "", line).strip()

            # Step 2: Check if the cleaned line has only capital letters (excluding spaces)
            if cleaned and cleaned.replace(" ", "").isupper():
                return cleaned  # Return the correctly formatted name line

        return "Name Not Found"

    # def extract_seat_no(self):
    #     seat_text = self.fields.get("Seat_no")
    #     if seat_text:
    #         match = re.search(r"\b[A-Z]\d{7}\b", seat_text)
    #         return match.group() if match else seat_text.strip()
    #     return "Seat Number Not Found"
    
    def extract_seat_no(self):
        seat_text = self.fields.get("Seat_no")
        if seat_text:
            # Clean: remove all non-alphanumeric characters
            cleaned = re.sub(r"[^A-Z0-9]", "", seat_text)

            if len(cleaned) > 1:
                cleaned = cleaned[0] + cleaned[1:].replace('S', '5')

            match = re.search(r"[A-Z]\d{7}", cleaned)
            if match:
                return match.group()
            return "Error extracting Seat Number"
        return "Error extracting Seat Number"

    def extract_month_year(self):
        month_text = self.fields.get("Month_year")
        if month_text:
            # Normalize all types of dashes to regular hyphen
            month_text = month_text.replace("—", "-").replace("–", "-").replace("~", "-")
            cleaned = re.sub(r"[^A-Za-z0-9\s-]", "", month_text)
            match = re.search(r"\b(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s*-\s*\d{4}\b", cleaned)
            if match:    
                return match.group(0) 
            return "Error extracting Month-Year"
        return "Error extracting Month-Year"

    def extract_percentile_rank(self):
        percentile_text = self.fields.get("Percentile_rank")
        if percentile_text:
        # Step 1: Clean the text - replace underscore with decimal point
             cleaned = percentile_text.replace("_", ".")
        
        # Step 2: Keep only digits and dots
             cleaned = re.sub(r"[^0-9.]", "", cleaned).strip()
        
        
        if " " in cleaned:
            parts = cleaned.split()
            if len(parts) == 2:
                cleaned = f"{parts[0]}.{parts[1]}"
        
        # Step 4: Validate format (must be like XX.XX)
        if re.match(r"^\d{1,2}\.\d{2}$", cleaned):
            return cleaned
        else:
            # Try to fix common patterns
            if re.match(r"^\d{2,4}$", cleaned) and len(cleaned) >= 4:
                
                return f"{cleaned[:-2]}.{cleaned[-2:]}"
            
            return "Invalid Format: Expected XX.XX"

        return "Percentile Rank Not Found"
     