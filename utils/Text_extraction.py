import cv2
from PIL import Image
import numpy as np
from ultralytics import YOLO
from collections import defaultdict
import easyocr

class TextExtractor:
    def __init__(self, model_path, lang_list=['en']):
        self.model = YOLO(model_path)
        self.reader = easyocr.Reader(lang_list, gpu=False)  # Set gpu=True if using GPU

    def extract_text(self, image):
        try:
            results = self.model(image, conf=0.10)
            extracted_data = []

            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                h, w, _ = image.shape
                x1, y1 = max(0, x1 - 5), max(0, y1 - 5)
                x2, y2 = min(w, x2 + 5), min(h, y2 + 5)

                cropped = image[y1:y2, x1:x2]
                if cropped is None or cropped.size == 0:
                    print(f"Warning: Empty cropped image for bbox {x1, y1, x2, y2}")
                    continue

                raw_text = self.parse_image(cropped)
                if raw_text:
                    label_index = int(box.cls[0].item())
                    label = self.model.names[label_index]

                    extracted_data.append({
                        "label": label,
                        "coordinates": (x1, y1, x2, y2),
                        "text": raw_text,
                        "confidence": box.conf.item()
                    })

            #  Auto-pick highest confidence per label
            grouped_data = defaultdict(list)
            for item in extracted_data:
                grouped_data[item["label"].lower()].append(item)

            final_extracted_data = []
            for label, items in grouped_data.items():
                best_item = max(items, key=lambda x: x["confidence"])
                final_extracted_data.append(best_item)

            print("Filtered Extracted Text (one per label):", final_extracted_data)
            return final_extracted_data if final_extracted_data else None

        except Exception as e:
            raise RuntimeError(f"Error extracting text: {e}")

    def parse_image(self, cropped_image):
        """OCR processing using EasyOCR"""
        try:
            if cropped_image is None or cropped_image.size == 0:
                return ""

            # Convert image to RGB if needed
            if len(cropped_image.shape) == 2 or cropped_image.shape[2] == 1:
                cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_GRAY2RGB)
            elif cropped_image.shape[2] == 4:
                cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGRA2RGB)
            else:
                cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)

            result = self.reader.readtext(cropped_image, detail=0)
            return ' '.join(result).strip()

        except Exception as e:
            print(f"OCR Error in cropped image processing: {str(e)}")
            return f"OCR Error: {str(e)}"
