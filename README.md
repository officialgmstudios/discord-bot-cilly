Team: AlgoWorks
Author: Sumit (Team Head)
Project Goal: a multipurpose Discord bot using Python and discord.py
Focus areas:
-Server management (moderation & utilities)
-Fun commands (!meme , !joke etc.)
-*XP System (members who are more active without spamming will get higher XP and
Rank Cards)
Phase 1 (MVP):
1. Prefix based commands like !meme (shows a random meme), !joke (sends a random
joke)
2. Moderation : Kick, ban, Mute (strike based system)
3. Welcome and Goodbye messages
Phase 2 :
1. XP system:
-members gain xp for chatting (not spamming or violating community guidelines)
-Top members get rank cards
2. Expand Moderation system
3. Polling system:
Ex: !poll “who’s got a wider chest” “Brock Lesner” “Mod…….
4. Daily news and quotes
Phase Optional: (just some ideas, might add)
-mini games: Tick Tac Toe etc.
Tech overview:
Prefix commands -> discord.py
Memes and jokes -> requests
Moderation system -> discord.py and splite3
Welcome and goodbye messages -> discord.py
XP System -> splite3 and pillow
Polls -> discord.py embeds
Learning:
-Core Python
-API Interactions (!meme , !joke commands )
-Database (storing members xp and strike count etc.)
-Automation

## News and Quotes Commands

- `!news` — Fetches a random top news headline from a public news API and posts it as an embed.
- `!quote` — Fetches a random inspirational quote from a public quotes API and posts it as an embed.

These commands are available to all users. Example usage:

```
!news
!quote
```

The bot will reply with the latest news or a motivational quote.
