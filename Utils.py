squares_to_edge = {}
ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {i: j for j, i in ranks_to_rows.items()}
files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {i: j for j, i in files_to_cols.items()}
direction_offsets = [-8, 8, 1, -1, 7, -7, 9, -9]
knight_offsets_x = [2, 1, -1, -2, -2, -1, 1, 2]
knight_offsets_y = [1, 2, 2, 1, -1, -2, -2, -1]

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
    fields = fen_string.split(" ")
    assert len(fields) == 6
    board_info = fields[0]
    color = fields[1]
    castling = fields[2]
    enpassant = fields[3]
    halfmove = fields[4]
    fullmove = fields[5]

    board = [["--" for i in range(8)] for j in range(8)]
    current_rank = 0
    current_file = 0

    for char in board_info:
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
    
    return (board, white_to_move, castling, enpassant, halfmove, fullmove)

'''
Returns the piece at a specific coordinate
input: index ([0, 0])
output: piece ('wP')
'''
def get_piece_at_index(gamestate, index):
    return gamestate.board[index[0]][index[1]]


'''
Returns the piece at a specific board index
input: board_num (54)
output: piece ('wP')
'''
def get_piece_at_board_index(gamestate, board_num):
    assert board_num >= 0 and board_num <= 63
    row_value = board_num // 8
    col_value = board_num % 8
    return gamestate.board[row_value][col_value] 

'''
Returns the square at a specific board index
input: board_num (0)
output: (0, 0)
'''
def get_square_at_board_index(board_num):
    row_value = board_num // 8
    col_value = board_num % 8
    return (row_value, col_value)    
    
def is_friendly_piece(gamestate, piece):
    if isinstance(piece, int):
        piece = get_piece_at_board_index(gamestate, piece)
    if (('w' in piece and gamestate.whites_turn) or ('b' in piece and not gamestate.whites_turn)):
        return True
    return False

"""
Returns the rank of a given board_num
1 - 8
"""
def get_rank(board_num):
    assert board_num > 0 and board_num < 64
    return abs(board_num - 63) // 8 + 1

"""
Returns the file of a given board_num
1 - 8
"""
def get_file(board_num):
    assert board_num > 0 and board_num < 64
    return board_num % 8 + 1


## need function to convert e4 to board_num
def get_board_num_from_notation(notation):
    new_rank = ranks_to_rows[notation[1]]
    new_file = files_to_cols[notation[0]]
    return new_rank * 8 + new_file

## function to convert board_num to e4
def get_notation_from_board_num(board_num):
    return cols_to_files[get_file(board_num) - 1] + rows_to_ranks[get_rank(board_num) - 1]

def get_chess_notation(move):
        return get_rank_file(move.start_row, move.start_col) + get_rank_file(move.end_row, move.end_col)

def get_rank_file(row, col):
    return cols_to_files[col] + rows_to_ranks[row]

def print_turn(gamestate):
    if (gamestate.whites_turn):
        print('Whites turn')
    else:
        print('Blacks turn')