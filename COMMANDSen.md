
---

# 📝 Full Command List

## 🚀 Command Shortcuts

- **`/start`**: 👋 Launches the main menu.
- **`/clip <quote>`**/ **`/k <quote>`**: 🎥 Clip search.
- **`/search <quote>`**/ **`/sz <quote>`**: 🔍 Find clips.
- **`/list`**/ **`/l`**: 📋 List of clips.
- **`/select <clip_number>`**/ **`/w <clip_number>`**: 🎯 Clip selection.
- **`/episodes <season>`**/ **`/o <season>`**: 🎞️ List of episodes.
- **`/cut <season_episode> <start_time> <end_time>`**: ✂️ Cutting a clip.
- **`/adjust <extend_before> <extend_after>`**/ **`/d <extend_before> <extend_after>`**: ⏳ Adjusting a clip.
- **`/compile all`**/ **`/kom all`**: 🎬 Compiling all clips.
- **`/compile <range>`**/ **`/kom <range>`**: 🎬 Compiling a range of clips.
- **`/compile <clip_number1> <clip_number2> ...`**/ **`/kom <clip_number1> <clip_number2> ...`**: 🎬 Compiling selected clips.
- **`/save <name>`**/ **`/z <name>`**: 💾 Saving a clip.
- **`/myclips`**/ **`/mk`**: 📂 Your clips.
- **`/send <name>`**/ **`/wys <name>`**: 📤 Sending a clip.
- **`/deleteclip <clip_name>`**/ **`/uk <clip_name>`**: 🗑️ Deleting a clip.
- **`/admin`**: 🔧 Administrative commands.
- **`/addwhitelist <id>`**/ **`/addw <id>`**: 📝 Adding to the whitelist.
- **`/removewhitelist <id>`**/ **`/rmw <id>`**: 🚫 Removing from the whitelist.
- **`/listwhitelist`**/ **`/lw`**: 📄 Whitelist of users.
- **`/listadmins`**/ **`/la`**: 🛡️ List of administrators.
- **`/listmoderators`**/ **`/lm`**: 🛡️ List of moderators.
- **`/note <user_id> <note>`**: 🗒️ Adding a note to a user.
- **`/key <key_content>`**/ **`/klucz <key_content>`**: 🔑 Using a subscription key.
- **`/listkeys`**/ **`/lk`**: 🔑 List of subscription keys.
- **`/addkey <days> <note>`**/ **`/addk <days> <note>`**: 🔑 Creating a new subscription key.
- **`/removekey <key>`**/ **`/rmk <key>`**: 🚫 Removing a subscription key.
- **`/report <issue_description>`**/ **`/r <issue_description>`**: ⚠️ Reporting an issue.

## 👥 Basic User Commands

- **`/start`**/ **`/s`**: 👋 Displays a welcome message with basic commands.
- **`/clip <quote>`**/ **`/k <quote>`**: 🎥 Searches for a clip based on a quote. Example: `/clip genius`.
- **`/search <quote>`**/ **`/sz <quote>`**: 🔍 Finds clips matching the quote (first 5 results). Example: `/search goat`.
- **`/list`**/ **`/l`**: 📋 Displays all clips found with `/search`.
- **`/select <clip_number>`**/ **`/w <clip_number>`**: 🎯 Selects a clip from the list generated by `/search`**for further operations. Example: `/select 1`.
- **`/episodes <season>`**/ **`/o <season>`**: 🎞️ Displays a list of episodes for the given season. Example: `/episodes 2`.
- **`/cut <season_episode> <start_time> <end_time>`**: ✂️ Cuts a segment from a clip. Example: `/cut S02E10 20:30.11 21:32.50`.
- **`/adjust <extend_before> <extend_after>`**/ **`/d <extend_before> <extend_after>`**: ⏳ Adjusts the selected clip by extending the start and end time. Example: `/adjust -5.5 1.2`.
- **`/compile all`**/ **`/kom all`**: 🎬 Compiles all clips.
- **`/compile <range>`**/ **`/kom <range>`**: 🎬 Compiles clips within a range. Example: `/compile 1-4`.
- **`/compile <clip_number1> <clip_number2> ...`**/ **`/kom <clip_number1> <clip_number2> ...`**: 🎬 Compiles selected clips. Example: `/compile 1 5 7`.
- **`/save <name>`**/ **`/z <name>`**: 💾 Saves the selected clip with a specified name. Example: `/save my_clip`.
- **`/myclips`**/ **`/mk`**: 📂 Displays a list of saved clips.
- **`/send <name>`**/ **`/wys <name>`**: 📤 Sends the saved clip with the specified name. Example: `/send my_clip`.
- **`/deleteclip <clip_name>`**/ **`/uk <clip_name>`**: 🗑️ Deletes the saved clip with the specified name. Example: `/uk my_clip`.

## 🔧 Administrative Commands

- **`/admin`**: 🔧 Displays administrative commands.
- **`/addwhitelist <id>`**/ **`/addw <id>`**: 📝 Adds a user to the whitelist. Example: `/addwhitelist 123456789`.
- **`/removewhitelist <id>`**/ **`/rmw <id>`**: 🚫 Removes a user from the whitelist. Example: `/removewhitelist 123456789`.
- **`/listwhitelist`**/ **`/lw`**: 📄 Displays a list of all users on the whitelist.
- **`/listadmins`**/ **`/la`**: 🛡️ Displays a list of all administrators.
- **`/listmoderators`**/ **`/lm`**: 🛡️ Displays a list of all moderators.
- **`/note <user_id> <note>`**: 🗒️ Adds or updates a note for a user. Example: `/note 123456789 This is a note`.
- **`/key <key_content>`**/ **`/klucz <key_content>`**: 🔑 Uses a new subscription key for a user. Example: `/key some_secret_key`.
- **`/listkeys`**/ **`/lk`**: 🔑 Displays a list of all subscription keys.
- **`/addkey <days> <note>`**/ **`/addk <days> <note>`**: 🔑 Creates a new subscription key for a specified number of days. Example: `/addkey 30 "secret_key"`.
- **`/removekey <key>`**/ **`/rmk <key>`**: 🚫 Removes an existing subscription key. Example: `/removekey some_secret_key`.
- **`/report <issue_description>`**/ **`/r <issue_description>`**: ⚠️ Reports an issue to the administrators.

---
