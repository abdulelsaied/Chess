import Utils

direction_offsets = [-8, 8, 1, -1, 7, -7, 9, -9]
knight_offsets_x = [2, 1, -1, -2, -2, -1, 1, 2]
knight_offsets_y = [1, 2, 2, 1, -1, -2, -2, -1]
move_count_dict = {}
ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
rows_to_ranks = {i: j for j, i in ranks_to_rows.items()}
files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
cols_to_files = {i: j for j, i in files_to_cols.items()}

class GameState():


    def __init__(self, fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        Utils.precompute_data()
        self.board, self.whites_turn, self.castling, self.enpassant, self.halfmove, self.fullmove = Utils.fen_to_array(fen_string)
        self.move_log = []
        self.move_set = []


    def make_move(self, move):
        ### move must start with current players piece, end on empty square or an opponents piece
        ### need to add flags to each move:
        ### DP --> double pawn move --> save the square that is enpassant eligible. if the next flag isnt DP, clear this flag
        ### EP --> enpassant --> different pawn capture movement.
        ### KC --> kingside castle --> ensure that move generated from king function is correct, different king/rook movement
        ### QC --> queenside castle
        ### for both castling moves, the second_piece must be 2 squares from the king 
        ### NM --> normal move, do nothing special.
        ### PC --> piece captured, can add sound to this later.
        ### PQ --> pawn promotion to a queen
        ### PR --> pawn promotion to a rook
        ### PN --> pawn promotion to a Knight
        ### PB --> pawn promotion to a bishop

        ## change legal_moves to be a dictionary, where key is the tuple of start/end square, and value is the corresponding flag. 

        ### legal moves responsible for setting flags, and we only check if actual squares match input
        ### in the case of pawn promotion, we handle the case in a special manner, maybe doing some of the logic in Gui.py?


        first_piece = move.piece_moved
        second_piece = move.piece_captured
        if self.is_friendly_piece_string(first_piece) and (not self.is_friendly_piece_string(second_piece) or second_piece == '--'):

            legal_moves = self.generate_pseudo_legal_moves()
            # print("Number of moves: ", len(legal_moves))
            # print("Legal moves: ", legal_moves)
            if ((move.start_row, move.start_col), (move.end_row, move.end_col)) in legal_moves:  
                self.board[move.start_row][move.start_col] = '--'
                self.board[move.end_row][move.end_col] = move.piece_moved
                self.move_log.append(move)
                self.whites_turn = not self.whites_turn
            else:
                print("Not a valid move!")
                print(((move.start_row, move.start_col), (move.end_row, move.end_col)))
        # print(self.enpassant)

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
                        # print("pawn")
                        possible_moves += (self.generate_pawn_moves(board_num))
                    elif ('Q' in piece):
                        # print("queen")
                        possible_moves += (self.generate_sliding_moves(board_num, 'Q'))
                    elif ('K' in piece):
                        # print("king")
                        possible_moves += (self.generate_king_moves(board_num))
                    elif ('B' in piece):
                        # print("bishop")
                        possible_moves += (self.generate_sliding_moves(board_num, 'B'))
                    elif ('R' in piece):
                        # print("rook")
                        possible_moves += (self.generate_sliding_moves(board_num, 'R'))
                    elif ('N' in piece):
                        # print("knight")
                        possible_moves += (self.generate_knight_moves(board_num))
        return possible_moves

    # boardnum is a number from 0 to 63, i * 8 + j
    def generate_sliding_moves(self, board_num, piece_type):
        possible_moves = []
        start_index = 4 if piece_type == 'B' else 0
        end_index = 4 if piece_type == 'R' else 8
        piece_on_current_square = Utils.get_square_at_board_index(board_num)
        for direction_index in range(start_index, end_index): ## end_index + 1?
            for n in range(Utils.squares_to_edge[board_num][direction_index]):
                target_square = board_num + direction_offsets[direction_index] * (n + 1)
                if (self.is_friendly_piece(target_square)):
                    # print("piece blocked")
                    break
                piece_on_target_square = Utils.get_square_at_board_index(target_square)
                # print(piece_on_current_square, piece_on_target_square, direction_index, n, squares_to_edge[board_num][direction_index])
                # possible_moves.append(Move(piece_on_current_square, piece_on_target_square, self.board))
                possible_moves.append((piece_on_current_square, piece_on_target_square))
                if (not self.is_friendly_piece(target_square) and Utils.get_piece_at_board_index(self, target_square) != '--'):
                    # append move with capture flag
                    break
        return possible_moves


    # problem with pawn moves
    def generate_pawn_moves(self, board_num):
        possible_moves = []
        current_square = Utils.get_square_at_board_index(board_num)
        rank = self.get_rank(board_num)
        file = self.get_file(board_num)
        # if whites turn, check first if theres an empty space up left right, including check for edges
        # then, check if the piece is on the 2nd rank, eligible for 2 pawn moves 
        if (self.whites_turn):
            if rank == 2:
                if Utils.get_piece_at_board_index(self, board_num - 8) == '--' and Utils.get_piece_at_board_index(self, board_num - 16) == '--':
                    target_square = Utils.get_square_at_board_index(board_num - 16)
                    possible_moves.append((current_square, target_square)) 
            if rank == 7:
                possible_moves += self.generate_pawn_promotion_moves(board_num)
            else:
                if Utils.get_piece_at_board_index(self, board_num - 8) == '--':
                    possible_moves.append((current_square, Utils.get_square_at_board_index(board_num - 8)))
                if file != 1 and Utils.get_piece_at_board_index(self, board_num - 9)[0] == 'b':
                    possible_moves.append((current_square, Utils.get_square_at_board_index(board_num - 9)))
                if file != 8 and Utils.get_piece_at_board_index(self, board_num - 7)[0] == 'b':
                    possible_moves.append((current_square, Utils.get_square_at_board_index(board_num - 7))) 
        else:
            if rank == 7:
                if Utils.get_piece_at_board_index(self, board_num + 8) == '--' and Utils.get_piece_at_board_index(self, board_num + 16) == '--':
                    possible_moves.append((current_square, Utils.get_square_at_board_index(board_num + 16)))
            if rank == 2:
                possible_moves += self.generate_pawn_promotion_moves(board_num)
            else:
                if Utils.get_piece_at_board_index(self, board_num + 8) == '--':
                    possible_moves.append((current_square, Utils.get_square_at_board_index(board_num + 8)))
                if file != 8 and Utils.get_piece_at_board_index(self, board_num + 9)[0] == 'w':
                    possible_moves.append((current_square, Utils.get_square_at_board_index(board_num + 9)))
                if file != 1 and Utils.get_piece_at_board_index(self, board_num + 7)[0] == 'w':
                    possible_moves.append((current_square, Utils.get_square_at_board_index(board_num + 7))) 
        possible_moves += self.generate_en_passant_moves(board_num)
        return possible_moves

    def generate_en_passant_moves(self, board_num):
        if self.enpassant == '-':
            return []
        possible_moves = []
        current_square = Utils.get_square_at_board_index(board_num)
        rank = self.get_rank(board_num)
        file = self.get_file(board_num)
        ep_num = self.get_board_num_from_notation(self.enpassant) # c3 -> 18
        if self.whites_turn:
            if rank == 5:
                print("got here")
                if file != 1 and board_num - 9 == ep_num:
                    possible_moves.append((current_square, Utils.get_square_at_board_index(ep_num), "EP"))
                elif file != 8 and board_num - 7 == ep_num:
                    possible_moves.append((current_square, Utils.get_square_at_board_index(ep_num), "EP")) 
        else:
            if rank == 4:
                if file != 8 and board_num + 9 == ep_num:
                    possible_moves.append((current_square, Utils.get_square_at_board_index(ep_num), "EP"))
                elif file != 1 and board_num + 7 == ep_num:
                    possible_moves.append((current_square, Utils.get_square_at_board_index(ep_num), "EP"))
        return possible_moves

    def generate_pawn_promotion_moves(self, board_num):
        possible_moves = []
        promotion_pieces = ["Q", "R", "N", "B"]
        current_square = Utils.get_square_at_board_index(board_num)
        rank = self.get_rank(board_num)
        file = self.get_file(board_num)
        if self.whites_turn:
            if rank == 7:
                if Utils.get_piece_at_board_index(self, board_num - 8) == '--':
                    for piece in promotion_pieces:
                        possible_moves.append((current_square, Utils.get_square_at_board_index(board_num - 8), piece))
                if file != 1 and Utils.get_piece_at_board_index(self, board_num - 9)[0] == 'b':
                    for piece in promotion_pieces:
                        possible_moves.append((current_square, Utils.get_square_at_board_index(board_num - 9), piece))
                if file != 8 and Utils.get_piece_at_board_index(self, board_num - 7)[0] == 'b':
                    for piece in promotion_pieces:
                        possible_moves.append((current_square, Utils.get_square_at_board_index(board_num - 7), piece)) 
        else:
            if rank == 2:
                if Utils.get_piece_at_board_index(self, board_num + 8) == '--':
                    for piece in promotion_pieces:
                        possible_moves.append((current_square, Utils.get_square_at_board_index(board_num + 8), piece))
                if file != 8 and Utils.get_piece_at_board_index(self, board_num + 9)[0] == 'w':
                    for piece in promotion_pieces:
                        possible_moves.append((current_square, Utils.get_square_at_board_index(board_num + 9), piece))
                if file != 1 and Utils.get_piece_at_board_index(self, board_num + 7)[0] == 'w':
                    for piece in promotion_pieces:
                        possible_moves.append((current_square, Utils.get_square_at_board_index(board_num + 7), piece)) 
        return possible_moves


    # a king can move with all 8 offsets, but only 1 deep
    def generate_king_moves(self, board_num):
        possible_moves = []
        start_index = 0 
        end_index = 8
        piece_on_current_square = Utils.get_square_at_board_index(board_num)
        for direction_index in range(start_index, end_index):
            # print(squares_to_edge[board_num][direction_index])
            if Utils.squares_to_edge[board_num][direction_index] > 0:
                target_square = board_num + direction_offsets[direction_index]
                if self.is_friendly_piece(target_square):
                    # print("piece blocked")
                    continue
                piece_on_target_square = Utils.get_square_at_board_index(target_square)
                # print(piece_on_current_square, piece_on_target_square, direction_index, squares_to_edge[board_num][direction_index])
                possible_moves.append((piece_on_current_square, piece_on_target_square))
        return possible_moves

    # need to use rank/col to calculate bounds, then convert backwards if needed
    # need 2 offsets
    def generate_knight_moves(self, board_num):
        possible_moves = []
        piece_on_current_square = Utils.get_square_at_board_index(board_num)
        for i in range(len(knight_offsets_x)):
            x = self.get_rank(board_num)
            y = self.get_file(board_num)
            dx = knight_offsets_x[i]
            dy = knight_offsets_y[i]
            new_rank = x + dx
            new_file = y + dy
            # print("++")
            # print("rank: ", x)
            # print("file: ", y)
            # print("new_rank: ", new_rank)
            # print("new_file: ", new_file)
            new_pos = (8 - new_rank) * 8 + new_file - 1
            # print("new_pos: ", new_pos)
            # print("++")
            if (not 1 <= new_rank <= 8) or (not 1 <= new_file <= 8):
                continue
            if self.is_friendly_piece(new_pos):
                # print("piece blocked, knight")
                continue
            piece_on_target_square = Utils.get_square_at_board_index(new_pos)
            # print(piece_on_current_square, piece_on_target_square)
            possible_moves.append((piece_on_current_square, piece_on_target_square))
        return possible_moves

    def generate_legal_moves(self):
        pass


    def count_moves(self, depth):
        if depth == 0:
            return 1
        legal_moves = self.generate_pseudo_legal_moves()
        num_pos = 0
        for legal_move in legal_moves:
            move_to_make = Move(legal_move[0], legal_move[1], self.board)
            self.make_move(move_to_make)
            num_pos += self.count_moves(depth - 1)
            self.undo_move()
        return num_pos

    def count_moves_set(self, depth):
        move_dict = {}
        legal_moves = self.generate_pseudo_legal_moves()
        for legal_move in legal_moves:
            move_to_make = Move(legal_move[0], legal_move[1], self.board)
            self.make_move(move_to_make)
            move_dict[move_to_make.get_chess_notation()] = self.count_moves(depth - 1)
            self.undo_move()
        return move_dict




### todo:
### combine these functions, and handle each case in the function, 
### then move it to Utils and replace instances in Game/Gui
    def is_friendly_piece(self, board_num):
        piece = Utils.get_piece_at_board_index(self, board_num)
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
    
    """
    Returns the rank of a given board_num
    1 - 8
    """
    def get_rank(self, board_num):
        assert board_num > 0 and board_num < 64
        return abs(board_num - 63) // 8 + 1

    """
    Returns the file of a given board_num
    1 - 8
    """
    def get_file(self, board_num):
        assert board_num > 0 and board_num < 64
        return board_num % 8 + 1


    ## need function to convert e4 to board_num
    def get_board_num_from_notation(self, notation):
        new_rank = ranks_to_rows[notation[1]]
        new_file = files_to_cols[notation[0]]
        return new_rank * 8 + new_file

    ## function to convert board_num to e4
    def get_notation_from_board_num(self, board_num):
        return cols_to_files[self.get_file(board_num) - 1] + rows_to_ranks[self.get_rank(board_num) - 1]
    


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
