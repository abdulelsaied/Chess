### file to contain helper functions useful in other classes.

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