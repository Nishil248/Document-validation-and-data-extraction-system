import re

class PANParser:
    def __init__(self, data):
        self.data = data
        self.fields = {item.get("label", ""): item["text"] for item in data}

    def extract_name(self):
        name = self.fields.get("Name")
        if name:
            cleaned = re.sub(r"[^A-Za-z\s]", "", name).strip()
            return cleaned
        return "Error extracting Name"

    def extract_father_name(self):
        fathername = self.fields.get("Father name")
        if fathername:
            cleaned = re.sub(r"[^A-Za-z\s]", "", fathername).strip()
            return cleaned
        return "Error extracting Father's Name"

    def extract_dob(self):
        dob = self.fields.get("DOB")
        if dob:
            # Check for correct format dd/mm/yyyy
            match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", dob)
            if match:
                return match.group(0)

            # Remove all non-digit characters
            dob_digits = re.sub(r"[^\d/]", "", dob)

            # Step 3: Handle 10-digit OCR-glitched format
            if len(dob_digits) == 10 and dob_digits[2] == '1' and dob_digits[5] == '1':
                formatted = f"{dob_digits[:2]}/{dob_digits[3:5]}/{dob_digits[6:]}"
                return formatted

            # Step 4: Handle clean 8-digit numeric date
            if len(dob_digits) == 8:
                return f"{dob_digits[:2]}/{dob_digits[2:4]}/{dob_digits[4:]}"
            
            return "Error extracting Date of Birth"

        return "Error extracting Date of Birth"

    def extract_pan_number(self):
        pan = self.fields.get("PAN_no")
        if pan:
            cleaned = re.sub(r"[^A-Z0-9]", "", pan.upper())
            match = re.search(r"[A-Z]{5}\d{4}[A-Z]", cleaned)
            if match:
                return match.group(0)
            return "Error extracting PAN number"
        
        return "Error extracting PAN number"    
