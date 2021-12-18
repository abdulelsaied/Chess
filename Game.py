import re

direction_offsets = [-8, 8, 1, -1, 7, -7, 9, -9]
squares_to_edge = {}


"""
Returns an array containing distances to edge for each square
squares_to_edge[i] = [n, s, e, w, sw, ne, se, nw]
"""
def precompute_data():
    for i in range(8):
        for j in range(8):
            board_num = i * 8 + j
            north = i
            south = 7 - i
            east = 7 - j
            west = j
            south_west = min(south, west)
            north_east = min(north, east)
            south_east = min(south, east)
            north_west = min(north, west)
            squares_to_edge[board_num] = [north, south, east, west, south_west, north_east, south_east, north_west]
    return squares_to_edge

def fen_to_array(fen_string):
    #assert re.match('\s*^(((?:[rnbqkpRNBQKP1-8]+\/){7})[rnbqkpRNBQKP1-8]+)\s([b|w])\s([K|Q|k|q]{1,4})\s(-|[a-h][1-8])\s(\d+\s\d+)$', fen_string)
    fields = fen_string.split(" ")
    assert len(fields) == 6
    board_info = fields[0]
    color = fields[1]
    castling = fields[2]
    enpassant = fields[3]
    halfmove = fields[4]
    fullmove = fields[5]

    # should import constants once its a class and use the value here
    board = [["--" for i in range(8)] for j in range(8)]
    current_rank = 0
    current_file = 0

    for char in board_info:
        piece = '--'
        if (char == '/'):
            current_rank += 1
            current_file = 0
        else:
            if (char.isdigit()): 
                current_file += int(char)
            else:
                if (char.isupper()): # white piece
                    board[current_rank][current_file] = 'w' + char
                else:
                    board[current_rank][current_file] = 'b' + char.upper()
                current_file += 1

    white_to_move = True
    if color == 'b':
        white_to_move = False
    
    return (board, white_to_move)
    
class GameState():

    def __init__(self, fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        precompute_data()
        self.board, self.whites_turn = fen_to_array(fen_string)
        self.move_log = []
        self.move_set = []


    def make_move(self, move):
        ### move must start with current players piece, end on empty square or an opponents piece
        first_piece = move.piece_moved
        second_piece = move.piece_captured
        if self.is_friendly_piece_string(first_piece) and (not self.is_friendly_piece_string(second_piece) or second_piece == '--'):
            ### validate move made here
            legal_moves = self.generate_pseudo_legal_moves()
            print("Number of moves: ", len(legal_moves))
            print("Legal moves: ", legal_moves)
            
            self.board[move.start_row][move.start_col] = '--'
            self.board[move.end_row][move.end_col] = move.piece_moved
            self.move_log.append(move)
            self.whites_turn = not self.whites_turn

    def undo_move(self):
        if self.move_log:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whites_turn = not self.whites_turn


    def generate_pseudo_legal_moves(self):
        possible_moves = []
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                board_num = i * 8 + j
                if (self.is_friendly_piece(board_num)):
                    if ('P' in piece): # this is a pawn
                        print("pawn")
                        possible_moves += (self.generate_pawn_moves(board_num))
                    elif ('Q' in piece):
                        print("queen")
                        possible_moves += (self.generate_sliding_moves(board_num, 'Q'))
                    elif ('K' in piece):
                        print("king")
                        possible_moves += (self.generate_king_moves(board_num))
                    elif ('B' in piece):
                        print("bishop")
                        possible_moves += (self.generate_sliding_moves(board_num, 'B'))
                    elif ('R' in piece):
                        print("rook")
                        possible_moves += (self.generate_sliding_moves(board_num, 'R'))
                    elif ('N' in piece):
                        print("knight")
                        possible_moves += (self.generate_knight_moves(board_num))
        return possible_moves

    # boardnum is a number from 0 to 63, i * 8 + j
    def generate_sliding_moves(self, board_num, piece_type):
        possible_moves = []
        start_index = 4 if piece_type == 'B' else 0
        end_index = 4 if piece_type == 'R' else 8
        piece_on_current_square = self.get_square_at_board_index(board_num)
        for direction_index in range(start_index, end_index): ## end_index + 1?
            for n in range(squares_to_edge[board_num][direction_index]):
                print(direction_index, n)
                target_square = board_num + direction_offsets[direction_index] * (n + 1)
                if (self.is_friendly_piece(target_square)):
                    print("piece blocked")
                    break
                piece_on_target_square = self.get_square_at_board_index(target_square)
                print(piece_on_current_square, piece_on_target_square, direction_index, n, squares_to_edge[board_num][direction_index])
                # possible_moves.append(Move(piece_on_current_square, piece_on_target_square, self.board))
                possible_moves.append((piece_on_current_square, piece_on_target_square))
                if (not self.is_friendly_piece(target_square) and self.get_piece_at_board_index(target_square) != '--'):
                    print("opponent piece in the way!")
                    print(self.get_piece_at_board_index(target_square))
                    break
        return possible_moves

    def generate_pawn_moves(self, board_num):
        possible_moves = []
        current_square = self.get_square_at_board_index(board_num)
        rank = self.get_rank(board_num)
        file = self.get_file(board_num)
        # if whites turn, check first if theres an empty space up left right, including check for edges
        # then, check if the piece is on the 2nd rank, eligible for 2 pawn moves 
        # 
        # add case for rank 7, where u can promote to a different piece
        if (self.whites_turn):
            if rank == 2:
                if self.get_piece_at_board_index(board_num - 16) == '--':
                    possible_moves.append((current_square, self.get_square_at_board_index(board_num - 16)))
            if self.get_piece_at_board_index(board_num - 8) == '--':
                possible_moves.append((current_square, self.get_square_at_board_index(board_num - 8)))
            if file != 1 and self.get_piece_at_board_index(board_num - 9)[0] == 'b':
                possible_moves.append((current_square, self.get_square_at_board_index(board_num - 9)))
            if file != 8 and self.get_piece_at_board_index(board_num - 7)[0] == 'b':
                possible_moves.append((current_square, self.get_square_at_board_index(board_num - 7))) 
        else:
            if rank == 7:
                if self.get_piece_at_board_index(board_num + 16) == '--':
                    possible_moves.append((current_square, self.get_square_at_board_index(board_num + 16)))
            if self.get_piece_at_board_index(board_num + 8) == '--':
                possible_moves.append((current_square, self.get_square_at_board_index(board_num + 8)))
            if file != 8 and self.get_piece_at_board_index(board_num + 9)[0] == 'w':
                possible_moves.append((current_square, self.get_square_at_board_index(board_num + 9)))
            if file != 1 and self.get_piece_at_board_index(board_num + 7)[0] == 'w':
                possible_moves.append((current_square, self.get_square_at_board_index(board_num + 7))) 
        return possible_moves

    # a king can move with all 8 offsets, but only 
    # fix this!!!!
    def generate_king_moves(self, board_num):
        possible_moves = []
        start_index = 0 
        end_index = 8
        piece_on_current_square = self.get_square_at_board_index(board_num)
        for direction_index in range(start_index, end_index):
            target_square = board_num + direction_offsets[direction_index]
            if self.is_friendly_piece(target_square):
                print("piece blocked")
                break
            piece_on_target_square = self.get_square_at_board_index(target_square)
            print(piece_on_current_square, piece_on_target_square, direction_index, n, squares_to_edge[board_num][direction_index])
            # possible_moves.append(Move(piece_on_current_square, piece_on_target_square, self.board))
            possible_moves.append((piece_on_current_square, piece_on_target_square))
            if (not self.is_friendly_piece(target_square) and self.get_piece_at_board_index(target_square) != '--'):
                print("opponent piece in the way!")
                print(self.get_piece_at_board_index(target_square))
                break
        return possible_moves

    def generate_knight_moves(self, board_num):
        return []

    def generate_legal_moves(self):
        pass

    def get_image_at_coordinates(self, xcoor, ycoor):
        return self.board[xcoor][ycoor]

    
    '''
    Returns the piece at a specific coordinate
    input: index ([0, 0])
    output: piece ('wP')
    '''
    def get_piece_at_index(self, index):
        return self.board[index[0]][index[1]]

    '''
    Returns the piece at a specific board index
    input: board_num (54)
    output: piece ('wP')
    '''
    def get_piece_at_board_index(self, board_num):
        assert board_num >= 0 and board_num <= 63
        row_value = board_num // 8
        col_value = board_num % 8
        return self.board[row_value][col_value] 

    '''
    Returns the square at a specific board index
    input: board_num (0)
    output: (0, 0)
    '''
    def get_square_at_board_index(self, board_num):
        row_value = board_num // 8
        col_value = board_num % 8
        return (row_value, col_value)     

    def is_friendly_piece(self, board_num):
        piece = self.get_piece_at_board_index(board_num)
        if (('w' in piece and self.whites_turn) or ('b' in piece and not self.whites_turn)):
            return True
        return False
    
    def is_friendly_piece_string(self, piece):
        if (('w' in piece and self.whites_turn) or ('b' in piece and not self.whites_turn)):
            return True
        return False

    def print_turn(self):
        if (self.whites_turn):
            print('Whites turn')
        else:
            print('Blacks turn')
    
    def get_rank(self, board_num):
        assert board_num > 0 and board_num < 64
        return abs(board_num - 63) // 8 + 1

    def get_file(self, board_num):
        assert board_num > 0 and board_num < 64
        return board_num % 8 + 1


class Move():

    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {i: j for j, i in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {i: j for j, i in files_to_cols.items()}
    
    def __init__(self, start_square, end_square, board):
        assert start_square 
        assert end_square
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]


    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]
