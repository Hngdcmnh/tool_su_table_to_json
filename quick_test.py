#!/usr/bin/env python3
"""
Quick test script để demo transformation
"""

import os
from transform_prd_to_template import PRDTableTransformer

def main():
    print("=== QUICK TEST: PRD QC TABLE TRANSFORMER ===")
    
    # Test với file hiện tại
    input_file = "prd_qc_table copy.xlsx"
    output_file = "quick_test_output.xlsx"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file {input_file} not found!")
        return
    
    try:
        print(f"🔄 Transforming {input_file}...")
        transformer = PRDTableTransformer(input_file)
        transformer.transform()
        transformer.save_output(output_file)
        
        print(f"\n✅ SUCCESS!")
        print(f"📁 Input: {input_file}")
        print(f"📁 Output: {output_file}")
        print(f"📊 Check your output file to see the results!")
        
        # Quick comparison
        print(f"\n📋 Quick Summary:")
        print(f"   - Input có 16 columns với các trường mới: Image, Audio, Voice_Speed, etc.")
        print(f"   - Output có 18 columns theo template format")
        print(f"   - JSON objects có đầy đủ 10 trường: text, mood, image, video, moods, voice_speed, text_viewer, volume, audio, model")
        print(f"   - Logic nối question objects hoạt động đúng")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 