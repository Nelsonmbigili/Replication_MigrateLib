import os
import yaml
import shutil
import csv

# Configuration
SOURCE_DIR = "../datasets/pymigbench"
SELECTED_DIR = "../datasets/utils/selected"
CSV_FILE = "../datasets/utils/selected_migs.csv"

def filter_and_copy_yamls():
    if not os.path.exists(SELECTED_DIR):
        os.makedirs(SELECTED_DIR)
        print(f"Created directory: {SELECTED_DIR}")

    target_migs = set()
    
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        return

    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mig_id = row['mig'].replace('/', '@')
            target_migs.add(mig_id)

    print(f"Found {len(target_migs)} unique migrations in CSV.")

    yaml_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.yaml')]
    
    count = 0
    for filename in yaml_files:
        file_base = os.path.splitext(filename)[0]
        
        if file_base in target_migs:
            source_path = os.path.join(SOURCE_DIR, filename)
            dest_path = os.path.join(SELECTED_DIR, filename)
            
            try:
                shutil.copy2(source_path, dest_path)
                count += 1
                print(f" Copied: {filename}")
            except Exception as e:
                print(f" Error copying {filename}: {e}")

    print(f"\nDone! Copied {count} files to {SELECTED_DIR}")

if __name__ == "__main__":
    filter_and_copy_yamls()