import argparse
import json
import os
import re
import sys

def parse_weight(weight_str: str) -> float:
    """
    Parses a weight string and converts it into grams.
    Handles formats like '126g', '0.126KG'.
    """
    if not weight_str:
        return 0.0
        
    match = re.match(r"([\d\.]+)\s*(KG|G)", weight_str.strip().upper())
    if not match:
        raise ValueError(f"Unrecognised weight format: {weight_str}")
    
    value = float(match.group(1))
    unit = match.group(2)
    
    # Standardize to grams for step 7
    if unit == "KG":
        return value * 1000.0
    return value

def process_formulas(file_paths: list, output_dir: str):
    """Processes a list of JSON files and their paths generating a summary report."""
    total_files = 0
    total_instructions = 0
    equipment = set()
    materials = set()
    total_expected_weight = 0.0
    total_actual_weight = 0.0

    for file_path in file_paths:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            total_files += 1
            
            expected_str = data.get('metadata', {}).get('expected_weight', '0g')
            total_expected_weight += parse_weight(expected_str)
            
            for instr in data.get('instructions', []):
                total_instructions += 1
                
                if 'equipment' in instr:
                    equipment.update(instr['equipment'])
                if 'material' in instr:
                    materials.add(instr['material'])
                if 'weight_added' in instr:
                    total_actual_weight += parse_weight(instr['weight_added'])
                    
        except FileNotFoundError:
            print(f"Error: File not found -> {file_path}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in -> {file_path}", file=sys.stderr)
        except ValueError as ve:
            print(f"Data Error in {file_path}: {ve}", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error processing {file_path}: {e}", file=sys.stderr)
    generate_report(total_files, total_instructions, equipment, materials, 
                    total_expected_weight, total_actual_weight, output_dir)

def generate_report(files, instructions, equip_set, mat_set, expected_wt, actual_wt, out_dir):
    """Formats and writes the parsed data to summary.txt"""
    equip_list = f"[{', '.join(sorted(list(equip_set)))}]"
    mat_list = f"[{', '.join(sorted(list(mat_set)))}]"
    
    report_lines = [
        "Summary",
        f"Total files processed: {files}",
        f"Total instructions: {instructions}",
        f"Equipment: {equip_list}",
        f"Materials: {mat_list}",
        f"Total expected weight in grams: {expected_wt:g}",
        f"Total weight actuallyadded in grams: {actual_wt:g}"
    ]
    
    # checks for variance at 5% threshold 
    if expected_wt > 0:
        variance = abs(actual_wt - expected_wt) / expected_wt
        if variance > 0.05:
            report_lines.append("Warning: actual weight differs from expected weight by more than 5%")

    report_text = "\n".join(report_lines)
    
    out_path = os.path.join(out_dir, "summary.txt") if out_dir else "summary.txt"
    
    try:
        with open(out_path, 'w') as out_file:
            out_file.write(report_text)
        print(f"Success! Summary written to: {out_path}")
    except IOError as e:
        print(f"Error writing to output directory: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse lab formulation JSON files.")
    parser.add_argument("input_files", nargs="+", help="Paths to the JSON files")
    parser.add_argument("--out", dest="output_dir", default="", help="Optional output directory for summary.txt")
    
    args = parser.parse_args()
    process_formulas(args.input_files, args.output_dir)