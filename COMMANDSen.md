# Full List of Commands

## Basic User Commands
- **`/start`**: Displays a welcome message with basic commands.
- **`/clip <quote>`**: Searches for a clip based on a quote. Example: `/clip genius`.
- **`/search <quote>`**: Finds clips matching the quote (returns the first 5 results). Example: `/search goat`.
- **`/list`**: Displays all clips found by `/search`.
- **`/select <clip_number>`**: Selects a clip from the list obtained by `/search` for further operations. Example: `/select 1`.
- **`/episodes <season>`**: Displays a list of episodes for the specified season. Example: `/episodes 2`.
- **`/cut <season_episode> <start_time> <end_time>`**: Cuts a fragment of the clip. Example: `/cut S02E10 20:30.11 21:32.50`.
- **`/adjust <before> <after>`**: Adjusts the selected clip by extending the start and end times. Example: `/adjust -5.5 1.2`.
- **`/compile all`**: Creates a compilation of all clips.
- **`/compile <range>`**: Creates a compilation from a range of clips. Example: `/compile 1-4`.
- **`/compile <clip_number1> <clip_number2> ...`**: Creates a compilation from selected clips. Example: `/compile 1 5 7`.
- **`/save <name>`**: Saves the selected clip with a given name. Example: `/save my_clip`.
- **`/myclips`**: Displays a list of saved clips.
- **`/send <name>`**: Sends a saved clip with the given name. Example: `/send my_clip`.
- **`/deleteclip <clip_name>`**: Deletes a saved clip with the given name. Example: `/deleteclip my_clip`.

## Administrative Commands
- **`/admin`**: Displays admin commands.
- **`/addwhitelist <id>`**: Adds a user to the whitelist. Example: `/addwhitelist 123456789`.
- **`/removewhitelist <id>`**: Removes a user from the whitelist. Example: `/removewhitelist 123456789`.
- **`/listwhitelist`**: Displays a list of all users in the whitelist.
- **`/listadmins`**: Displays a list of all admins.
- **`/listmoderators`**: Displays a list of all moderators.
- **`/note <user_id> <note>`**: Adds or updates a note for a user. Example: `/note 123456789 This is a note`.
- **`/key <key_content>`**: Saves a new key for the user. Example: `/key some_secret_key`.
- **`/listkey`**: Displays a list of all user keys.
- **`/report <issue_description>`**: Reports an issue to the admins.