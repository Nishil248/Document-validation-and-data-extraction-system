class ValidateDocument:
    # Enhanced NLP keyword sets for each document type
    AADHAR_KEYWORDS = {
        "aadhar", "aadhaar", "uid", "unique identification", "uidai", 
        "भारत सरकार", "government of india", "आईडी", "identification", 
        "dob", "date of birth", "जन्म", "male", "female", "gender", "लिंग",
        "address", "पता", "निवास", "residence", "verify", "authentication",
        "year of birth", "जन्म का साल", "photo", "फोटो", "january", "february",
        "march", "april", "may", "june", "july", "august", "september", "october",
        "november", "december"
    }
    
    PAN_KEYWORDS = {
        "pan", "permanent account number", "income tax", "department of income", 
        "father", "father's name", "पिता", "आयकर विभाग", "tax", "आयकर", 
        "dob", "date of birth", "जन्म", "signature", "हस्ताक्षर", "income-tax",
        "govt. of india", "भारत सरकार", "permanent", "account", "number", "card",
        "कार्ड", "स्थायी", "खाता", "संख्या", "income", "department"
    }
    
    MARKSHEET_10_KEYWORDS = {
        "ssc", "secondary", "10th", "tenth", "board", "examination", "result", 
        "marks", "grade", "percentile", "rank", "school", "विद्यालय", "मार्कशीट",
        "mathematics", "science", "english", "social", "hindi", "language", 
        "pass", "month", "year", "seat", "roll", "student", "division",
        "matriculation", "class x", "certificate", "central board", "state board",
        "cbse", "icse", "total marks", "subject", "theory", "practical"
    }
    
    MARKSHEET_12_KEYWORDS = {
        "hsc", "higher secondary", "12th", "twelfth", "board", "examination", 
        "result", "marks", "grade", "percentile", "rank", "school", "विद्यालय",
        "physics", "chemistry", "biology", "mathematics", "science", "english", 
        "pass", "month", "year", "seat", "roll", "student", "division", "som",
        "class xii", "senior secondary", "certificate", "pcm", "pcb", "commerce",
        "accountancy", "business studies", "economics", "informatics"
    }
    
    COLLEGE_MARKSHEET_KEYWORDS = {
        "university", "college", "institute", "semester", "sem", "sgpa", "cgpa", 
        "course", "degree", "bachelor", "master", "विश्वविद्यालय", "बीटेक", "बीए", "बीएससी",
        "credits", "grade point", "subjects", "theory", "practical", "विषय", "प्रयोगिक",
        "engineering", "arts", "science", "commerce", "elective", "enrollment", "enroll",
        "department", "faculty", "programme", "program", "academic year", "examination",
        "transcript", "btech", "be", "bsc", "ba", "bcom", "bca", "mtech", "me", "msc",
        "ma", "mcom", "mca", "phd", "session", "branch", "division", "honours", "scheme"
    }
    
    @staticmethod
    def _count_keyword_matches(text_data, keyword_set):
        """Count how many keywords from the set match in the text data"""
        if not text_data:
            return 0
            
        # Convert all text to lowercase for case-insensitive matching
        text = " ".join(str(item).lower() for item in text_data).lower()
        
        # Count matching keywords
        matches = sum(1 for keyword in keyword_set if keyword.lower() in text)
        return matches, matches / len(keyword_set) if keyword_set else 0
    
    @staticmethod
    def _extract_all_text(extracted_data):
        """Extract all text from the data for keyword matching"""
        all_text = []
        
        if not extracted_data:
            return all_text
            
        # Extract both labels and values
        for item in extracted_data:
            if isinstance(item, dict):
                # Handle dictionary format
                for key, value in item.items():
                    if isinstance(value, str):
                        all_text.append(value)
                    if isinstance(key, str):
                        all_text.append(key)
            elif isinstance(item, str):
                # Handle string items
                all_text.append(item)
                    
        return all_text
    
    @staticmethod
    def _find_pattern_matches(text_data, patterns):
        """Find matches for specific patterns in the text data"""
        matches = []
        for item in text_data:
            if isinstance(item, str):
                for pattern, pattern_type in patterns:
                    if pattern.search(item):
                        matches.append(pattern_type)
        return matches
    
    @staticmethod
    def _normalize_label(label):
        """Normalize label text for more flexible matching"""
        if not label:
            return ""
        # Convert to lowercase, remove spaces and underscores
        normalized = label.lower().replace(" ", "").replace("_", "")
        return normalized
        
    @staticmethod
    def validate_aadhar_card(extracted_data):
        if not extracted_data:
            return False, "No extracted data found from the document."
        
        try:
            # Aadhar number pattern: 12 digits, optionally grouped with spaces or dashes
            import re
            aadhar_patterns = [
                (re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'), 'aadhar_number'),
                (re.compile(r'\b[2-9]\d{11}\b'), 'aadhar_number')  # Raw 12 digits (first digit 2-9)
            ]
            
            # Extract all text and look for patterns
            all_text = ValidateDocument._extract_all_text(extracted_data)
            pattern_matches = ValidateDocument._find_pattern_matches(all_text, aadhar_patterns)
            
            # Check for Aadhar number in values with flexible label matching
            aadhar_found = False
            for item in extracted_data:
                if isinstance(item, dict) and 'label' in item and 'value' in item:
                    normalized_label = ValidateDocument._normalize_label(item['label'])
                    if any(keyword in normalized_label for keyword in ['aadhar', 'aadhaar', 'uid', 'number']):
                        # Check if value looks like an Aadhar number (12 digits)
                        value = ''.join(filter(str.isdigit, item['value']))
                        if len(value) == 12 and value[0] in '23456789':
                            aadhar_found = True
                            break
            
            # Keyword NLP check
            keyword_matches, match_ratio = ValidateDocument._count_keyword_matches(all_text, ValidateDocument.AADHAR_KEYWORDS)
            
            # Document is valid if either:
            # 1. It has an identifiable Aadhar number OR
            # 2. It has enough keyword matches AND pattern matches to indicate it's an Aadhar card
            if aadhar_found or 'aadhar_number' in pattern_matches:
                return True, "Document validated successfully as an Aadhar card."
            elif keyword_matches >= 5 or match_ratio >= 0.15:  # More flexible threshold
                return True, "Document validated as an Aadhar card based on content analysis."
            else:
                return False, "Validation Failed: Document does not appear to be an Aadhar card."
                
        except Exception as e:
            return False, f"Unexpected data format: {str(e)}"
    
    @staticmethod
    def validate_pan_card(extracted_data):
        if not extracted_data:
            return False, "No extracted data found from the document."
        
        try:
            # PAN pattern: 5 letters + 4 digits + 1 letter
            import re
            pan_pattern = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b')
            
            # Extract all text and look for PAN pattern
            all_text = ValidateDocument._extract_all_text(extracted_data)
            
            # Directly search for PAN format in all text
            pan_found = False
            for text in all_text:
                if isinstance(text, str):
                    # Convert to uppercase and search
                    matches = pan_pattern.findall(text.upper())
                    if matches:
                        pan_found = True
                        break
            
            # Check for PAN in values with flexible label matching
            pan_label_found = False
            for item in extracted_data:
                if isinstance(item, dict) and 'label' in item and 'value' in item:
                    normalized_label = ValidateDocument._normalize_label(item['label'])
                    if any(keyword in normalized_label for keyword in ['pan', 'permanent', 'number', 'account']):
                        # Clean and check value
                        value = item['value'].strip().upper()
                        if pan_pattern.search(value):
                            pan_label_found = True
                            break
            
            # Keyword NLP check
            keyword_matches, match_ratio = ValidateDocument._count_keyword_matches(all_text, ValidateDocument.PAN_KEYWORDS)
            
            # Document is valid if either:
            # 1. It has a PAN format number OR
            # 2. It has a PAN label with valid format OR
            # 3. It has enough keyword matches to indicate it's a PAN card
            if pan_found or pan_label_found:
                return True, "Document validated successfully as a PAN card."
            elif keyword_matches >= 4 or match_ratio >= 0.15:  # More flexible threshold
                return True, "Document validated as a PAN card based on content analysis."
            else:
                return False, "Validation Failed: Document does not appear to be a PAN card."
                
        except Exception as e:
            return False, f"Unexpected data format: {str(e)}"
    
    @staticmethod
    def validate_marksheet_10(extracted_data):
        if not extracted_data:
            return False, "Validation Failed: No data extracted from the document."
        
        try:
            # Extract all text 
            all_text = ValidateDocument._extract_all_text(extracted_data)
            
            # Keyword NLP check
            keyword_matches, match_ratio = ValidateDocument._count_keyword_matches(all_text, ValidateDocument.MARKSHEET_10_KEYWORDS)
            
            # Check for subject patterns
            subject_keywords = ["mathematics", "maths", "english", "science", "social", "hindi", "language", "sanskrit"]
            subject_count = 0
            
            # Count subject references
            for item in extracted_data:
                if isinstance(item, dict):
                    if 'label' in item:
                        label = item['label'].lower()
                        if any(subj in label for subj in subject_keywords):
                            subject_count += 1
                    
                    # Also check values for subject names
                    if 'value' in item:
                        value = item['value'].lower()
                        if any(subj in value for subj in subject_keywords):
                            subject_count += 1
            
            # Check for "10th" or "SSC" or "Secondary" indicators
            tenth_indicators = ["10th", "tenth", "ssc", "secondary", "matriculation", "class x"]
            has_tenth_indicator = any(indicator in " ".join(all_text).lower() for indicator in tenth_indicators)
            
            # Document is valid if:
            # 1. It has strong 10th marksheet indicators AND subject references OR
            # 2. It has enough keyword matches to indicate it's a 10th marksheet
            if has_tenth_indicator and subject_count >= 2:
                return True, "Document validated successfully as a 10th Marksheet."
            elif keyword_matches >= 5 or match_ratio >= 0.15:  # More flexible threshold
                return True, "Document validated as a 10th Marksheet based on content analysis."
            else:
                return False, "Validation Failed: Document does not appear to be a 10th Marksheet."
                
        except Exception as e:
            return False, f"Unexpected data format: {str(e)}"
    
    @staticmethod
    def validate_marksheet_12(extracted_data):
        if not extracted_data:
            return False, "Validation Failed: No data extracted from the document."
        
        try:
            # Extract all text
            all_text = ValidateDocument._extract_all_text(extracted_data)
            
            # Keyword NLP check
            keyword_matches, match_ratio = ValidateDocument._count_keyword_matches(all_text, ValidateDocument.MARKSHEET_12_KEYWORDS)
            
            # Check for 12th specific subjects
            subject_keywords = ["physics", "chemistry", "biology", "mathematics", "computer science", 
                              "accountancy", "business", "economics", "english", "hindi"]
            subject_count = 0
            
            # Count subject references
            for item in extracted_data:
                if isinstance(item, dict):
                    if 'label' in item:
                        label = item['label'].lower()
                        if any(subj in label for subj in subject_keywords):
                            subject_count += 1
                    
                    # Also check values for subject names
                    if 'value' in item:
                        value = item['value'].lower()
                        if any(subj in value for subj in subject_keywords):
                            subject_count += 1
            
            # Check for "12th" or "HSC" indicators
            twelfth_indicators = ["12th", "twelfth", "hsc", "higher secondary", "senior secondary", "class xii"]
            has_twelfth_indicator = any(indicator in " ".join(all_text).lower() for indicator in twelfth_indicators)
            
            # Document is valid if:
            # 1. It has strong 12th marksheet indicators AND subject references OR
            # 2. It has enough keyword matches to indicate it's a 12th marksheet
            if has_twelfth_indicator and subject_count >= 2:
                return True, "Document validated successfully as a 12th Marksheet."
            elif keyword_matches >= 5 or match_ratio >= 0.15:  # More flexible threshold
                return True, "Document validated as a 12th Marksheet based on content analysis."
            else:
                return False, "Validation Failed: Document does not appear to be a 12th Marksheet."
                
        except Exception as e:
            return False, f"Unexpected data format: {str(e)}"
    
    @staticmethod
    def validate_college_marksheet(extracted_data):
        if not extracted_data:
            return False, "Validation Failed: No data extracted from the document."
        
        try:
            # Extract all text
            all_text = ValidateDocument._extract_all_text(extracted_data)
            
            # Keyword NLP check
            keyword_matches, match_ratio = ValidateDocument._count_keyword_matches(all_text, ValidateDocument.COLLEGE_MARKSHEET_KEYWORDS)
            
            # Check for college-specific indicators
            college_indicators = ["university", "college", "institute", "bachelor", "master", "semester", 
                                "degree", "programme", "sgpa", "cgpa", "engineering", "technology", "faculty"]
            
            has_college_indicator = any(indicator in " ".join(all_text).lower() for indicator in college_indicators)
            
            # Check for degree patterns
            degree_patterns = ["btech", "be", "bsc", "ba", "bcom", "bca", "mtech", "me", "msc", "ma", "mcom", "mca", "phd"]
            has_degree_pattern = any(pattern in " ".join(all_text).lower() for pattern in degree_patterns)
            
            # Check for semester patterns
            import re
            semester_pattern = re.compile(r'\b(?:sem|semester)[^a-z0-9]*[1-8]\b', re.IGNORECASE)
            has_semester = any(semester_pattern.search(text) for text in all_text if isinstance(text, str))
            
            # Document is valid if:
            # 1. It has strong college indicators AND degree/semester references OR
            # 2. It has enough keyword matches to indicate it's a college marksheet
            if (has_college_indicator and (has_degree_pattern or has_semester)):
                return True, "Document validated successfully as a College Marksheet."
            elif keyword_matches >= 5 or match_ratio >= 0.12:  # More flexible threshold
                return True, "Document validated as a College Marksheet based on content analysis."
            else:
                return False, "Validation Failed: Document does not appear to be a College Marksheet."
                
        except Exception as e:
            return False, f"Unexpected data format: {str(e)}"