from flask import Blueprint, request, jsonify
import numpy as np
from copy import deepcopy
import traceback

from utils.Text_extraction import TextExtractor
from utils.Validation import ValidateDocument
from utils.helper import FileHelper
from repository.college_parser import CollegeMarksheetParser
from utils.database import MongoDBManager


college_route = Blueprint("college_bp", __name__)

@college_route.route('/api/college/extract', methods=["POST"])
def process_college():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        helper = FileHelper("College Marksheet")
        np_img, error = helper.load_file_as_image(file)

        if np_img is None:
            return jsonify({"Error": error}), 400  # status contains error message        

        extractor = TextExtractor("Models/CVM_Marksheet_Trained_2/weights/best.pt")
        extracted = extractor.extract_text(np_img)

        validator = ValidateDocument()
        valid, msg = validator.validate_college_marksheet(extracted)
        if not valid:
            return jsonify({"error": msg}), 422

        helper.save_image(np_img)

        parser = CollegeMarksheetParser(extracted)
        result = {
            "Name": parser.extract_name(),
            "Enrollment Number": parser.extract_enrolment_no(),
            "Semester": parser.extract_semester(),
            "Month-Year": parser.extract_month_year(),
            "Course": parser.extract_course(),
            "SGPA": parser.extract_sgpa(),
            "CGPA": parser.extract_cgpa()
        }

        # Save to MongoDB
        db = MongoDBManager()
        msg = db.insert_document("College_collection", deepcopy(result))

        return {"Message":msg, "Extracted Data": result}, 200

    except Exception as e:
        error_trace = traceback.format_exc()
        print("Error Traceback:\n", error_trace)  
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
