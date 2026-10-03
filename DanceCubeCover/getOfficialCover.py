import requests
import os
import json
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

# Output file path
output_file = './CoverData'

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
existing_ids = {item["MusicID"] for item in existing_data}

url = f"https://dancedemo.shenghuayule.com/Dance/api/User/GetMusicRankingNew?musicIndex=1&keyword=&page=1&pagesize=15"
response = requests.request("GET", url, headers=headers, data=payload)

try:
    # Parse JSON response directly from the URL
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
except json.JSONDecodeError:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to decode JSON response.")

# Combine existing data with new data
music_data.extend(existing_data)

# Sort the collected data by MusicID
music_data = sorted(music_data, key=lambda x: x["MusicID"])

# Save the updated data back to the JSON file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(music_data, f, ensure_ascii=False, indent=4)

print(f"Data updated and saved to {output_file}")

# Record the end time
end_time = time.time()

# Output the total runtime
print(f"Total runtime: {end_time - start_time:.2f} seconds")
