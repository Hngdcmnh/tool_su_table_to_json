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
                    if image_name:
                        if ' ' in image_name:
                            errors.append(f"Row {i+1} (QUESTION, item {idx+1}): Image name must not contain spaces: {image_name}")
                        elif not (image_name.lower().endswith('.jpg') or image_name.lower().endswith('.gif')):
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
                    if image_name:
                        if ' ' in image_name:
                            errors.append(f"Row {i+1} (RESPONSE_1, item {idx+1}): Image name must not contain spaces: {image_name}")
                        elif not (image_name.lower().endswith('.jpg') or image_name.lower().endswith('.gif')):
                            errors.append(f"Row {i+1} (RESPONSE_1, item {idx+1}): Image name must end with .jpg or .gif: {image_name}")
            except Exception:
                pass
    return errors 

def validate_question_intent_pattern(output_rows, debug=False):
    """
    Kiểm tra pattern hợp lệ sau mỗi Question/Section:
    - Mỗi nhóm Question-Intent_Response phải có đủ cả 'fallback' và 'silence'
    
    Args:
        output_rows (list): Danh sách các dòng dữ liệu (dict hoặc list)
        debug (bool): Có in thông tin debug không
    
    Returns:
        dict: {
            'errors': list,           # Danh sách lỗi
            'total_questions': int,   # Tổng số question
            'valid_questions': int,   # Số question hợp lệ
            'question_details': list  # Chi tiết từng question
        }
    
    Quy tắc hợp lệ:
        ✅ Question → fast_response → fallback → silence
        ✅ Question → fast_response → silence → fallback  
        ✅ Question → fallback → silence
        ✅ Question → silence → fallback
        
        ❌ Question → fast_response → fallback (thiếu silence)
        ❌ Question → fast_response → silence (thiếu fallback)
        ❌ Question → fast_response (thiếu cả fallback và silence)
    """
    errors = []
    question_details = []
    n = len(output_rows)
    
    if debug:
        print(f"🔍 Bắt đầu validation với {n} dòng dữ liệu")
    
    i = 0
    while i < n:
        row = output_rows[i]
        
        # ===== BƯỚC 1: Nhận dạng Question/Section =====
        is_question = False
        question_content = None
        question_type = None
        
        if isinstance(row, dict):
            # Kiểm tra nhiều key có thể có
            for key in ['QUESTION', 'Question', 'question', 'SECTION', 'Section', 'section']:
                if row.get(key) is not None and str(row.get(key)).strip():
                    is_question = True
                    question_content = str(row.get(key)).strip()
                    question_type = key.lower()
                    break
                    
        elif isinstance(row, list) and len(row) > 0:
            first_col = str(row[0]).strip().lower()
            if first_col in ['question', 'section']:
                is_question = True
                question_content = str(row[1]).strip() if len(row) > 1 else 'Unknown'
                question_type = first_col
        
        if is_question:
            if debug:
                print(f"\n📋 Tìm thấy {question_type} tại dòng {i+1}: '{question_content}'")
            
            # ===== BƯỚC 2: Thu thập Intent_Response =====
            j = i + 1
            intent_group = []
            intent_details = []
            
            while j < n:
                next_row = output_rows[j]
                
                # Kiểm tra có phải question/section mới không
                is_next_question = False
                if isinstance(next_row, dict):
                    for key in ['QUESTION', 'Question', 'question', 'SECTION', 'Section', 'section']:
                        if next_row.get(key) is not None and str(next_row.get(key)).strip():
                            is_next_question = True
                            break
                elif isinstance(next_row, list) and len(next_row) > 0:
                    first_col = str(next_row[0]).strip().lower()
                    if first_col in ['question', 'section']:
                        is_next_question = True
                
                if is_next_question:
                    break  # Gặp question/section mới thì dừng
                
                # Lấy intent name
                intent_name = None
                is_intent_response = False
                
                if isinstance(next_row, dict):
                    keys = list(next_row.keys())
                    if len(keys) > 0:
                        first_col_value = str(next_row.get(keys[0], '')).strip().lower()
                        # Kiểm tra nhiều pattern có thể có
                        if any(pattern in first_col_value for pattern in ['intent_response', 'intent', 'response']):
                            is_intent_response = True
                            # Tìm intent name trong các cột/key có thể
                            if len(keys) > 1:
                                intent_name = next_row.get(keys[1])
                            if not intent_name:
                                for intent_key in ['Intent', 'INTENT', 'intent', 'Intent_Name', 'INTENT_NAME']:
                                    if next_row.get(intent_key):
                                        intent_name = next_row.get(intent_key)
                                        break
                                        
                elif isinstance(next_row, list) and len(next_row) > 0:
                    first_col_value = str(next_row[0]).strip().lower()
                    if any(pattern in first_col_value for pattern in ['intent_response', 'intent', 'response']):
                        is_intent_response = True
                        if len(next_row) > 1:
                            intent_name = next_row[1]
                
                if is_intent_response and intent_name and str(intent_name).strip():
                    clean_intent = str(intent_name).strip().lower()
                    intent_group.append(clean_intent)
                    intent_details.append({
                        'row': j + 1,
                        'intent': clean_intent,
                        'raw_value': str(intent_name).strip()
                    })
                    if debug:
                        print(f"  ✓ Intent tại dòng {j+1}: '{clean_intent}'")
                
                j += 1
            
            # ===== BƯỚC 3: Validation =====
            question_detail = {
                'row': i + 1,
                'question': question_content,
                'type': question_type,
                'intents': intent_group.copy(),
                'intent_details': intent_details.copy(),
                'is_valid': True,
                'missing': [],
                'has_intents': len(intent_group) > 0
            }
            
            # Chỉ kiểm tra khi có ít nhất 1 intent
            if intent_group:
                intent_set = set(intent_group)
                
                # Kiểm tra thiếu fallback và silence
                missing = []
                if 'fallback' not in intent_set:
                    missing.append('fallback')
                if 'silence' not in intent_set:
                    missing.append('silence')
                
                if missing:
                    question_detail['is_valid'] = False
                    question_detail['missing'] = missing
                    
                    # Tạo thông báo lỗi chi tiết
                    error_msg = (
                        f"❌ {question_type.title()} '{question_content}' tại dòng {i+1} "
                        f"thiếu: {', '.join(missing)} "
                        f"(có: {', '.join(sorted(intent_group))})"
                    )
                    errors.append(error_msg)
                    
                    if debug:
                        print(f"  ❌ KHÔNG HỢP LỆ - Thiếu: {', '.join(missing)}")
                else:
                    if debug:
                        print(f"  ✅ HỢP LỆ - Có đủ fallback và silence")
            else:
                if debug:
                    print(f"  ⚠️  Không có Intent nào - Bỏ qua kiểm tra")
            
            question_details.append(question_detail)
        
        i += 1
    
    # ===== BƯỚC 4: Tổng kết =====
    total_questions = len(question_details)
    valid_questions = sum(1 for q in question_details if q['is_valid'])
    
    result = {
        'errors': errors,
        'total_questions': total_questions,
        'valid_questions': valid_questions,
        'invalid_questions': total_questions - valid_questions,
        'question_details': question_details,
        'success_rate': valid_questions / total_questions * 100 if total_questions > 0 else 100
    }
    
    if debug:
        print(f"\n📊 KẾT QUA TỔNG KẾT:")
        print(f"   • Tổng questions: {total_questions}")
        print(f"   • Hợp lệ: {valid_questions}")
        print(f"   • Không hợp lệ: {total_questions - valid_questions}")
        print(f"   • Tỷ lệ thành công: {result['success_rate']:.1f}%")
        print(f"   • Tổng lỗi: {len(errors)}")
    
    return result

