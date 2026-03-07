import os
import glob
import shutil

SOURCE_DIR = "../datasets/utils/selected"        
LLM_MIGRATIONS_DIR = "/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/LLMMig-artifacts/LLMMig-results/mini/10"                   
OUTPUT_BASE_DIR = "../replicationResults/RQ1.1/selectedLlmChanges"

def copy_selected_folders():
    if not os.path.exists(OUTPUT_BASE_DIR):
        os.makedirs(OUTPUT_BASE_DIR)

    yaml_paths = glob.glob(os.path.join(SOURCE_DIR, "*.yaml"))
    
    for yaml_path in yaml_paths:
        folder_id = os.path.splitext(os.path.basename(yaml_path))[0]
        
        src_folder = os.path.join(LLM_MIGRATIONS_DIR, folder_id)
        dst_folder = os.path.join(OUTPUT_BASE_DIR, folder_id)

        if os.path.isdir(src_folder):
            print(f"Copying: {folder_id}...")
            shutil.copytree(src_folder, dst_folder, dirs_exist_ok=True)
        else:
            print(f"[!] Folder not found for ID: {folder_id}")

if __name__ == "__main__":
    copy_selected_folders()
    print("\nAll matching folders have been copied.")