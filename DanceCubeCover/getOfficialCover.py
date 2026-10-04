import requests
import os
import json
import subprocess
from datetime import datetime
import time

payload = {}
headers = {}

# Record the start time
start_time = time.time()

# Initialize a list to store the data
music_data = []
# Initialize a set to track unique MusicIDs
unique_music_ids = set()

# Use the repository-relative location to ensure the output is saved inside the repo tree.
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, os.pardir))
output_dir = os.path.join(repo_root, 'DanceCubeCover')
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'CoverData')


def try_git_commit_and_push():
    """Attempt to commit and push the generated JSON file if running inside a git repo."""
    try:
        git_check = subprocess.run(
            ['git', '-C', repo_root, 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            check=True,
        )
        if git_check.stdout.strip() != 'true':
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Git repo check failed, skip commit.")
            return

        subprocess.run(['git', '-C', repo_root, 'add', 'DanceCubeCover/CoverData.json'], check=True)

        status = subprocess.run(
            ['git', '-C', repo_root, 'diff', '--cached', '--quiet', '--', 'DanceCubeCover/CoverData.json'],
            capture_output=True,
            text=True,
            check=False,
        )
        if status.returncode == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No file changes to commit.")
            return

        subprocess.run(
            ['git', '-C', repo_root, 'config', 'user.name', 'GitHub Action'],
            check=False,
        )
        subprocess.run(
            ['git', '-C', repo_root, 'config', 'user.email', 'action@github.com'],
            check=False,
        )
        subprocess.run(
            ['git', '-C', repo_root, 'commit', '-m', 'Update cover data'],
            check=False,
        )
        subprocess.run(
            ['git', '-C', repo_root, 'push'],
            check=False,
        )
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Commit/push step completed or skipped intentionally.")
    except Exception as exc:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Git commit/push skipped: {exc}")


# Check if the output file already exists
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
else:
    existing_data = []

# Merge existing data with new data, avoiding duplicates
existing_ids = {item["MusicID"] for item in existing_data if isinstance(item, dict) and "MusicID" in item}

url = "https://dancedemo.shenghuayule.com/Dance/api/User/GetMusicRankingNew?musicIndex=1&keyword=&page=1&pagesize=15"
response = requests.request("GET", url, headers=headers, data=payload)

try:
    response.raise_for_status()
    data = response.json()

    # Extract MusicID and Cover
    for item in data.get("List", []):
        music_id = item.get("MusicID")
        cover_url = item.get("Cover")

        if music_id and cover_url and music_id not in unique_music_ids and music_id not in existing_ids:
            # Remove the "/200" suffix from the Cover URL
            cover_url = cover_url.rsplit('/200', 1)[0]

            # Append the MusicID and Cover URL to the list
            music_data.append({"MusicID": music_id, "CoverURL": cover_url})
            # Add the MusicID to the set
            unique_music_ids.add(music_id)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ Stored: MusicID={music_id}, CoverURL={cover_url}")
except (json.JSONDecodeError, requests.RequestException) as exc:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to decode JSON response or request failed: {exc}")

# Combine existing data with new data
music_data.extend(existing_data)

# Sort the collected data by MusicID
music_data = sorted(music_data, key=lambda x: x["MusicID"])

# Save the updated data back to the JSON file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(music_data, f, ensure_ascii=False, indent=4)

print(f"Data updated and saved to {output_file}")

# Attempt to automatically commit and push if this is a git repo and credentials are available.
try_git_commit_and_push()

# Record the end time
end_time = time.time()

# Output the total runtime
print(f"Total runtime: {end_time - start_time:.2f} seconds")
