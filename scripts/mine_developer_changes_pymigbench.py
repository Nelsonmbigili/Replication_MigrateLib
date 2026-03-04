import os
import yaml
import requests
import glob

SOURCE_DIR = "../datasets"
OUTPUT_BASE_DIR = "../replicationResults/RQ1.1"

def download_file(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"  [!] Failed to download. Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"  [!] Error: {e}")
        return None

def process_all_yamls():
    if not os.path.exists(OUTPUT_BASE_DIR):
        os.makedirs(OUTPUT_BASE_DIR)

    yaml_files = glob.glob(os.path.join(SOURCE_DIR, "*.yaml"))
    
    if not yaml_files:
        print(f"No YAML files found in {SOURCE_DIR}")
        return

    for yaml_path in yaml_files:
        with open(yaml_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(f"Error parsing {yaml_path}: {exc}")
                continue

        repo = data.get('repo')
        commit_sha = data.get('commit')
        
        yaml_basename = os.path.splitext(os.path.basename(yaml_path))[0]
        target_folder = os.path.join(OUTPUT_BASE_DIR, yaml_basename)
        
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        print(f"--- Processing: {yaml_basename} ---")

        for file_info in data.get('files', []):
            file_path = file_info['path']
            filename = os.path.basename(file_path)
            
            after_url = f"https://raw.githubusercontent.com/{repo}/{commit_sha}/{file_path}"
            before_url = f"https://raw.githubusercontent.com/{repo}/{commit_sha}^/{file_path}"

            # Process After version
            print(f"  Fetching 'After': {filename}")
            after_code = download_file(after_url)
            if after_code:
                with open(os.path.join(target_folder, f"after_{filename}"), 'w', encoding='utf-8') as f:
                    f.write(after_code)

            # Process Before version
            print(f"  Fetching 'Before': {filename}")
            before_code = download_file(before_url)
            if before_code:
                with open(os.path.join(target_folder, f"before_{filename}"), 'w', encoding='utf-8') as f:
                    f.write(before_code)

if __name__ == "__main__":
    process_all_yamls()
    print(f"\nDone! Check the {OUTPUT_BASE_DIR} folder.")