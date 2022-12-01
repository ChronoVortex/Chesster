import discord
from discord.ext import commands
from io import BytesIO, StringIO
from wand.image import Image
from wand.color import Color
import chess.svg as chess_svg
import chess as Chess
from settings import *

def eqor(val, *args):
    for arg in args:
        if val == arg:
            return True
    return False

'''
checking on the first move screws up the undo command, the condition:
bool(self.movesMade) == (self.active_player() == ctx.author)
is not sufficient
'''
class chess(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chessBoard = None
        self.movesMade = 0
        self.movesMax = 1
        self.player1 = None
        self.player2 = None
    
    def chess_clear(self):
        self.chessBoard = None
        self.movesMade = 0
        self.movesMax = 1
        self.player1 = None
        self.player2 = None
        print('Chess cleared')
    
    def is_chess_player(self, player: discord.Member):
        return self.chessBoard and eqor(player, self.player1, self.player2)
    
    def active_player(self):
        return self.player1 if self.chessBoard.turn else self.player2
    
    @commands.command(help='View the board')
    async def view(self, ctx):
        if self.chessBoard:
            # Generate and format board image
            with Color('#00000000') as bgcolor, Image(\
                blob=chess_svg.board(board=self.chessBoard, style='text{fill:white}').encode(),\
                format='svg', width=400, height=400, background=bgcolor) as img:
                    render = BytesIO(img.make_blob(format='png'))
            render.seek(0)
            
            # Send board image to discord
            await ctx.send(file=discord.File(fp=render, filename='chessboard.png'))
    
    @commands.command(help='Request a chess match')
    async def chess(self, ctx, member: discord.Member, variant = 'normal'):
        if self.player1:
            await ctx.send('Chess is already in progress. Patience, young grasshopper.')
        elif member and member != ctx.author:
            self.movesMax = 2 if variant == 'double' else 1
            self.player1 = ctx.author
            self.player2 = member
            await ctx.send('{1} challenges {2} to a game of chess! Use "{0}accept" to play or "{0}refuse" to run like a *coward*.'.format(
                PREFIX, self.player1.display_name, self.player2.display_name))
    
    @commands.command(help='Refuse a chess match')
    async def refuse(self, ctx):
        if not self.chessBoard and self.player1 and eqor(ctx.author, self.player1, self.player2):
            await ctx.send('Chess cancled.')
            self.chess_clear()
    
    @commands.command(help='Accept a chess match')
    async def accept(self, ctx):
        # Board is uninitialized, player 2 is exists and command was called by player 2
        if not self.chessBoard and self.player2 and ctx.author == self.player2:
            # Tell players the game has started
            print('Initializing chess...')
            await ctx.send('Beginning chess with {1} as white and {2} as black. Maximum moves per turn is {3}. Use "{0}move" to move a piece on your turn. Use "{0}view" to view the board or "{0}forfeit" to give up at any time. Use "{0}undo" to take back a move you just made.'.format(PREFIX, self.player1.display_name, self.player2.display_name, self.movesMax))
            
            # Initialize the chess board
            self.chessBoard = Chess.Board()
            
            # Show board
            await self.view(ctx)
            print('Chess is running')
    
    @commands.command(help='Forfeit the game')
    async def forfeit(self, ctx):
        if self.is_chess_player(ctx.author):
            await ctx.send('Game over! {} forfeits!'.format(ctx.author.display_name))
            self.chess_clear()
    
    @commands.command(help='Undo your last move')
    async def undo(self, ctx):
        if self.is_chess_player(ctx.author):
            # Make sure the caller was the last person to move
            if bool(self.movesMade) == (self.active_player() == ctx.author):
                # Try to undo the move
                print('Attempting to undo move...')
                try:
                    self.chessBoard.pop()
                except IndexError as e:
                    print('Undo failed: {}'.format(str(e)))
                    await ctx.send('No moves to undo.')
                    return
                print('Undo successful')
                
                # Show board
                await self.view(ctx)
                
                # Fix move count (turn switching is handled by pop)
                if self.movesMade > 0:
                    self.movesMade -= 1
                else:
                    self.movesMade = self.movesMax - 1
            else:
                await ctx.send('That wasn\'t your move. Nice try.')
    
    @commands.command(help='Make a move')
    async def move(self, ctx, move: str):
        # Check if game is in progress and caller is one of the players
        if self.is_chess_player(ctx.author):
            if self.active_player() == ctx.author:
                # Get turn
                turn = self.chessBoard.turn
                color = 'White' if turn else 'Black'
                
                # Try the move
                if eqor(move, 'skip', 'pass', 'forfeit'): # Give current player the option to pass
                    print(color + ' passes')
                    self.chessBoard.push(Chess.Move.null())
                    await ctx.send('Move skipped.')
                else: # The actual moves
                    print('{} attempting move {}...'.format(color, move))
                    try:
                        self.chessBoard.push_san(move)
                    except ValueError as e:
                        print('Move failed: {}'.format(str(e)))
                        await ctx.send('That move is illegal.')
                        return
                    print('Move successful')
                    
                    # Show board
                    await self.view(ctx)
                
                # Keep the color the same for movesMax turns if no check
                self.movesMade += 1
                if self.movesMade < self.movesMax and not self.chessBoard.is_check():
                    self.chessBoard.turn = turn
                else:
                    # Turn is over, check if game is over
                    if self.chessBoard.is_checkmate():
                        await ctx.send('Game over! {} wins!'.format((self.player1 if (self.chessBoard.result() == '1-0') else self.player2).display_name))
                        self.chess_clear()
                        return
                    
                    # Reset moves on turn switch
                    self.movesMade = 0
            else:
                await ctx.send("It is currently {}'s turn.".format(self.active_player().display_name))
    
    @commands.command(help='Skip your move')
    async def zugzwang(self, ctx):
        await self.move(ctx, 'skip')

def setup(bot):
    bot.add_cog(chess(bot))
