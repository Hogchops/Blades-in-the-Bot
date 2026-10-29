# Blades in the Bot

A Discord bot for running **Blades in the Dark** (and other Forged in the Dark) games. It rolls dice with the Blades success rules, tracks progress clocks with images, manages faction info for the GM, and handles weekly session sign-ups with automatic reminders.

Built with [discord.py](https://discordpy.readthedocs.io/) and uses slash commands throughout.

## Features

- **Dice rolling:** Rolls d6 pools and reports Fail, Partial, Success, or Critical. Supports zero-dice rolls, position, and effect.
- **Progress clocks:** Create 4, 6, 8, or 12-segment clocks with a picture that updates as you tick them. Clocks are posted and pinned in the channel.
- **Faction tracker:** The GM can create factions with tier, affiliation, contact, and leader. Players can look them up. Factions are saved to disk as JSON.
- **Session sign-ups:** Post a weekly sign-up with one button per day. Days lock in once enough people join, and the bot can announce sessions and DM reminders the day before.
- **GM tools:** Hidden rolls, private GM notes, and a channel purge.
- **Engagement helper:** A quick reference for the engagement roll modifiers.

## Commands

### Rolling

| Command | Description |
|---|---|
| `/r <num>` | Roll `num` d6. Entering `0` rolls 2 dice and takes the lowest. |
| `/roll <num> [position] [effect]` | Roll with position (Desperate, Risky, Controlled) and effect (Limited, Standard, Great). Defaults to Risky / Standard. |
| `/gr <num>` | Roll dice that only you can see. *(Admin)* |
| `/how-to-roll` | Show how rolling works. |
| `/engagement` | Show the engagement roll modifiers. |

**Result rules:** The highest die decides the outcome. A 6 is a Success, 4 or 5 is a Partial, and 1 to 3 is a Fail. Two or more 6s is a Critical. When rolling zero dice, the lowest of two dice is used instead.

### Clocks

| Command | Description |
|---|---|
| `/clock <description> <total> [progress]` | Create a clock. Totals of 4, 6, 8, or 12 show a clock image. |
| `/tick <description> <amount>` | Advance a clock. A negative amount lowers it. |
| `/delete <description>` | Delete a clock and its message. |
| `/clear-clocks` | Forget all tracked clocks. |

### Factions

| Command | Description |
|---|---|
| `/faction <title>` | View a faction. |
| `/add-faction ...` | Create a faction. *(Admin)* Affiliation is `0` Empire, `1` Hutt, `2` Rebel. |
| `/modify-faction <title> <field> <value>` | Edit a faction field. *(Admin)* |
| `/remove-faction <title>` | Delete a faction. *(Admin)* |

### Session Sign-ups

| Command | Description |
|---|---|
| `/signup [session_max] [session_confirmed]` | Post the weekly sign-up with a button for each day. *(Admin)* |
| `/sr <user> <day>` | Remove someone from a day. *(Admin)* |
| `/sessions` | Announce every day that has enough sign-ups. *(Admin)* |
| `/notify` | Schedule DM reminders for confirmed sessions. *(Admin)* |

Sessions are set for **7:00 PM Eastern**. Reminders go out the day before.

### GM Notes and Utilities

| Command | Description |
|---|---|
| `/note <content>` | Save a private GM note. *(Admin)* |
| `/list-notes` | List your notes. *(Admin)* |
| `/delete-notes` | Delete all notes. *(Admin)* |
| `/clear-channel` | Delete all messages in the current channel. *(Admin)* |
| `/help` | List the commands you have access to. |

## Getting Started

### Prerequisites

- Python 3.10 or newer
- A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)
- The **Message Content** intent enabled for your bot

### Installation

```bash
git clone https://github.com/Hogchops/Blades-in-the-Bot.git
cd Blades-in-the-Bot
pip install discord.py python-dotenv pillow
```

### Configuration

Create a `.env` file in the project root:

```
DISCORD_TOKEN=your_bot_token_here
```

Create a `Factions/` folder in the project root. The faction commands save and load JSON files from it.

### Running

```bash
python blades_bot.py
```

Slash commands sync automatically when the bot starts. They can take a few minutes to appear in Discord.

### Bot Permissions

When inviting the bot, grant it at least: Send Messages, Embed Links, Attach Files, Manage Messages (to pin clocks and purge channels), and Read Message History.

## Project Structure

```
Blades-in-the-Bot/
├── blades_bot.py        # Entry point, loads the cogs
├── cogs/                # Command groups
│   ├── roll-cog.py
│   ├── clocks-cog.py
│   ├── faction-cog.py
│   ├── signup-cog.py
│   ├── admin-cog.py
│   └── help-cog.py
├── objects/             # Faction, clock, week, and reminder models
├── interactions/        # Discord button views for sign-ups
├── utils/               # Help formatting and image helpers
├── ClockImages/         # Clock pictures (4, 6, 8, and 12 segments)
└── Systems/             # Star system images
```

## Notes and Known Limitations

- **Setup is partly tied to one server.** The sign-up cog and `/help` contain a hardcoded server ID and owner ID. Update these in `cogs/signup-cog.py` and `cogs/help-cog.py` to use the bot on your own server.
- **Clocks and GM notes live in memory.** They are lost when the bot restarts. Factions, sign-up state, and reminders are saved to disk and restored.
- **Faction images** are loaded from a `FactionImages/` folder (`empire.jpg`, `hutt.jpg`, `rebellion.jpg`) that is not included in this repo. Add your own, or factions will fail to display an image.
- The faction affiliations (Empire, Hutt, Rebel) and the images in `Systems/` reflect a Star Wars themed campaign.
- `Outdated/` holds an older faction implementation and is not used.

## Acknowledgments

*Blades in the Dark* is a tabletop RPG by John Harper, published by One Seven Design. This is an unofficial fan project and is not affiliated with or endorsed by them.
