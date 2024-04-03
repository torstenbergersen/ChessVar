class ChessVar:
    '''
    Handles the playing of the game. Contains methods for getting turn, 
    switching turns, making moves, entering a fairy piece, and getting the game 
    state. Initiates the Board subclass when called.
    '''
    def __init__(self):
        '''
        Initialize the game state and turn(begin with white). Creates the board.
        '''
        self._game_state = "UNFINISHED"
        self._turn = 'white'
        self._board = Board(self)

    def get_turn(self):
        '''
        Returns whose turn it is.
        Returns:
            str: 'white' or 'black'
        '''  
        return self._turn     

    def make_move(self, start: str, end: str):
        '''
        Handles movement of pieces on the board. Calls on the board class to 
        update positions and check for wins, and the piece classes for move
        validation.
        Parameters:
            start (str): The starting square of the piece (e.g., 'e2').
            end (str): The ending square of the piece (e.g., 'e4').
        Returns:
            bool: True if the move is valid and made, False otherwise.
        '''  
        board = self._board.get_board()
        if start not in board or end not in board:
            return False
        piece_symbol = board[start]
        piece_color = 'white' if piece_symbol.isupper() else 'black'
        piece_class = self._board.get_piece_mapping().get(piece_symbol.upper())

        if self.get_game_state() in ['WHITE_WON', 'BLACK_WON']:
            return False
        if ((piece_color == 'white' and self._turn == 'black') 
                or (piece_color == 'black' and self._turn == 'white')):
            return False
        if piece_class:
            piece = piece_class(start, piece_color, self._board)
            if piece.is_valid_move(start, end) == True:
                if board[end] == 'K':
                    self._board.update_board(piece_symbol, start, end)
                    self._game_state = 'BLACK_WON'
                    print(self._game_state)
                    return True
                if board[end] == 'k':
                    self._board.update_board(piece_symbol, start, end)
                    self._game_state = 'WHITE_WON'
                    print(self._game_state)
                    return True
                if self._game_state == 'UNFINISHED':
                    self.switch_turn()
                    self._board.update_board(piece_symbol, start, end)
                    return True   
        return False

    def get_game_state(self):
        '''
        Returns the state of the game (UNFINISHED', 'WHITE_WON', 'BLACK_WON').
        Returns:
            str: The current state of the game.
        '''    
        return self._game_state

    def enter_fairy_piece(self, piece: str, square: str):
        '''
        Positions a fairy piece on the board. Checks to make sure position and
        timing are valid(they have lost the correct piece on a previous turn).
        Also checks whether they have a fairy piece to use.
        Parameters:
            piece (str): The type of fairy piece ('F', 'H', 'f', 'h').
            square (str): The square where the fairy piece is to be placed.
        Returns:
            bool: True if the fairy piece is successfully placed, False otherwise.
        '''
        board = self._board.get_board()
        pieces = self._board.get_piece_mapping()
        if square not in board:
            return False
        if piece not in pieces:
            return False

        piece_color = 'white' if piece.isupper() else 'black'
        lost_pieces = self._board.get_lost_major_pieces(piece_color)
        fairy_pieces_placed = self._board.get_fairy_piece_status(piece_color)
        if piece in fairy_pieces_placed:
            return False
                    
        if self._turn != piece_color:
            return False
        
        # Ensure the square is within the home ranks
        if not ((piece_color == 'white' and square[1] in ('1', '2')) or
                (piece_color == 'black' and square[1] in ('7', '8'))):
            return False

        # Check if the square is empty
        if board[square] != '.':
            return False
        
        if len(lost_pieces) < 1 or (len(fairy_pieces_placed) >= 1 and len(lost_pieces) < 2):
            return False

        self.switch_turn()
        self._board.update_board(piece, None, square)
        self._board.register_fairy_piece_placement(piece, piece_color)
        return True

    def switch_turn(self):
        '''
        Called whenever a move is made. Changes whose turn it is.  
        '''
        if self._turn == 'white':
            self._turn = 'black'
        else:
            self._turn = 'white'


class Board:
    '''
    Represents the chess board with dictionaries for piece tracking as well as
    methods for printing in the terminal. 
    '''
    def __init__(self, chess_var):
        '''
        Initializes the board with the starting position of pieces.
        Paramters:
            chess_var(class): chess_var class
        '''
        self._chess_var = chess_var 
        self._board = {
            'a8': 'r', 'b8': 'n', 'c8': 'b', 'd8': 'q', 'e8': 'k', 'f8': 'b', 'g8': 'n', 'h8': 'r',
            'a7': 'p', 'b7': 'p', 'c7': 'p', 'd7': 'p', 'e7': 'p', 'f7': 'p', 'g7': 'p', 'h7': 'p',
            'a6': '.', 'b6': '.', 'c6': '.', 'd6': '.', 'e6': '.', 'f6': '.', 'g6': '.', 'h6': '.',
            'a5': '.', 'b5': '.', 'c5': '.', 'd5': '.', 'e5': '.', 'f5': '.', 'g5': '.', 'h5': '.',
            'a4': '.', 'b4': '.', 'c4': '.', 'd4': '.', 'e4': '.', 'f4': '.', 'g4': '.', 'h4': '.',
            'a3': '.', 'b3': '.', 'c3': '.', 'd3': '.', 'e3': '.', 'f3': '.', 'g3': '.', 'h3': '.',
            'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P',
            'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K', 'f1': 'B', 'g1': 'N', 'h1': 'R'
        }
        self._lost_major_pieces = {'white': [], 'black': []}
        self._fairy_pieces_placed = {'white': [], 'black': []}
        self._piece_mapping = {
            'P': Pawn,
            'p': Pawn,
            'R': Rook,
            'r': Rook,
            'N': Knight,
            'n': Knight,
            'B': Bishop,
            'b': Bishop,
            'Q': Queen,
            'q': Queen,
            'K': King,
            'k': King,
            'F': Falcon,
            'f': Falcon,
            'H': Hunter,
            'h': Hunter,
        }
        self._pieces = {
            'K': '\u2654',  # White King
            'Q': '\u2655',  # White Queen
            'B': '\u2657',  # White Bishop
            'N': '\u2658',  # White Knight
            'R': '\u2656',  # White Rook
            'P': '\u2659',  # White Pawn
            'k': '\u265A',  # Black King
            'q': '\u265B',  # Black Queen
            'b': '\u265D',  # Black Bishop
            'n': '\u265E',  # Black Knight
            'r': '\u265C',  # Black Rook
            'p': '\u265F',  # Black Pawn
            '.': ' ',       # Empty Square
            'F': 'F',       # White Falcon
            'H': 'H',       # White Hunter
            'f': 'f',       # Black Falcon
            'h': 'h',       # Black Hunter
        }
        print('')
        print('Falcon-Hunter Chess, by Torsten')
        print('')
        print("Consult the rules for Falcon/Hunter placement. If you wish to place" \
              " either, type 'f' and 'h' for black, and 'F' and 'H' for white for" \
              " the 'origin' and the square that you wish to place them for the "
              "'destination'. Type 'e' to exit game.")
        print('')
        print('Let the game begin! ')
        print('')
        print('')
        self.print_board()

    def print_board(self):
        '''
        Prints the current state of the board to the terminal.
        '''
        top_border = "  ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗"
        middle_border = "  ╟───┼───┼───┼───┼───┼───┼───┼───╢"
        bottom_border = "  ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝"
        row_start = "║"
        row_end = "║"
        if self._chess_var.get_turn() == 'white':
            print("White's turn")
        else:
            print("Black's turn")
        print('') 
        print(top_border)
        for row_number in range(8, 0, -1):
            print(f'{row_number} {row_start}', end='')
            for col_letter in 'abcdefgh':
                square = col_letter + str(row_number)
                piece = self._board.get(square, '.')  #
                print(f' {self._pieces[piece]} │', end='')
            print(f'\b{row_end}')  
            if row_number > 1:
                print(middle_border)
            else:
                print(bottom_border)
        print('    a   b   c   d   e   f   g   h  ')
        print('') 

    def update_board(self, piece, start: str, end: str):
        '''
        Updates the board (dictionary) with a new move.
        Parameters:
            piece (str): The piece being moved.
            start (str): The starting square of the piece.
            end (str): The ending square of the piece.
        '''
        if self._board[end] != '.':
            captured_piece = self._board[end]
            player_color = 'white' if captured_piece.isupper() else 'black'
            if captured_piece in 'QRBNqrbn':  # It's a major piece
                self._lost_major_pieces[player_color].append(captured_piece)

        if start:
            self._board[start] = '.'  # Clear the starting square if it's not a new placement
        self._board[end] = piece  # Place or move the piece to the ending square
        self.print_board()

    def get_lost_major_pieces(self, color):
        '''
        Return a list of lost major pieces for the given color.
        '''
        return self._lost_major_pieces[color]

    def register_fairy_piece_placement(self, piece, color):
        '''
        Increment the count of fairy pieces placed for the given color.
        '''
        self._fairy_pieces_placed[color].append(piece)

    def get_fairy_piece_status(self, color):
        '''
        Return the number of fairy pieces placed for the given color.
        '''
        return self._fairy_pieces_placed[color]

    def get_board(self):
        '''
        Returns the board dictionary.
        '''
        return self._board

    def get_piece_mapping(self):
        '''
        Return piece mapping dictionary.
        '''
        return self._piece_mapping

    def get_opponent_pieces(self, color):
        '''
        Returns list of opponent pieces.
        Parameters:
            color(str): The color of your side.
        '''
        opponent_pieces = []
        if color == 'white':
            for pos, piece in self._board.items(): 
                if piece.islower():
                    opponent_pieces.append((pos, piece))
        else:
            for pos, piece in self._board.items(): 
                if piece.isupper():
                    opponent_pieces.append((pos, piece))
        return opponent_pieces

class Pawn:
    '''
    Represents a pawn piece and its movement rules.
    '''
    def __init__(self, pos, color, board):
        '''
        Initializes the pawn with its position and color.
        Parameters:
            pos(str): position
            color(str): color of piece ('black' or 'white')
            board(dictionary): board dictionary
        '''
        self._position = pos
        self._color = color
        self._board = board
    def get_valid_moves(self, pos): 
        '''
        Returns a list of valid moves based on the pawn's position.
        Parameters:
            pos (str): The position of the pawn on the board.
        Returns:
            list[str]: A list of valid moves (e.g., ['e3', 'e4']).
        '''
        valid_moves = []
        row, col = pos[1], pos[0]
        forward_row = str(int(row)+ 1) if self._color == 'white' else str(int(row)- 1)
        forward_pos = col + forward_row
        #forward
        if self._board.get_board().get(forward_pos, None) == '.':
            valid_moves.append(forward_pos)

            #double forward
            if (self._color == 'white' and row == '2') or (self._color == 'black' and row == '7'):
                double_forward_row = str(int(row)+ 2) if self._color == 'white' else str(int(row)- 2)
                double_forward_pos = col + double_forward_row
                if self._board.get_board().get(double_forward_pos, None) == '.':
                    valid_moves.append(double_forward_pos)

        #capture
        for capture_col in [chr(ord(col)-1), chr(ord(col)+ 1)]: #ascii to check adjacent columns
            capture_pos = capture_col + forward_row
            if any(pos == capture_pos for pos, _ in self._board.get_opponent_pieces(self._color)):
                valid_moves.append(capture_pos)
        
        return valid_moves

    def is_valid_move(self, start: str, end: str):
        '''
        Checks if the move from start to end is valid for this piece.
        Parameters:
            start (str): The starting square of the piece (e.g., 'e2').
            end (str): The ending square of the piece (e.g., 'e4').
        Returns:
            bool: True if the move is valid, False otherwise.
        '''
        if end in self.get_valid_moves(start):
            return True
        return False

class Rook:
    '''
    Represents a rook piece and its movement rules.
    '''
    def __init__(self, pos, color, board):
        '''
        Initializes the rook with its position and color.
        Parameters:
            pos(str): position
            color(str): color of piece ('black' or 'white')
            board(dictionary): board dictionary
        '''
        self._position = pos
        self._color = color
        self._board = board
    def get_valid_moves(self, pos): 
        '''
        Returns a list of valid moves based on the rook's position.
        Parameters:
            pos (str): The position of the rook on the board.
        Returns:
            list[str]: A list of valid moves (e.g., ['e3', 'e4']).
        '''
        valid_moves = []
        row, col = int(pos[1]), pos[0]  
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for direction in directions:
            for index in range(1, 8):  # Maximum number of squares in any direction
                newRow = row + direction[0] * index
                newCol = ord(col) + direction[1] * index
                if newRow in range(1, 9) and newCol in range(ord('a'), ord('h') + 1):
                    newPos = chr(newCol) + str(newRow)
                    if self._board.get_board().get(newPos, None) == '.':
                        valid_moves.append(newPos)
                    else:
                        if any(newPos == pos for pos, _ in self._board.get_opponent_pieces(self._color)):
                            valid_moves.append(newPos)
                        break  # Stop checking further in this direction
            
        return valid_moves

    def is_valid_move(self, start: str, end: str):
        '''
        Checks if the move from start to end is valid for this piece.
        Parameters:
            start (str): The starting square of the piece (e.g., 'e2').
            end (str): The ending square of the piece (e.g., 'e4').
        Returns:
            bool: True if the move is valid, False otherwise.
        '''
        if end in self.get_valid_moves(start):
            return True
        return False

class Knight:
    '''
    Represents a knight piece and its movement rules.
    '''
    def __init__(self, pos, color, board):
        '''
        Initializes the knight with its position and color.
        Parameters:
            pos(str): position
            color(str): color of piece ('black' or 'white')
            board(dictionary): board dictionary
        '''
        self._position = pos
        self._color = color
        self._board = board

    def get_valid_moves(self, pos): 
        '''
        Returns a list of valid moves based on the knights's position.
        Parameters:
            pos (str): The position of the knight on the board.
        Returns:
            list[str]: A list of valid moves (e.g., ['e3', 'e4']).
        '''
        valid_moves = []
        row, col = int(pos[1]), pos[0]  
        moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                 (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for move in moves:
            newRow = row + move[0] 
            newCol = ord(col) + move[1] 

            if newRow in range(1, 9) and newCol in range(ord('a'), ord('h') + 1):
                newPos = chr(newCol) + str(newRow)
                if self._board.get_board().get(newPos, None) == '.':
                        valid_moves.append(newPos)
                elif any(pos == newPos for pos, _ in self._board.get_opponent_pieces(self._color)):
                    valid_moves.append(newPos)

        return valid_moves

    def is_valid_move(self, start: str, end: str):
        '''
        Checks if the move from start to end is valid for this piece.
        Parameters:
            start (str): The starting square of the piece (e.g., 'e2').
            end (str): The ending square of the piece (e.g., 'e4').
        Returns:
            bool: True if the move is valid, False otherwise.
        '''
        if end in self.get_valid_moves(start):
            return True
        return False

class Bishop:
    '''
    Represents a bishop piece and its movement rules.
    '''
    def __init__(self, pos, color, board):
        '''
        Initializes the bishop with its position and color.
        Parameters:
            pos(str): position
            color(str): color of piece ('black' or 'white')
            board(dictionary): board dictionary
        '''
        self._position = pos
        self._color = color
        self._board = board

    def get_valid_moves(self, pos): 
        '''
        Returns a list of valid moves based on the bishop's position.
        Parameters:
            pos (str): The position of the rook on the board.
        Returns:
            list[str]: A list of valid moves (e.g., ['e3', 'e4']).
        '''
        valid_moves = []
        row, col = int(pos[1]), pos[0]  
         # Directions: Diagonally Up-Left, Up-Right, Down-Left, Down-Right
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for direction in directions:
            for index in range(1, 8):  
                newRow = row + direction[0] * index
                newCol = ord(col) + direction[1] * index
                
                if newRow in range(1, 9) and newCol in range(ord('a'), ord('h') + 1):
                    newPos = chr(newCol) + str(newRow)
                    if self._board.get_board().get(newPos, None) == '.':
                        valid_moves.append(newPos)
                    else:
                        if any(newPos == pos for pos, _ in self._board.get_opponent_pieces(self._color)):
                            valid_moves.append(newPos)
                        break  # Stop checking further in this direction
            
        return valid_moves

    def is_valid_move(self, start: str, end: str):
        '''
        Checks if the move from start to end is valid for this piece.
        Parameters:
            start (str): The starting square of the piece (e.g., 'e2').
            end (str): The ending square of the piece (e.g., 'e4').
        Returns:
            bool: True if the move is valid, False otherwise.
        '''
        if end in self.get_valid_moves(start):
            return True
        return False

class Queen:
    '''
    Represents a queen piece and its movement rules.
    '''
    def __init__(self, pos, color, board):
        '''
        Initializes the queen with its position and color.
        Parameters:
            pos(str): position
            color(str): color of piece ('black' or 'white')
            board(dictionary): board dictionary
        '''
        self._position = pos
        self._color = color
        self._board = board

    def get_valid_moves(self, pos): 
        '''
        Returns a list of valid moves based on the queen's position.
        Parameters:
            pos (str): The position of the queen on the board.
        Returns:
            list[str]: A list of valid moves (e.g., ['e3', 'e4']).
        '''
        valid_moves = []
        row, col = int(pos[1]), pos[0]  
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), 
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for direction in directions:
            for index in range(1, 8):
                newRow = row + direction[0] * index
                newCol = ord(col) + direction[1] * index
                
                if newRow in range(1, 9) and newCol in range(ord('a'), ord('h') + 1):
                    newPos = chr(newCol) + str(newRow)
                    if self._board.get_board().get(newPos, None) == '.':
                        valid_moves.append(newPos)
                    else:
                        if any(newPos == pos for pos, _ in self._board.get_opponent_pieces(self._color)):
                            valid_moves.append(newPos)
                        break  # Stop checking further in this direction
            
        return valid_moves

    def is_valid_move(self, start: str, end: str):
        '''
        Checks if the move from start to end is valid for this piece.
        Parameters:
            start (str): The starting square of the piece (e.g., 'e2').
            end (str): The ending square of the piece (e.g., 'e4').
        Returns:
            bool: True if the move is valid, False otherwise.
        '''
        if end in self.get_valid_moves(start):
            return True
        return False

class King:
    '''
    Represents a king piece and its movement rules.
    '''
    def __init__(self, pos, color, board):
        '''
        Initializes the king with its position and color.
        Parameters:
            pos(str): position
            color(str): color of piece ('black' or 'white')
            board(dictionary): board dictionary
        '''
        self._position = pos
        self._color = color
        self._board = board

    def get_valid_moves(self, pos): 
        '''
        Returns a list of valid moves based on the king's position.
        Parameters:
            position (str): The position of the king on the board.
        Returns:
            list[str]: A list of valid moves (e.g., ['e3', 'e4']).
        '''
        valid_moves = []
        row, col = int(pos[1]), pos[0]  
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), 
                    (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for direction in directions:
            newRow = row + direction[0]
            newCol = ord(col) + direction[1]

            if newRow in range(1, 9) and newCol in range(ord('a'), ord('h') + 1):
                newPos = chr(newCol) + str(newRow)
                if self._board.get_board().get(newPos, None) == '.':
                        valid_moves.append(newPos)
                elif any(pos == newPos for pos, _ in self._board.get_opponent_pieces(self._color)):
                    valid_moves.append(newPos)
    
        return valid_moves

    def is_valid_move(self, start: str, end: str):
        '''
        Checks if the move from start to end is valid for this piece.
        Parameters:
            start (str): The starting square of the piece (e.g., 'e2').
            end (str): The ending square of the piece (e.g., 'e4').
        Returns:
            bool: True if the move is valid, False otherwise.
        '''
        if end in self.get_valid_moves(start):
            return True
        return False 

class Falcon:
    '''
    Represents a falcon piece and its movement rules.
    '''
    def __init__(self, pos, color, board):
        '''
        Initializes the falcon with its position and color.
        Parameters:
            pos(str): position
            color(str): color of piece ('black' or 'white')
            board(dictionary): board dictionary
        '''
        self._position = pos
        self._color = color
        self._board = board

    def get_valid_moves(self, pos): 
        '''
        Returns a list of valid moves based on the falcon's position.
        Parameters:
            pos (str): The position of the falcon on the board.
        Returns:
            list[str]: A list of valid moves (e.g., ['e3', 'e4']).
        '''
        valid_moves = []
        row, col = int(pos[1]), pos[0]  
        if self._color == 'white':
            directions = [(-1, 0), (1, 1), (1, -1)] 
        if self._color == 'black':
            directions = [(1, 0), (-1, -1), (-1, 1)] 

        for direction in directions:
            for index in range(1, 8):  
                newRow = row + direction[0] * index
                newCol = ord(col) + direction[1] * index
                
                if newRow in range(1, 9) and newCol in range(ord('a'), ord('h') + 1):
                    newPos = chr(newCol) + str(newRow)
                    if self._board.get_board().get(newPos, None) == '.':
                        valid_moves.append(newPos)
                    else:
                        if any(newPos == pos for pos, _ in self._board.get_opponent_pieces(self._color)):
                            valid_moves.append(newPos)
                        break  
            
        return valid_moves

    def is_valid_move(self, start: str, end: str):
        '''
        Checks if the move from start to end is valid for this piece.
        Parameters:
            start (str): The starting square of the piece (e.g., 'e2').
            end (str): The ending square of the piece (e.g., 'e4').
        Returns:
            bool: True if the move is valid, False otherwise.
        '''
        if end in self.get_valid_moves(start):
            return True
        return False

class Hunter:
    '''
    Represents a hunter piece and its movement rules.
    '''
    def __init__(self, pos, color, board):
        '''
        Initializes the hunter with its position and color.
        Parameters:
            pos(str): position
            color(str): color of piece ('black' or 'white')
            board(dictionary): board dictionary
        '''
        self._position = pos
        self._color = color
        self._board = board

    def get_valid_moves(self, pos): 
        '''
        Returns a list of valid moves based on the hunter's position.
        Parameters:
            pos(str): The position of the hunter on the board.
        Returns:
            list[str]: A list of valid moves (e.g., ['e3', 'e4']).
        '''
        valid_moves = []
        row, col = int(pos[1]), pos[0]  
        if self._color == 'white':
            directions = [(1, 0), (-1, -1), (-1, 1)] 
        if self._color == 'black':
            directions = [(-1, 0), (1, -1), (1, 1)]   

        for direction in directions:
            for index in range(1, 8):  
                newRow = row + direction[0] * index
                newCol = ord(col) + direction[1] * index
                
                if newRow in range(1, 9) and newCol in range(ord('a'), ord('h') + 1):
                    newPos = chr(newCol) + str(newRow)
                    if self._board.get_board().get(newPos, None) == '.':
                        valid_moves.append(newPos)
                    else:
                        if any(newPos == pos for pos, _ in self._board.get_opponent_pieces(self._color)):
                            valid_moves.append(newPos)
                        break  
        
        return valid_moves

    def is_valid_move(self, start: str, end: str):
        '''
        Checks if the move from start to end is valid for this piece.
        Parameters:
            start (str): The starting square of the piece (e.g., 'e2').
            end (str): The ending square of the piece (e.g., 'e4').
        Returns:
            bool: True if the move is valid, False otherwise.
        '''
        if end in self.get_valid_moves(start):
            return True
        return False




# if __name__ == "__main__":
#     game = ChessVar()
#     while game.get_game_state() == "UNFINISHED":
#         origin = input("> Origin: ")
#         if origin == 'e':
#             break
#         destination = input("> Destination: ")
#         if destination == 'e':
#             break
#         if origin in ('f', 'F', 'h', 'H'):
#             game.enter_fairy_piece(origin, destination)
#         else:
#             game.make_move(origin, destination)