#!/usr/bin/env python3
"""
Flask Web Application for PRD QC Table Transformation
Upload Excel file and display results in a table for copy-paste
"""

from flask import Flask, request, render_template, jsonify, send_file
import pandas as pd
import os
import json
from werkzeug.utils import secure_filename
from transform_prd_to_template import PRDTableTransformer
import tempfile
from datetime import datetime
from utils_validate import validate_image_jpg

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Transform the file
            transformer = PRDTableTransformer(filepath)
            output_rows = transformer.transform()
            
            # Validate: Image link must end with .jpg
            image_errors = validate_image_jpg(output_rows)
            if image_errors:
                return jsonify({'error': 'Validation failed', 'details': image_errors}), 400
            
            if not output_rows:
                return jsonify({'error': 'No data to transform'}), 400
            
            # Convert to DataFrame for easier handling
            df = pd.DataFrame(output_rows)
            
            # Convert DataFrame to HTML table data
            table_data = {
                'columns': df.columns.tolist(),
                'rows': []
            }
            
            for _, row in df.iterrows():
                row_data = []
                for col in df.columns:
                    value = row[col]
                    if pd.isna(value):
                        row_data.append('')
                    elif isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                        # Pretty format JSON
                        try:
                            json_obj = json.loads(value)
                            formatted_json = json.dumps(json_obj, ensure_ascii=False, indent=2)
                            row_data.append(formatted_json)
                        except:
                            row_data.append(str(value))
                    else:
                        row_data.append(str(value))
                table_data['rows'].append(row_data)
            
            # Save output file for download
            output_filename = f"transformed_{timestamp}_{filename}"
            output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            df.to_excel(output_filepath, index=False)
            
            # Clean up input file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'table_data': table_data,
                'download_url': f'/download/{output_filename}',
                'stats': {
                    'total_rows': len(df),
                    'question_rows': len(df[df['QUESTION'].notna()]),
                    'intent_rows': len(df[df['INTENT_NAME'].notna()])
                }
            })
        
        else:
            return jsonify({'error': 'Invalid file type. Please upload .xlsx or .xls files only.'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'File not found: {str(e)}'}), 404

@app.route('/clear')
def clear_files():
    """Clean up old files"""
    try:
        upload_dir = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return jsonify({'success': True, 'message': 'All files cleared'})
    except Exception as e:
        return jsonify({'error': f'Error clearing files: {str(e)}'}), 500

def find_free_port():
    """Find a free port to run the server"""
    import socket
    for port in [5000, 8000, 8080, 3000, 5001, 8001]:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return 5000  # fallback

if __name__ == '__main__':
    # Check if running in Docker
    import os
    is_docker = os.path.exists('/.dockerenv')
    
    if is_docker:
        # Production mode in Docker
        print("🐳 Starting PRD QC Table Transformer in Docker...")
        print("🌐 Server will be available on port 5000")
        app.run(debug=False, host='0.0.0.0', port=5000)
    else:
        # Development mode
        port = find_free_port()
        print("🚀 Starting PRD QC Table Transformer Web App...")
        print("📁 Upload your prd_qc_table.xlsx file")
        print("📊 View results in table format")
        print("💾 Download transformed Excel file")
        print(f"🌐 Access at: http://localhost:{port}")
        if port != 5000:
            print(f"💡 Note: Using port {port} (5000 was busy)")
        app.run(debug=True, host='0.0.0.0', port=port) 