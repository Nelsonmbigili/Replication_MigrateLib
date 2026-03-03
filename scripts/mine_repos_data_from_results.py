import os
import yaml
from pathlib import Path
from libmig_eval.util.models import decode_mig_id

# Create yaml files from Results for mining repos
results_path = Path("../results")
mig_db_included = Path("../replicationResults/mig_db/included")

for folder_name in os.listdir(results_path):
    if "__" in folder_name: 
        try:
            repo, commit, src, tgt = decode_mig_id(folder_name)
            meta = {
                "id": folder_name,
                "repo": repo,
                "commit": commit,
                "source": src,
                "target": tgt
            }
            with open(mig_db_included / f"{folder_name}.yaml", "w") as f:
                yaml.dump(meta, f)
        except:
            continue
print(f"Created {len(os.listdir(mig_db_included))} migration definitions.")