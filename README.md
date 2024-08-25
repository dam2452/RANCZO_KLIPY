# RanczoKlipy Bot

RanczoKlipy Bot is a highly customizable Telegram bot designed to manage and process video clips from the popular TV series "Ranczo." The bot allows users to search for specific quotes, manage their own video clips, and perform various administrative tasks related to user management and content moderation.

## Features

### 1. Video Clip Management
- **Search for Quotes:** Users can search for specific quotes within the series using commands like `/klip <quote>` and `/szukaj <quote>`. The bot will return matching video segments.
- **Clip Compilation:** Users can compile multiple clips into a single video file with commands like `/kompiluj <clip_numbers>` or `/kompiluj wszystko`.
- **Clip Adjustment:** The bot allows for fine-tuning of clips by adjusting start and end times using `/dostosuj <clip_number> <adjust_before> <adjust_after>`.
- **Saved Clips Management:** Users can save, list, and delete their clips with commands like `/zapisz`, `/mojeklipy`, and `/usunklip`.

### 2. User and Role Management
- **Admin and Moderator Roles:** Admins and moderators have access to specific functionalities. Commands like `/listadmins` and `/listmoderators` help view these roles.
- **Whitelist Management:** Users can be added to or removed from the whitelist, allowing them access to certain features. Use `/addwhitelist <user_id>` or `/removewhitelist <user_id>` for this.
- **Notes on Users:** Admins can add notes to user profiles using the `/note <user_id> <note>` command.
### 3. Content Moderation
- **Report Issues:** Users can report issues directly to admins using the `/report <issue_description>` command.
- **Cooldown and Limits:** To prevent spamming, cooldown periods and limits are enforced for non-admin users, ensuring a balanced usage experience.

### 4. Elasticsearch Integration
- The bot is integrated with Elasticsearch to efficiently manage and search through transcripts of the series. This integration allows fast and accurate retrieval of video segments based on text queries.

### 5. Database Management
- The bot uses PostgreSQL for storing user data, video clips, search history, and logs. Database operations like initializing the schema and managing user data are handled through a set of robust asynchronous functions.

## Key Commands

### Basic User Commands
- **`/start`**: Displays a welcome message with basic commands.
- **`/clip <quote>`**: Searches for a specific quote and returns the matching video clip.
- **`/myclips`**: Lists all the clips saved by the user.
- **`/compile <clip_numbers>`**: Compiles selected clips into one video.

### Administrative Commands
- **`/listadmins`**: Lists all admins.
- **`/listmoderators`**: Lists all moderators.
- **`/addwhitelist <user_id>`**: Adds a user to the whitelist.
- **`/removewhitelist <user_id>`**: Removes a user from the whitelist.
- **`/note <user_id> <note>`**: Adds or updates a note for a user.
- **`/report <issue_description>`**: Reports an issue to the admins.

For a full list of commands, refer to the [Commands Documentation](./COMMANDS.md).

## Prerequisites
- **Python 3.12**
- **PostgreSQL Database**
- **Elasticsearch**
- **FFmpeg**

### Required Python Libraries
- **ffmpeg**
- **elasticsearch**
- **urllib3**
- **python-dotenv**
- **requests**
- **tabulate**
- **Retry**
- **psycopg2-binary**
- **aiogram**
- **asyncpg**
- **pydantic-settings**
- **pydantic**


## Contributing

Contributions are always welcome! If you'd like to help improve the project, feel free to collaborate by submitting pull requests or suggesting changes.

## License

This project is licensed under the MIT License. You are free to use and modify the software for personal or internal purposes. However, distribution or public sharing of modified versions should be done through contributions to this project. If you wish to use this software in a significant or commercial capacity, please contact the project maintainers for further discussion.

