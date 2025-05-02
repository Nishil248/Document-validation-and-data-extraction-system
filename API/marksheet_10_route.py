from flask import Blueprint, request, jsonify
import numpy as np
from copy import deepcopy
import traceback

from utils.Text_extraction import TextExtractor
from utils.Validation import ValidateDocument
from utils.helper import FileHelper
from repository.marksheet_parser_10 import MarksheetParser10
from utils.database import MongoDBManager


marksheet_10_route = Blueprint("marksheet10_bp", __name__)

@marksheet_10_route.route('/api/marksheet10/extract', methods=["POST"])
def process_10th():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        helper = FileHelper("Aadhar card")
        np_img, error = helper.load_file_as_image(file)

        if np_img is None:
            return jsonify({"Error": error}), 400  # status contains error message 

        extractor = TextExtractor("Models/10th_Trained_3/weights/best.pt")
        extracted = extractor.extract_text(np_img)

        validator = ValidateDocument()
        is_valid, msg = validator.validate_marksheet_10(extracted)
        if not is_valid:
            return jsonify({"error": msg}), 422

        helper.save_image(np_img)

        parser = MarksheetParser10(extracted)
        result = {
            "Name": parser.extract_name(),
            "Seat Number": parser.extract_seat_no(),
            "Month-Year": parser.extract_month_year(),
            "Percentile Rank": parser.extract_percentile_rank()
        }

        
        error_values = [
            "Error extracting Seat Number",
        ]
        if all(val in result.values() for val in error_values):
            return jsonify({"error": "Document validation failed or wrong document uploaded"}), 422

        helper.save_image(np_img)


        # Save to MongoDB
        db = MongoDBManager()
        msg = db.insert_document("Marksheet10_collection", deepcopy(result))

        return {"Message":msg, "Extracted Data": result}, 200

    except Exception as e:
        error_trace = traceback.format_exc()
        print("Error Traceback:\n", error_trace)  
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
