import json

# Function to extract season number from episode data
# This needs to be adjusted based on actual season breaks
def get_season_number(episode_number):
    if episode_number <= 13:
        return 1
    elif episode_number <= 26:
        return 2
    elif episode_number <= 39:
        return 3
    elif episode_number <= 52:
        return 4
    elif episode_number <= 65:
        return 5
    elif episode_number <= 78:
        return 6
    elif episode_number <= 91:
        return 7
    elif episode_number <= 104:
        return 8
    elif episode_number <= 117:
        return 9
    else:
        return 10

# Read the data from input.txt
# Read the data from input.txt
with open('input.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()[1:]  # Skip the first line

episodes = []
for line in lines:
    parts = line.strip().split('\t')
    if len(parts) < 4:  # Skip any lines that don't have enough data
        continue
    episode_number, title, premiere, viewership = parts
    viewership = viewership.replace(" ", "").replace("[1]", "")  # Remove spaces and footnote references
    try:
        episodes.append({
            "episode_number": int(episode_number),
            "title": title,
            "premiere_date": premiere,
            "viewership": int(viewership)
        })
    except ValueError:
        continue  # Skip lines where episode_number is not a number

# Rest of your code...

# Organize episodes into seasons
seasons = {}
for episode in episodes:
    season_number = get_season_number(episode["episode_number"])
    if season_number not in seasons:
        seasons[season_number] = []
    seasons[season_number].append(episode)

# Convert to JSON
json_data = json.dumps(seasons, indent=4)

# Optionally, write the JSON data to a file
with open('output.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)

print("JSON data has been written to output.json")
