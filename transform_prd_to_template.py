#!/usr/bin/env python3
"""
PRD QC Table to Template Output Transformer
Transforms input files like 'prd_qc_table.xlsx' to output like 'template_output.xlsx'
Complete implementation with all missing fields: image, audio, voice_speed, etc.

Usage: python3 transform_prd_to_template.py input_file.xlsx [output_file.xlsx]
"""

import pandas as pd
import json
import numpy as np
import sys
from collections import defaultdict

class PRDTableTransformer:
    def __init__(self, input_file):
        self.input_file = input_file
        self.df = pd.read_excel(input_file)
        self.output_rows = []
        self.intent_descriptions = set()
        self.question_groups = []
        self.intent_max_loops = {}
        
    def analyze_data(self):
        """Analyze input data structure"""
        print(f"Input file: {self.input_file}")
        print(f"Total rows: {len(self.df)}")
        print(f"Columns: {list(self.df.columns)}")
        
        # Find question groups positions first
        self.scan_question_groups()
        
        # Find max loop for each intent within each question turn
        self.calculate_intent_max_loops_per_turn()
        
    def calculate_intent_max_loops_per_turn(self):
        """Calculate max loop for each intent within question turns"""
        # Store max loops per turn for later use
        self.turn_intent_max_loops = {}
        
        # Process each question turn (from one question group to the next)
        for i in range(len(self.question_groups)):
            turn_start = self.question_groups[i]['end'] + 1  # Start after current question group
            turn_end = self.question_groups[i + 1]['start'] - 1 if i + 1 < len(self.question_groups) else len(self.df) - 1
            
            # Find max loop for each intent within this turn
            turn_intent_loops = defaultdict(list)
            for idx in range(turn_start, turn_end + 1):
                if idx < len(self.df):
                    row = self.df.iloc[idx]
                    if pd.notna(row['Intent']) and pd.notna(row['Loop']):
                        turn_intent_loops[row['Intent']].append(row['Loop'])
            
            # Calculate max loop for each intent in this turn
            turn_max_loops = {}
            for intent, loops in turn_intent_loops.items():
                if loops:
                    turn_max_loops[intent] = max(loops)
            
            # Store turn max loops with turn range info
            self.turn_intent_max_loops[(turn_start, turn_end)] = turn_max_loops
            
        print(f"Intent max loops per turn: {self.turn_intent_max_loops}")
        
        # Keep global max loops for backward compatibility (but use turn-specific logic)
        intent_max_loops = defaultdict(int)
        for turn_range, turn_max_loops in self.turn_intent_max_loops.items():
            for intent, max_loop in turn_max_loops.items():
                intent_max_loops[intent] = max(intent_max_loops[intent], max_loop)
        self.intent_max_loops = dict(intent_max_loops)
        
    def scan_question_groups(self):
        """Scan and identify all question groups in the data"""
        current_group = []
        current_group_start = None
        
        for idx, row in self.df.iterrows():
            if row['Section'] == 'Question':
                if current_group_start is None:
                    current_group_start = idx
                current_group.append(idx)
            else:
                if current_group:
                    # End of question group
                    self.question_groups.append({
                        'start': current_group_start,
                        'end': current_group[-1],
                        'indices': current_group.copy()
                    })
                    current_group = []
                    current_group_start = None
        
        # Handle last group if exists
        if current_group:
            self.question_groups.append({
                'start': current_group_start,
                'end': current_group[-1],
                'indices': current_group.copy()
            })
            
        print(f"Found {len(self.question_groups)} question groups: {[(g['start'], g['end']) for g in self.question_groups]}")
    
    def create_text_object(self, row):
        """Create complete text object with all fields including new ones"""
        # Build moods array
        moods = []
        if pd.notna(row['Mood']) and row['Mood'].strip():
            mood_obj = {
                "mood_name": row['Mood'],
                "servo_name": row['Servo_Name'] if pd.notna(row['Servo_Name']) else "",
                "duration": float(row['Servo_Duration']) if pd.notna(row['Servo_Duration']) else 2000.0
            }
            moods.append(mood_obj)
        
        # Create text object with all fields from input
        text_obj = {
            "text": row['Text_Vietnamese'] if pd.notna(row['Text_Vietnamese']) else "",
            "mood": row['Mood'] if pd.notna(row['Mood']) else "",
            "image": row['Image'] if pd.notna(row['Image']) else "",
            "video": "",  # Not in input, set default
            "moods": moods,
            "voice_speed": float(row['Voice_Speed']) if pd.notna(row['Voice_Speed']) else "",
            "text_viewer": "",  # Not in input, set default
            "volume": 1.0,  # Default value
            "audio": row['Audio'] if pd.notna(row['Audio']) else "",
            "model": ""  # Default value
        }
        
        return text_obj
    
    def generate_unique_intent_description(self, intent_name, user_examples, loop_count):
        """Generate unique intent description based on guidelines"""
        if intent_name.lower() == 'silence':
            return None
            
        base_description = ""
        
        if intent_name.lower() == 'fallback':
            base_description = "User say something not relate to question"
        elif user_examples and pd.notna(user_examples):
            examples_lower = str(user_examples).lower()
            # Check for affirm keywords
            if any(word in examples_lower for word in ['yes', 'đồng ý', 'ok', 'được', 'affirm', 'tôi sẽ giúp', 'i will help', 'có']):
                base_description = "user affirm"
            # Check for decline keywords
            elif any(word in examples_lower for word in ['no', 'không', 'từ chối', 'không muốn', 'no way', 'not', 'chưa']):
                base_description = "user decline"
            else:
                # Use first example
                first_example = str(user_examples).split(',')[0].strip()
                base_description = f"user says something like: {first_example}"
        else:
            return None
            
        # Make unique if already exists
        description = base_description
        counter = 1
        while description in self.intent_descriptions:
            description = f"{base_description} - {intent_name.lower()} loop {loop_count}"
            if description in self.intent_descriptions:
                description = f"{base_description} - variant {counter}"
                counter += 1
                
        self.intent_descriptions.add(description)
        return description
    
    def find_next_question_group(self, current_position):
        """Find the next question group after current position"""
        for group in self.question_groups:
            if group['start'] > current_position:
                return group
        return None
    
    def process_question_group(self, group_indices):
        """Process a group of consecutive question rows"""
        question_objects = []
        button_value = None
        image_listening = None
        audio_listening = None
        
        for idx in group_indices:
            row = self.df.iloc[idx]
            text_obj = self.create_text_object(row)
            question_objects.append(text_obj)
            
            # Get values from any row in group
            if pd.notna(row['Button']) and button_value is None:
                button_value = row['Button']
            if pd.notna(row['Image_Listening']) and image_listening is None:
                image_listening = row['Image_Listening']
            if pd.notna(row['Audio_Listening']) and audio_listening is None:
                audio_listening = row['Audio_Listening']
        
        # Create question output row
        question_row = {
            'QUESTION': json.dumps(question_objects, ensure_ascii=False, indent=2),
            'INTENT_NAME': None,
            'INTENT_DESCRIPTION': None,
            'BUTTON': button_value,
            'TRIGGER': None,
            'LOOP_COUNT': None,
            'MAX_LOOP': 2,
            'LANGUAGE': None,
            'LLM_ANSWERING': None,
            'SCORE': None,
            'RESPONSE_1': None,
            'IMAGE_LISTENING': image_listening,
            'AUDIO_LISTENING': audio_listening,
            'PRONUNCIATION_CHECKER_TOOL': None,
            'GRAMMAR_CHECKER_TOOL': None,
            'LISTENING_ANIMATIONS': None,
            'REGEX_POSITIVE': None,
            'REGEX_NEGATIVE': None
        }
        
        return question_row
    
    def process_intent_group(self, intent_name, intent_rows, next_question_group=None, current_turn_range=None):
        """Process a group of intent rows with same Intent, grouped by Loop"""
        # Group by Loop
        loop_groups = defaultdict(list)
        for row in intent_rows:
            loop_groups[row['Loop']].append(row)
        
        intent_output_rows = []
        
        # Get max loop for this intent in current turn
        turn_max_loop = 0
        if current_turn_range and current_turn_range in self.turn_intent_max_loops:
            turn_max_loop = self.turn_intent_max_loops[current_turn_range].get(intent_name, 0)
        
        for loop_count, rows in loop_groups.items():
            # Create response objects
            response_objects = []
            button_value = None
            user_examples = None
            image_listening = None
            audio_listening = None
            
            for row in rows:
                text_obj = self.create_text_object(row)
                response_objects.append(text_obj)
                
                # Get values from any row in loop group
                if pd.notna(row['Button']) and button_value is None:
                    button_value = row['Button']
                if pd.notna(row['User_Examples']) and user_examples is None:
                    user_examples = row['User_Examples']
                if pd.notna(row['Image_Listening']) and image_listening is None:
                    image_listening = row['Image_Listening']
                if pd.notna(row['Audio_Listening']) and audio_listening is None:
                    audio_listening = row['Audio_Listening']
            
            # IMPORTANT: If this is max loop intent IN CURRENT TURN, append next question objects
            is_max_loop = (loop_count == turn_max_loop)
            if is_max_loop and next_question_group and turn_max_loop > 0:
                print(f"Appending next question group to {intent_name} loop {loop_count} (turn max: {turn_max_loop})")
                # Add question objects from next group
                for idx in next_question_group['indices']:
                    next_row = self.df.iloc[idx]
                    next_text_obj = self.create_text_object(next_row)
                    response_objects.append(next_text_obj)
            
            # Generate unique intent description
            intent_description = self.generate_unique_intent_description(
                intent_name, user_examples, loop_count
            )
            
            # Create intent output row
            intent_row = {
                'QUESTION': None,
                'INTENT_NAME': intent_name.lower() if intent_name.lower() in ['fallback', 'silence'] else intent_name,
                'INTENT_DESCRIPTION': intent_description,
                'BUTTON': button_value,
                'TRIGGER': None,
                'LOOP_COUNT': loop_count,
                'MAX_LOOP': None,
                'LANGUAGE': None,
                'LLM_ANSWERING': None,
                'SCORE': None,
                'RESPONSE_1': json.dumps(response_objects, ensure_ascii=False, indent=2),
                'IMAGE_LISTENING': image_listening,
                'AUDIO_LISTENING': audio_listening,
                'PRONUNCIATION_CHECKER_TOOL': None,
                'GRAMMAR_CHECKER_TOOL': None,
                'LISTENING_ANIMATIONS': None,
                'REGEX_POSITIVE': None,
                'REGEX_NEGATIVE': None
            }
            
            intent_output_rows.append(intent_row)
        
        return intent_output_rows
    
    def transform(self):
        """Main transformation logic implementing guidelines"""
        self.analyze_data()
        
        current_idx = 0
        
        while current_idx < len(self.df):
            row = self.df.iloc[current_idx]
            
            if row['Section'] == 'Question':
                # Find current question group
                current_question_group = None
                for group in self.question_groups:
                    if current_idx in group['indices']:
                        current_question_group = group
                        break
                
                if current_question_group:
                    # Process question group
                    question_row = self.process_question_group(current_question_group['indices'])
                    self.output_rows.append(question_row)
                    
                    # Skip to end of question group
                    current_idx = current_question_group['end'] + 1
                else:
                    current_idx += 1
                    
            elif row['Section'] == 'Intent_Response':
                # Find all consecutive intent rows with same intent
                intent_name = row['Intent']
                intent_rows = []
                
                while (current_idx < len(self.df) and 
                       self.df.iloc[current_idx]['Section'] == 'Intent_Response' and
                       self.df.iloc[current_idx]['Intent'] == intent_name):
                    intent_rows.append(self.df.iloc[current_idx])
                    current_idx += 1
                
                # Find next question group for appending (critical logic)
                next_question_group = self.find_next_question_group(current_idx - 1)
                
                # Find current turn range for max loop calculation
                current_turn_range = None
                intent_start_position = intent_rows[0].name if intent_rows else current_idx - 1
                for turn_range in self.turn_intent_max_loops.keys():
                    turn_start, turn_end = turn_range
                    if turn_start <= intent_start_position <= turn_end:
                        current_turn_range = turn_range
                        break
                
                # Process intent group
                intent_output_rows = self.process_intent_group(
                    intent_name, intent_rows, next_question_group, current_turn_range
                )
                self.output_rows.extend(intent_output_rows)
            else:
                current_idx += 1
        
        return self.output_rows
    
    def save_output(self, output_file):
        """Save transformed data to Excel"""
        if not self.output_rows:
            print("No output data to save")
            return
            
        output_df = pd.DataFrame(self.output_rows)
        output_df.to_excel(output_file, index=False)
        print(f"Saved output to {output_file}")
        print(f"Output shape: {output_df.shape}")
        
        # Validation
        print("\n=== VALIDATION ===")
        question_rows = output_df[output_df['QUESTION'].notna()]
        intent_rows = output_df[output_df['INTENT_NAME'].notna()]
        print(f"Question rows: {len(question_rows)}")
        print(f"Intent rows: {len(intent_rows)}")
        print(f"Total rows: {len(output_df)}")
        
        # Check unique descriptions
        descriptions = intent_rows['INTENT_DESCRIPTION'].dropna().tolist()
        unique_descriptions = set(descriptions)
        if len(descriptions) != len(unique_descriptions):
            print("WARNING: Duplicate intent descriptions found!")
            duplicates = [desc for desc in descriptions if descriptions.count(desc) > 1]
            print(f"Duplicates: {set(duplicates)}")
        else:
            print("✓ All intent descriptions are unique")

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python3 transform_prd_to_template.py input_file.xlsx [output_file.xlsx]")
        print("Example: python3 transform_prd_to_template.py prd_qc_table.xlsx template_output.xlsx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"transformed_{input_file}"
    
    print(f"=== PRD QC TABLE TRANSFORMER ===")
    print(f"Input: {input_file}")
    print(f"Output: {output_file}")
    
    try:
        transformer = PRDTableTransformer(input_file)
        transformer.transform()
        transformer.save_output(output_file)
        
        print("\n=== TRANSFORMATION COMPLETE ===")
        print(f"✓ Successfully transformed {input_file} to {output_file}")
        print("The output includes all fields: image, audio, voice_speed, IMAGE_LISTENING, AUDIO_LISTENING")
        
    except Exception as e:
        print(f"Error during transformation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 