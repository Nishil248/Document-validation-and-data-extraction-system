import re
import spacy

class CollegeMarksheetParser:
    
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
            # Remove all characters except letters and spaces
            cleaned = re.sub(r"[^A-Za-z\s]", "", line).strip()

            # Check if the cleaned line has only capital letters (excluding spaces)
            if cleaned and cleaned.replace(" ", "").isupper():
                return cleaned  

        return "Error extracting Name"       
    
    def extract_course(self):
        raw_text = self.fields.get("Course", "")
        if raw_text:
            cleaned = re.sub(r"[^A-Za-z\s()]", "", raw_text)
            match = re.search(r"(?i)(BACHELOR|MASTER).*", cleaned)
            return match.group(0).strip() if match else "Error extracting course"
        
        return "Error extracting course"

    def extract_month_year(self):
        month_text = self.fields.get("Month_year")
        if month_text:
            month_text = month_text.replace("~", "-").strip()
            match = re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s*[--]\s*\d{4}\b", month_text, re.IGNORECASE)
            return match.group(0).strip().upper() if match else month_text
        
        return "Error extracting Month-Year"
    
    def extract_enrolment_no(self):
        raw_text = self.fields.get("Enroll_No")
        if raw_text:
            cleaned = re.sub(r"[^0-9]", "", raw_text)
            return cleaned if len(cleaned) == 14 else "Invalid Enrolment Number"
        
        return "Error extracting Enrolment number"

    def extract_semester(self):
        raw_text = self.fields.get("Sem")
        if raw_text:
            cleaned = re.sub(r"[^A-Za-z0-9\s]", "", raw_text)
            match = re.search(r"\bSEMESTER\s?\d\b", cleaned, re.IGNORECASE)
            return match.group(0).upper() if match else "Error extracting Semester"

        return "Error extracting Semester"

    def extract_sgpa(self):
        try:
            raw_text = self.fields.get("SGPA")
            cleaned = re.sub(r"[^0-9.,]", "", raw_text).replace(",", ".")
            match = re.search(r"^\d\.\d{2}$", cleaned)
            return match.group(0) if match else "Invalid Format"
        except:
            return "Error extracting SGPA"

    def extract_cgpa(self):
        try:
            raw_text = self.fields.get("CGPA")
            cleaned = re.sub(r"[^0-9.,]", "", raw_text).replace(",", ".")
            match = re.search(r"^\d\.\d{2}$", cleaned)
            return match.group(0) if match else "Invalid Format"
        except:
            return "Error extracting CGPA"
        

        