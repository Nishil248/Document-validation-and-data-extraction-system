from flask import Blueprint, request, jsonify
import numpy as np
from copy import deepcopy
import traceback

from utils.Text_extraction import TextExtractor
from utils.Validation import ValidateDocument
from utils.helper import FileHelper
from repository.marksheet_parser_12 import MarksheetParser12
from utils.database import MongoDBManager


marksheet_12_route = Blueprint("marksheet12_bp", __name__)

@marksheet_12_route.route('/api/marksheet12/extract', methods=["POST"])
def process_12th():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        helper = FileHelper("12th Marksheet")
        np_img, error = helper.load_file_as_image(file)

        if np_img is None:
            return jsonify({"Error": error}), 400  # status contains error message 

        extractor = TextExtractor("Models/12th_Trained_2/weights/best.pt")
        extracted = extractor.extract_text(np_img)

        validator = ValidateDocument()
        is_valid, msg = validator.validate_marksheet_12(extracted)
        if not is_valid:
            return jsonify({"error": msg}), 422

        helper.save_image(np_img)

        parser = MarksheetParser12(extracted)
        result = {
            "Name": parser.extract_name(),
            "Seat Number": parser.extract_seat_no(),
            "Month-Year": parser.extract_month_year(),
            "Percentile Rank": parser.extract_percentile_rank()
        }

        # Save to MongoDB
        db = MongoDBManager()
        msg = db.insert_document("Marksheet12_collection", deepcopy(result))

        return {"Message":msg, "Extracted Data": result}, 200

    except Exception as e:
        error_trace = traceback.format_exc()
        print("Error Traceback:\n", error_trace)  
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
