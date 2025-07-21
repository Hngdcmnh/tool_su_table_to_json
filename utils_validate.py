import json

def validate_image_jpg(output_rows):
    errors = []
    for i, row in enumerate(output_rows):
        # Kiểm tra cột QUESTION (nếu có)
        question_json = row.get('QUESTION')
        if question_json:
            try:
                question_objs = json.loads(question_json)
                for idx, obj in enumerate(question_objs):
                    image_name = obj.get('image', '')
                    if image_name and not (image_name.lower().endswith('.jpg') or image_name.lower().endswith('.gif')):
                        errors.append(f"Row {i+1} (QUESTION, item {idx+1}): Image name must end with .jpg or .gif: {image_name}")
            except Exception:
                pass
        # Kiểm tra cột RESPONSE_1 (nếu có)
        response_json = row.get('RESPONSE_1')
        if response_json:
            try:
                response_objs = json.loads(response_json)
                for idx, obj in enumerate(response_objs):
                    image_name = obj.get('image', '')
                    if image_name and not (image_name.lower().endswith('.jpg') or image_name.lower().endswith('.gif')):
                        errors.append(f"Row {i+1} (RESPONSE_1, item {idx+1}): Image name must end with .jpg or .gif: {image_name}")
            except Exception:
                pass
    return errors 