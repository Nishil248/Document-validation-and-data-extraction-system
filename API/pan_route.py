from flask import Blueprint, request, jsonify
import numpy as np
from copy import deepcopy

from utils.Text_extraction import TextExtractor
from utils.Validation import ValidateDocument
from utils.helper import FileHelper
from repository.pan_parser import PANParser
from utils.database import MongoDBManager


pan_route = Blueprint("pan_bp", __name__)

@pan_route.route('/api/pan/extract', methods=["POST"])
def process_pan():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        helper = FileHelper("PAN card")
        np_img, error = helper.load_file_as_image(file)

        if np_img is None:
            return jsonify({"Error": error}), 400  # status contains error message 
        extractor = TextExtractor("Models/PAN_Trained_2/weights/best.pt")
        extracted = extractor.extract_text(np_img)

        validator = ValidateDocument()
        is_valid, msg = validator.validate_pan_card(extracted)
        if not is_valid:
            return jsonify({"error": msg}), 422      

        helper.save_image(np_img)

        parser = PANParser(extracted)
        result = {
            "Name": parser.extract_name(),
            "Father Name": parser.extract_father_name(),
            "DOB": parser.extract_dob(),
            "PAN Number": parser.extract_pan_number()
        }

        # Save to MongoDB
        db = MongoDBManager()
        msg = db.insert_document("PAN_collection", deepcopy(result))


        return {"Message":msg, "Extracted Data": result}, 200
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
