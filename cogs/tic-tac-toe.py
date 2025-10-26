import discord
from discord.ext import commands
import random

# Emoji board positions
EMPTY = "⬜"
PLAYER = "❌"
BOT = "⭕"

class TicTacToeButton(discord.ui.Button):
    def __init__(self, x, y, game):
        super().__init__(style=discord.ButtonStyle.secondary, label=EMPTY, row=y)
        self.x = x
        self.y = y
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        if self.game.board[self.y][self.x] != EMPTY:
            await interaction.response.send_message("Spot already taken!", ephemeral=True)
            return

        # Player move
        self.game.board[self.y][self.x] = PLAYER
        self.label = PLAYER
        self.disabled = True

        # Check if player won
        if self.game.check_winner(PLAYER):
            for child in self.view.children:
                child.disabled = True
            await interaction.response.edit_message(content="You win! 🎉", view=self.view)
            return

        # Check tie
        if self.game.is_full():
            for child in self.view.children:
                child.disabled = True
            await interaction.response.edit_message(content="It's a tie!", view=self.view)
            return

        # Bot move
        self.game.bot_move()
        # Update button labels
        for btn in self.view.children:
            btn.label = self.game.board[btn.y][btn.x]
            if self.game.board[btn.y][btn.x] != EMPTY:
                btn.disabled = True

        # Check if bot won
        if self.game.check_winner(BOT):
            for child in self.view.children:
                child.disabled = True
            await interaction.response.edit_message(content="Bot wins! 🤖", view=self.view)
            return

        await interaction.response.edit_message(view=self.view)

class TicTacToe:
    def __init__(self):
        self.board = [[EMPTY]*3 for _ in range(3)]

    def is_full(self):
        return all(cell != EMPTY for row in self.board for cell in row)

    def check_winner(self, symbol):
        # Rows
        for row in self.board:
            if all(cell == symbol for cell in row):
                return True
        # Columns
        for col in range(3):
            if all(self.board[row][col] == symbol for row in range(3)):
                return True
        # Diagonals
        if all(self.board[i][i] == symbol for i in range(3)):
            return True
        if all(self.board[i][2-i] == symbol for i in range(3)):
            return True
        return False

    def bot_move(self):
        empty_positions = [(y, x) for y in range(3) for x in range(3) if self.board[y][x] == EMPTY]
        if empty_positions:
            y, x = random.choice(empty_positions)
            self.board[y][x] = BOT

class TicTacToeView(discord.ui.View):
    def __init__(self, game):
        super().__init__()
        self.game = game
        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y, game))

class TicTacToeGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tictactoe(self, ctx):
        """Start a single-player Tic-Tac-Toe game."""
        game = TicTacToe()
        view = TicTacToeView(game)
        await ctx.send("Tic-Tac-Toe: You are ❌, Bot is ⭕", view=view)

async def setup(bot):
    await bot.add_cog(TicTacToeGame(bot))
