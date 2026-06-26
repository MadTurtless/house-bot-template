# Baratheon Backup
Welcome to the Baratheon Backup repo! This hosts the code used by the Discord bot in House Arryn.
## Features
**Reaction Roles:** Automated regional role assignment using message reactions.

**Event Logging:** Logs events sent in specific channels. Using the specified format, the event data is parsed, validated, and added to a SQLite database.
Note: invalid logs are deleted after 10s to prevent chat clutter. Valid logs get a checkmark.

If an event log is edited, the new log is checked against the old one and updated where necessary.

**Entry Message:** When a user joins the guild, the bot will send a welcome message.

**Levelling System:** Guild members can gain xp by chatting in a specified channel.
They earn 5 xp per message, with a cooldown of 1s and a **Shannon Entropy check** to prevent spam.
By default, server boosters will enjoy **double xp**.

**Jokes & Quotes:** Using two APIs, the bot can fetch a joke or a GoT quote.

**Invite Tracking:** Track how many invites each member has. This can be used to reward recruitment.

**Profile Cards:** Displays user profiles and leaderboards as dynamically generated images using the `Pillow` library.
## Commands
### Leveling & Profile
* `/profile` - Check your current level, total XP, and progress chart.
* `/uprofile [@user]` - Check another member's profile card.
* `/leaderboard` - Display the top 10 members with the highest XP.

### Invites & Recruitment
* `/invites` - Check your total successful invitations.
* `/uinvites [@user]` - Check another member's invite count.
* `/invleaderboard` - Display the top 10 recruiters on the server.

### Fun & Utilities
* `/joke` - Fetch a random joke.
* `/quote` - Fetch a random *Game of Thrones* quote.
* `/events` - Check how many and which events you have attended.
* `/status` - Display the current running version (Dev vs. Production) and database connection integrity.

## Event Log Format
Logs must follow this structure for the parser to validate them properly:
```text
Event Type: [Name]
Host: [@Mention]
Attendees: [@Mention1, @Mention2]
Proof: [Image/Link]
```
## Setup
1. Clone the repo.
2. Environment Variables: Create a .env file with:
    * `DISCORD_TOKEN`
    * `LOGS_CHANNEL_ID`
    * `JOIN_CHANNEL_ID`
    * `XP_EARNABLE_CHANNEL_ID`
    * `BOOSTER_ROLE_ID`
    * `LEVEL_UP_MSG_CHANNEL_ID`
3. Create the `data/db.sqlite` file. (The database schema is automatically created during initial setup.)
4. Setup a virtual environment (venv):
   ```bash
   python -m venv .venv
   ```
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Run the bot:
   ```bash
   python main.py
   ```

Recommendation: When deploying the bot on a Linux VPS, wrap it in a SystemD service.
## Questions/Concerns?
DM MadTurtless on Discord.

### Ours is the Fury
