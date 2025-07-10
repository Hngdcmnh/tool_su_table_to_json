# PRD QC Table to Template Output Transformer

## Tổng quan

Script này chuyển đổi file input dạng `prd_qc_table.xlsx` thành file output dạng `template_output.xlsx` theo đúng yêu cầu và implementation guideline.

### Các tính năng chính:
- ✅ **Đầy đủ các trường**: Xử lý tất cả các trường từ input bao gồm `image`, `audio`, `voice_speed`, `IMAGE_LISTENING`, `AUDIO_LISTENING`
- ✅ **Logic nối question objects**: Implement đúng quy tắc nối question objects từ question group TIẾP THEO vào response của intent có loop_count max
- ✅ **Intent description unique**: Đảm bảo tất cả intent descriptions đều unique
- ✅ **JSON structure hoàn chỉnh**: Tạo JSON objects với đầy đủ 10 trường required

## Cách sử dụng

### Cách 1: 🐳 Docker Deployment (PRODUCTION - KHUYẾN NGHỊ)
Deploy lên server bằng Docker:

**Development/Testing:**
```bash
# Build và chạy local
./docker-deploy.sh

# Hoặc manual
docker-compose up --build -d
```

**Production Server:**
```bash
# Deploy lên production (port 80)
./deploy-production.sh

# Hoặc manual
docker-compose -f docker-compose.prod.yml up --build -d
```

**Docker Commands:**
```bash
./docker-build.sh        # Build image
./docker-deploy.sh       # Deploy development
./deploy-production.sh   # Deploy production
./docker-stop.sh         # Stop containers
```

**Tính năng Docker:**
- ✅ **Auto port detection**: Tự động tìm port khả dụng
- ✅ **Production ready**: Optimized cho server deployment
- ✅ **Health checks**: Tự động kiểm tra container health
- ✅ **Auto restart**: Tự động restart khi crash
- ✅ **Volume mapping**: Data persistence qua uploads/ directory
- ✅ **Logging**: Centralized logging với rotation

### Cách 2: 🌐 Web Interface (Local Development)
Sử dụng giao diện web để upload file và xem kết quả:

```bash
python3 start_web_app.py
```

**Hoặc:**
```bash
python3 app.py
```

Sau đó truy cập: **http://localhost:5000**

**Tính năng web interface:**
- ✅ **Drag & Drop**: Kéo thả file Excel vào trang web
- ✅ **Preview Table**: Xem kết quả dưới dạng bảng
- ✅ **Copy & Paste**: Click vào từng cell để copy, hoặc copy toàn bộ data
- ✅ **Download Excel**: Tải file Excel đã transform
- ✅ **Real-time Processing**: Xem tiến trình xử lý file
- ✅ **Responsive Design**: Hoạt động trên mọi thiết bị

### Cách 3: Command line
```bash
python3 transform_prd_to_template.py input_file.xlsx [output_file.xlsx]
```

**Ví dụ:**
```bash
python3 transform_prd_to_template.py "prd_qc_table copy.xlsx" my_output.xlsx
```

### Cách 4: Sử dụng trong code
```python
from transform_prd_to_template import PRDTableTransformer

transformer = PRDTableTransformer('input_file.xlsx')
transformer.transform()
transformer.save_output('output_file.xlsx')
```

## Cấu trúc Input file

Input file cần có các columns sau:
- `Section`: "Question" hoặc "Intent_Response"
- `Intent`: Tên intent
- `User_Examples`: Ví dụ input từ user
- `Button`: Loại button
- `Loop`: Số lần lặp
- `Text_Vietnamese`: Nội dung text
- `Mood`: Tên mood
- `Image`: URL/path của image ⭐ **MỚI**
- `Audio`: URL/path của audio ⭐ **MỚI** 
- `Voice_Speed`: Tốc độ đọc ⭐ **MỚI**
- `Servo_Name`: Tên servo
- `Servo_Duration`: Thời gian servo
- `Image_Listening`: Image khi listening ⭐ **MỚI**
- `Audio_Listening`: Audio khi listening ⭐ **MỚI**

## Cấu trúc Output file

Output file có 18 columns theo template:
- `QUESTION`: JSON array của question objects (chỉ cho question rows)
- `INTENT_NAME`: Tên intent (chỉ cho intent rows)
- `INTENT_DESCRIPTION`: Mô tả intent unique
- `BUTTON`: Button value
- `LOOP_COUNT`: Số loop (chỉ cho intent rows)
- `MAX_LOOP`: 2 cho question rows, null cho intent rows
- `RESPONSE_1`: JSON array của response objects **có nối question objects từ question group tiếp theo**
- `IMAGE_LISTENING`: Image listening value
- `AUDIO_LISTENING`: Audio listening value
- Các trường khác: null

## Logic transformation chính

### 1. Question Group Processing
- Gộp các Question rows liền nhau thành 1 output row
- QUESTION = JSON array của tất cả text objects trong group
- MAX_LOOP = 2

### 2. Intent Group Processing
- Group Intent_Response rows theo (Intent, Loop)
- Mỗi group tạo 1 intent output row
- RESPONSE_1 = JSON array của text objects trong group

### 3. **Logic nối Question Objects (QUAN TRỌNG)**
Đối với intent có `loop_count = max_loop` của intent đó:
- Tìm question group TIẾP THEO trong sequence
- Nối question objects từ question group đó vào cuối RESPONSE_1
- **Không** nối từ question group phía trước
- **Chỉ** nối từ question group tiếp theo

Ví dụ sequence:
```
Question Group 1 → Intent Group 1 → Question Group 2 → Intent Group 2
```
- Intent Group 1 có max loop → nối Question Group 2 objects
- Intent Group 2 có max loop → không nối gì (không có question group tiếp theo)

### 4. Text Object Structure
Mỗi text object có đầy đủ 10 trường:
```json
{
  "text": "Nội dung từ Text_Vietnamese",
  "mood": "Mood từ input",
  "image": "Image từ input",
  "video": "",
  "moods": [{"mood_name": "...", "servo_name": "...", "duration": 2000.0}],
  "voice_speed": "Voice_Speed từ input", 
  "text_viewer": "",
  "volume": 1.0,
  "audio": "Audio từ input",
  "model": ""
}
```

### 5. Intent Description Generation
- `silence` intent: null
- `fallback` intent: "User say something not relate to question" + unique suffix
- Có từ khóa affirm: "user affirm" + unique suffix
- Có từ khóa decline: "user decline" + unique suffix
- Khác: "user says something like: [first example]" + unique suffix
- **Đảm bảo unique**: Thêm suffix nếu bị trùng

## Validation

Script tự động validate:
- ✅ Số lượng question rows và intent rows
- ✅ JSON structure hợp lệ
- ✅ Tất cả intent descriptions unique
- ✅ Đúng columns structure như template

## Files trong project

### Core Scripts
- `transform_prd_to_template.py`: **Script transformation chính**
- `implementation_guideline_to_json`: Guideline logic ban đầu

### Web Interface
- `app.py`: **Flask web application**
- `start_web_app.py`: Script khởi động web app (local development)
- `templates/index.html`: Giao diện web HTML
- `uploads/`: Thư mục lưu file upload (tự động tạo)

### 🐳 Docker Deployment
- `Dockerfile`: **Docker image definition**
- `docker-compose.yml`: Development deployment
- `docker-compose.prod.yml`: **Production deployment**
- `requirements.txt`: Python dependencies
- `.dockerignore`: Docker build optimization
- `docker-build.sh`: Build Docker image
- `docker-deploy.sh`: Deploy development
- `deploy-production.sh`: **Deploy to production server**
- `docker-stop.sh`: Stop containers

### Demo & Test
- `quick_test.py`: Demo script test nhanh  
- `test_web_app.py`: Test web app functionality
- `fix_port_issue.py`: Fix port 5000 issues
- `README.md`: Hướng dẫn này

## Kết quả

Với input file `prd_qc_table copy.xlsx` (174 rows):
- ➡️ Output: 135 rows (15 question + 120 intent)
- ✅ 15 question groups được xử lý
- ✅ 120 intent rows với descriptions unique
- ✅ Logic nối question objects hoạt động đúng
- ✅ Tất cả trường image, audio, voice_speed được xử lý

## Troubleshooting

### Dependencies:

**Docker (Production - KHUYẾN NGHỊ):**
```bash
# Chỉ cần Docker và Docker Compose
docker --version
docker-compose --version

# Deploy ngay
./deploy-production.sh
```

**Python (Local Development):**
```bash
pip install pandas openpyxl flask

# Hoặc từ file
pip install -r requirements.txt
```

### Lỗi thường gặp:
1. **FileNotFoundError**: Kiểm tra đường dẫn file input
2. **Pandas ImportError**: Chạy `pip install pandas openpyxl`
3. **Flask ImportError**: Chạy `pip install flask`
4. **JSON Decode Error**: Kiểm tra dữ liệu input có ký tự đặc biệt
5. **Web app không mở**: Thử truy cập thủ công `http://localhost:5000`

### Log output:
Script sẽ hiển thị:
- Số lượng question groups được tìm thấy
- Intent max loops mapping
- "Appending next question group to [Intent] loop [X]" khi nối question objects
- Validation results

## Liên hệ

Nếu có vấn đề hoặc cần hỗ trợ, vui lòng liên hệ team phát triển.

---
**Version**: 1.0  
**Last Updated**: December 2024  
**Compatibility**: Python 3.6+, pandas, openpyxl 