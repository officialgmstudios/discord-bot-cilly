# polls_cog.py
import discord
from discord.ext import commands, tasks
import sqlite3
import json
import asyncio
import time
import re
from typing import List

# CONFIG
DB_PATH = "polls.db"
PREFIX = "!"  # adjust to your bot prefix
# Supported numeric emojis up to 10 options:
NUMBER_EMOJIS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

# --- Database helpers ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS polls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER,
        channel_id INTEGER,
        message_id INTEGER,
        author_id INTEGER,
        question TEXT,
        options TEXT,
        emojis TEXT,
        is_anonymous INTEGER,
        end_time INTEGER,
        closed INTEGER DEFAULT 0
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        poll_id INTEGER,
        user_id INTEGER,
        emoji TEXT,
        PRIMARY KEY (poll_id, user_id)
    )
    """)
    conn.commit()
    conn.close()

def db_conn():
    return sqlite3.connect(DB_PATH)

# --- Poll parsing helper ---
def parse_poll_command(content: str):
    """
    Parses: !poll "Question" "Option1" "Option2" ... [-t seconds] [-anon]
    Returns dict with question, options, time (seconds or None), is_anonymous(bool)
    """
    # extract quoted strings
    quoted = re.findall(r'"([^"]+)"', content)
    if len(quoted) < 2:
        raise ValueError("Use quotes. Example: !poll \"Question\" \"Opt1\" \"Opt2\"")
    question = quoted[0].strip()
    options = [q.strip() for q in quoted[1:]]
    if not (2 <= len(options) <= 10):
        raise ValueError("Poll must have between 2 and 10 options.")
    # flags
    time_match = re.search(r'-t\s+(\d+)', content)
    duration = int(time_match.group(1)) if time_match else None
    anon = bool(re.search(r'-anon\b', content))
    return {"question": question, "options": options, "duration": duration, "anon": anon}

# --- Cog ---
class PollsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        init_db()
        self._closing_task = self.poll_closer.start()

    def cog_unload(self):
        self.poll_closer.cancel()

    # Helper to create poll row
    def _create_poll_row(self, guild_id, channel_id, message_id, author_id, question, options, emojis, is_anonymous, end_time):
        conn = db_conn()
        c = conn.cursor()
        c.execute("INSERT INTO polls (guild_id, channel_id, message_id, author_id, question, options, emojis, is_anonymous, end_time, closed) VALUES (?,?,?,?,?,?,?,?,?,0)",
                  (guild_id, channel_id, message_id, author_id, question, json.dumps(options), json.dumps(emojis), 1 if is_anonymous else 0, end_time))
        poll_id = c.lastrowid
        conn.commit()
        conn.close()
        return poll_id

    # Create command
    @commands.command(name="poll")
    async def create_poll(self, ctx, *, arg):
        """Create a poll. Usage: !poll "Question" "Opt1" "Opt2" ... [-t seconds] [-anon]"""
        try:
            parsed = parse_poll_command(arg)
        except Exception as e:
            await ctx.send(f"Error: {e}")
            return

        question = parsed["question"]
        options = parsed["options"]
        duration = parsed["duration"]
        is_anon = parsed["anon"]
        num_opts = len(options)
        emojis = NUMBER_EMOJIS[:num_opts]

        # Build embed
        embed = discord.Embed(title="📊 " + question, color=discord.Color.blurple())
        desc_lines = []
        for i, opt in enumerate(options):
            desc_lines.append(f"{emojis[i]}  {opt}")
        embed.description = "\n".join(desc_lines)
        footer_parts = []
        if is_anon:
            footer_parts.append("Anonymous poll")
        if duration:
            footer_parts.append(f"Ends in {duration} seconds")
        embed.set_footer(text=" • ".join(footer_parts) if footer_parts else "Poll")
        message = await ctx.send(embed=embed)

        # Add reactions
        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except Exception:
                # skip if emoji invalid
                pass

        end_time = int(time.time()) + duration if duration else None
        poll_id = self._create_poll_row(ctx.guild.id if ctx.guild else None, ctx.channel.id, message.id, ctx.author.id, question, options, emojis, is_anon, end_time)

        await ctx.send(f"Poll created with ID `{poll_id}`.")

    # Close poll
    @commands.command(name="closepoll")
    async def close_poll(self, ctx, poll_id: int):
        conn = db_conn()
        c = conn.cursor()
        c.execute("SELECT author_id, channel_id, message_id, closed FROM polls WHERE id=?", (poll_id,))
        row = c.fetchone()
        if not row:
            await ctx.send("Poll not found.")
            conn.close()
            return
        author_id, channel_id, message_id, closed = row
        if closed:
            await ctx.send("Poll is already closed.")
            conn.close()
            return
        # Permission: only author or manage_messages can close
        if ctx.author.id != author_id and not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You don't have permission to close this poll.")
            conn.close()
            return
        # mark closed
        c.execute("UPDATE polls SET closed=1 WHERE id=?", (poll_id,))
        conn.commit()
        conn.close()
        # fetch message and update embed
        channel = self.bot.get_channel(channel_id)
        if channel:
            try:
                msg = await channel.fetch_message(message_id)
                # edit embed to show closed
                embed = msg.embeds[0] if msg.embeds else discord.Embed(title="Poll", description="(no longer available)")
                embed.colour = discord.Color.dark_gray()
                embed.set_footer(text="Poll closed")
                await msg.edit(embed=embed)
            except Exception:
                pass
        await ctx.send(f"Poll `{poll_id}` closed.")
        # Announce results
        await self.show_results_internal(ctx, poll_id)

    # Internal results function
    async def show_results_internal(self, ctx, poll_id: int):
        conn = db_conn()
        c = conn.cursor()
        c.execute("SELECT question, options, emojis, is_anonymous FROM polls WHERE id=?", (poll_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return
        question, options_text, emojis_text, is_anon = row
        options = json.loads(options_text)
        emojis = json.loads(emojis_text)
        # tally votes
        c.execute("SELECT emoji, COUNT(*) FROM votes WHERE poll_id=? GROUP BY emoji", (poll_id,))
        counts = {row2[0]: row2[1] for row2 in c.fetchall()}
        conn.close()
        # build result embed
        embed = discord.Embed(title=f"Results — {question}", color=discord.Color.green())
        total = sum(counts.values())
        lines = []
        for i, opt in enumerate(options):
            emo = emojis[i]
            cnt = counts.get(emo, 0)
            pct = f"{(cnt / total * 100):.1f}%" if total > 0 else "0.0%"
            lines.append(f"{emo} **{opt}** — {cnt} votes ({pct})")
        embed.description = "\n".join(lines)
        if is_anon:
            embed.set_footer(text="Anonymous poll")
        await ctx.send(embed=embed)

    @commands.command(name="pollresults")
    async def poll_results(self, ctx, poll_id: int):
        """Show results for a poll (does not close)."""
        await self.show_results_internal(ctx, poll_id)

    @commands.command(name="activepolls")
    async def active_polls(self, ctx):
        conn = db_conn()
        c = conn.cursor()
        c.execute("SELECT id, question, end_time FROM polls WHERE closed=0 AND guild_id=?", (ctx.guild.id,))
        rows = c.fetchall()
        conn.close()
        if not rows:
            await ctx.send("No active polls.")
            return
        lines = []
        now = int(time.time())
        for r in rows:
            pid, q, end = r
            remaining = f"{end - now} seconds" if end else "No auto-close"
            lines.append(f"`{pid}` — {q} — {remaining}")
        await ctx.send("\n".join(lines))

    # Reaction handlers to sync votes
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return
        conn = db_conn()
        c = conn.cursor()
        c.execute("SELECT id, closed, emojis FROM polls WHERE message_id=? AND channel_id=? AND guild_id=?", (payload.message_id, payload.channel_id, payload.guild_id))
        row = c.fetchone()
        if not row:
            conn.close()
            return
        poll_id, closed, emojis_text = row
        if closed:
            conn.close()
            return
        emojis = json.loads(emojis_text)
        emoji_str = str(payload.emoji)
        # Only handle if emoji belongs to this poll
        if emoji_str not in emojis:
            conn.close()
            return
        # enforce single vote: remove previous vote entry for this user if exists
        c.execute("SELECT emoji FROM votes WHERE poll_id=? AND user_id=?", (poll_id, payload.user_id))
        prev = c.fetchone()
        if prev:
            prev_emoji = prev[0]
            if prev_emoji == emoji_str:
                conn.close()
                return  # same vote
            # remove previous reaction from message (best effort)
            try:
                channel = self.bot.get_channel(payload.channel_id)
                if channel:
                    message = await channel.fetch_message(payload.message_id)
                    # find the Member object
                    guild = self.bot.get_guild(payload.guild_id)
                    member = guild.get_member(payload.user_id)
                    if member:
                        await message.remove_reaction(prev_emoji, member)
            except Exception:
                pass
        # upsert vote
        c.execute("REPLACE INTO votes (poll_id, user_id, emoji) VALUES (?,?,?)", (poll_id, payload.user_id, emoji_str))
        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # If user removed reaction, remove their vote (so they effectively unvote)
        conn = db_conn()
        c = conn.cursor()
        c.execute("SELECT id, closed, emojis FROM polls WHERE message_id=? AND channel_id=? AND guild_id=?", (payload.message_id, payload.channel_id, payload.guild_id))
        row = c.fetchone()
        if not row:
            conn.close()
            return
        poll_id, closed, emojis_text = row
        if closed:
            conn.close()
            return
        emoji_str = str(payload.emoji)
        # delete vote record if any
        c.execute("DELETE FROM votes WHERE poll_id=? AND user_id=? AND emoji=?", (poll_id, payload.user_id, emoji_str))
        conn.commit()
        conn.close()

    # Background task to close polls when end_time reached
    @tasks.loop(seconds=20)
    async def poll_closer(self):
        now = int(time.time())
        conn = db_conn()
        c = conn.cursor()
        c.execute("SELECT id FROM polls WHERE closed=0 AND end_time IS NOT NULL AND end_time<=?", (now,))
        rows = c.fetchall()
        conn.close()
        for r in rows:
            pid = r[0]
            # Close via same logic as close_poll, but without ctx
            conn = db_conn()
            c = conn.cursor()
            c.execute("UPDATE polls SET closed=1 WHERE id=?", (pid,))
            c.execute("SELECT channel_id, message_id FROM polls WHERE id=?", (pid,))
            row2 = c.fetchone()
            conn.commit()
            conn.close()
            if row2:
                channel_id, message_id = row2
                channel = self.bot.get_channel(channel_id)
                if channel:
                    try:
                        msg = await channel.fetch_message(message_id)
                        embed = msg.embeds[0] if msg.embeds else discord.Embed(title="Poll", description="(no longer available)")
                        embed.colour = discord.Color.dark_gray()
                        embed.set_footer(text="Poll closed (auto)")
                        await msg.edit(embed=embed)
                    except Exception:
                        pass
                # try to announce results in the channel
                try:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        ctx_msg = await channel.send(f"Poll `{pid}` auto-closed. Results:")
                        # use internal show results with a fake Context using a minimal helper - instead, just call internal function if we had ctx; simpler: call show_results_internal with a dummy ctx-like wrapper:
                        class FakeCtx:
                            def __init__(self, channel):
                                self.channel = channel
                            async def send(self, *a, **k):
                                return await channel.send(*a, **k)
                        fake_ctx = FakeCtx(channel)
                        await self.show_results_internal(fake_ctx, pid)
                except Exception:
                    pass

    @poll_closer.before_loop
    async def before_closer(self):
        await self.bot.wait_until_ready()

# Setup for adding cog
def setup(bot):
    bot.add_cog(PollsCog(bot))
