import Utils
from collections import defaultdict

class GameState():

    def __init__(self, fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        Utils.precompute_data()
        self.board, self.whites_turn, self.castling, self.enpassant, self.halfmove, self.fullmove = Utils.fen_to_array(fen_string)
        self.move_log = []
        self.enpassant = [self.enpassant] # turn it into a 1 element array
        self.last_piece_captured = []
        ### add a last_piece_captured list, like move_log

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

        ### undoing a dp --> reset square that is enpassant eligible back
        ### undoing an ep --> undo move as normal and restore the last_piece_captured next to new pawn pos, pop 
        ### undoing a KC --> undo king move, move rook back, and add letter back to self.castling
        ### undoing a QC --> undo king move, move rook back, and add letter back to self.castling
        ### undoing a PC --> pop last_piece_captured off of list 
        ### undoing a PQ --> undo move normally, pop from queue if flag contains PC

        ### legal moves responsible for setting flags, and we only check if actual squares match input

        ### maybe assume queen promotion always for now, but make sure to count all possibilities in count_moves.


        ### add flag to move log, containing undo information
        ### format of this info?

        first_piece = move.piece_moved
        second_piece = move.piece_captured
        if Utils.is_friendly_piece(self, first_piece) and (not Utils.is_friendly_piece(self, second_piece) or second_piece == '--'):
            legal_moves = self.generate_pseudo_legal_moves()
            # print("Number of moves: ", len(legal_moves))
            # print("Legal moves: ", legal_moves)
            move_to_make = ((move.start_row, move.start_col), (move.end_row, move.end_col))

            if move_to_make in legal_moves:
                flag = legal_moves[move_to_make] # can have multiple flags.
                start_x = move.start_row
                start_y = move.start_col
                end_x = move.end_row
                end_y = move.end_col
                end_piece = move.piece_moved
                turn_char = "w"
                if not self.whites_turn:
                    turn_char = "b"
                set_enpassant = False
                if len(flag) > 1: 
                    end_piece = turn_char + "Q"
                    if "PC" in flag:
                        self.last_piece_captured.append(self.board[end_x][end_y])
                else:
                    if flag[0] == "DP":
                        assert move.start_col == move.end_col
                        set_enpassant = True
                    elif flag[0] == "EP":
                        assert self.enpassant[-1] != "-"
                        self.last_piece_captured.append(self.board[start_x][start_y + (end_y - start_y)])
                        self.board[start_x][start_y + (end_y - start_y)] = "--"
                        end_x, end_y = Utils.get_square_at_board_index(Utils.get_board_num_from_notation(self.enpassant[-1]))
                    elif flag[0] == "KC":
                        self.board[end_x][end_y + 1] = "--"
                        self.board[end_x][end_y - 1] = turn_char + "R"
                        replace_char = "K" if self.whites_turn else "k"
                        self.castling = self.castling.replace(replace_char, "")
                    elif flag[0] == "QC":
                        self.board[end_x][end_y - 2] = "--"
                        self.board[end_x][end_y + 1] = turn_char + "R"
                        replace_char = "Q" if self.whites_turn else "q"
                        self.castling = self.castling.replace(replace_char, "")
                    elif flag[0] == "PC":
                        self.last_piece_captured.append(self.board[end_x][end_y])
                self.board[start_x][start_y] = '--'
                self.board[end_x][end_y] = end_piece
                self.move_log.append((move, flag))
                self.whites_turn = not self.whites_turn
                if set_enpassant:
                    self.enpassant.append(Utils.get_rank_file(min(move.start_row, move.end_row) + 1, move.start_col))
                    set_enpassant = False
                else:
                    self.enpassant.append("-")
            else:
                print("Not a valid move!")

    # need to make sure undoing a move restores values like enpassant, castling rights, etc
    # after popping off the move, check its flag, and undo and values changed due to that flag.
    def undo_move(self):
        if self.move_log:
            move, flag = self.move_log.pop()
            turn_char = "b"
            if not self.whites_turn:
                turn_char = "w"
            if len(flag) > 1:
                if "PC" in flag:
                    self.last_piece_captured.pop()
            else:
                if flag[0] == "DP":
                    pass
                elif flag[0] == "EP":
                ## get square next to , replace with pawn
                    pawn_captured = self.last_piece_captured[-1]
                    self.board[move.start_row][move.start_col + (move.end_col - move.start_col)] = pawn_captured
                    self.last_piece_captured.pop()
                elif flag[0] == "KC":
                ## undo the rook move
                    self.board[move.end_row][move.end_col + 1] = turn_char + "R"
                    self.board[move.end_row][move.end_col - 1] = "--"
                    replace_char = "K" if not self.whites_turn else "k"
                    self.castling += replace_char
                elif flag[0] == "QC":
                    self.board[move.end_row][move.end_col - 2] = turn_char + "R"
                    self.board[move.end_row][move.end_col + 1] = "--"
                    replace_char = "Q" if not self.whites_turn else "q"
                    self.castling += replace_char
                elif flag[0] == "PC":
                    self.last_piece_captured.pop()

            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whites_turn = not self.whites_turn

            self.enpassant.pop()

    ### each generation function is responsible for mutating the 1 dictionary keeping track of moves and flags
    def generate_pseudo_legal_moves(self):
        possible_moves = defaultdict(lambda: [])
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                board_num = i * 8 + j
                if (Utils.is_friendly_piece(self, board_num)):
                    if ('P' in piece):
                        self.generate_pawn_moves(board_num, possible_moves)
                    elif ('Q' in piece):
                        self.generate_sliding_moves(board_num, 'Q', possible_moves)
                    elif ('K' in piece):
                        self.generate_king_moves(board_num, possible_moves)
                    elif ('B' in piece):
                        self.generate_sliding_moves(board_num, 'B', possible_moves)
                    elif ('R' in piece):
                        self.generate_sliding_moves(board_num, 'R', possible_moves)
                    elif ('N' in piece):
                        self.generate_knight_moves(board_num, possible_moves)
        return possible_moves

    def generate_sliding_moves(self, board_num, piece_type, possible_moves):
        start_index = 4 if piece_type == 'B' else 0
        end_index = 4 if piece_type == 'R' else 8
        piece_on_current_square = Utils.get_square_at_board_index(board_num)
        for direction_index in range(start_index, end_index):
            for n in range(Utils.squares_to_edge[board_num][direction_index]):
                target_square = board_num + Utils.direction_offsets[direction_index] * (n + 1)
                if (Utils.is_friendly_piece(self, target_square)):
                    break
                piece_on_target_square = Utils.get_square_at_board_index(target_square)
                if (not Utils.is_friendly_piece(self, target_square) and Utils.get_piece_at_board_index(self, target_square) != '--'):
                    possible_moves[(piece_on_current_square, piece_on_target_square)] = ["PC"]
                    break
                else:
                    possible_moves[(piece_on_current_square, piece_on_target_square)] = ["NM"]

    def generate_pawn_moves(self, board_num, possible_moves):
        current_square = Utils.get_square_at_board_index(board_num)
        rank = Utils.get_rank(board_num)
        file = Utils.get_file(board_num)
        if (self.whites_turn):
            if rank == 2:
                if Utils.get_piece_at_board_index(self, board_num - 8) == '--' and Utils.get_piece_at_board_index(self, board_num - 16) == '--':
                    target_square = Utils.get_square_at_board_index(board_num - 16)
                    possible_moves[(current_square, target_square)] = ["DP"]
            if rank == 7:
                self.generate_pawn_promotion_moves(board_num, possible_moves)
            else:
                if Utils.get_piece_at_board_index(self, board_num - 8) == '--':
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num - 8))] = ["NM"]
                if file != 1 and Utils.get_piece_at_board_index(self, board_num - 9)[0] == 'b':
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num - 9))] = ["PC"]
                if file != 8 and Utils.get_piece_at_board_index(self, board_num - 7)[0] == 'b':
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num - 7))] = ["PC"]
        else:
            if rank == 7:
                if Utils.get_piece_at_board_index(self, board_num + 8) == '--' and Utils.get_piece_at_board_index(self, board_num + 16) == '--':
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num + 16))] = ["DP"]
            if rank == 2:
                self.generate_pawn_promotion_moves(board_num, possible_moves)
            else:
                if Utils.get_piece_at_board_index(self, board_num + 8) == '--':
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num + 8))] = ["NM"]
                if file != 8 and Utils.get_piece_at_board_index(self, board_num + 9)[0] == 'w':
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num + 9))] = ["PC"]
                if file != 1 and Utils.get_piece_at_board_index(self, board_num + 7)[0] == 'w':
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num + 7))] = ["PC"]
        self.generate_en_passant_moves(board_num, possible_moves)

    ### enpassant wont work until in make_moves, we set the correct self.enpassant value directly after a double pawn push.
    def generate_en_passant_moves(self, board_num, possible_moves):
        if self.enpassant[-1] == '-':
            return 
        current_square = Utils.get_square_at_board_index(board_num)
        rank = Utils.get_rank(board_num)
        file = Utils.get_file(board_num)
        ep_num = Utils.get_board_num_from_notation(self.enpassant[-1]) # c3 -> 18
        if self.whites_turn:
            if rank == 5:
                if file != 1 and board_num - 9 == ep_num:
                    possible_moves[(current_square, Utils.get_square_at_board_index(ep_num))] = ["EP"]
                elif file != 8 and board_num - 7 == ep_num:
                    possible_moves[(current_square, Utils.get_square_at_board_index(ep_num))] = ["EP"]
        else:
            if rank == 4:
                if file != 8 and board_num + 9 == ep_num:
                    possible_moves[(current_square, Utils.get_square_at_board_index(ep_num))] = ["EP"]
                elif file != 1 and board_num + 7 == ep_num:
                    possible_moves[(current_square, Utils.get_square_at_board_index(ep_num))] = ["EP"]

    ## make sure, that pawns cannot move forward on 7th rank
    def generate_pawn_promotion_moves(self, board_num, possible_moves):
        promotion_pieces = ["Q", "R", "N", "B"]
        current_square = Utils.get_square_at_board_index(board_num)
        rank = Utils.get_rank(board_num)
        file = Utils.get_file(board_num)
        if self.whites_turn:
            if rank == 7:
                if Utils.get_piece_at_board_index(self, board_num - 8) == '--':
                    for piece in promotion_pieces:
                        possible_moves[(current_square, Utils.get_square_at_board_index(board_num - 8))] += ["P" + piece]
                if file != 1 and Utils.get_piece_at_board_index(self, board_num - 9)[0] == 'b':
                    for piece in promotion_pieces:
                        possible_moves[(current_square, Utils.get_square_at_board_index(board_num - 9))] += ["P" + piece]
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num - 9))] += ["PC"]
                if file != 8 and Utils.get_piece_at_board_index(self, board_num - 7)[0] == 'b':
                    for piece in promotion_pieces:
                        possible_moves[(current_square, Utils.get_square_at_board_index(board_num - 7))] += ["P" + piece]
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num - 7))] += ["PC"]
        else:
            if rank == 2:
                if Utils.get_piece_at_board_index(self, board_num + 8) == '--':
                    for piece in promotion_pieces:
                        possible_moves[(current_square, Utils.get_square_at_board_index(board_num + 8))] += ["P" + piece]
                if file != 8 and Utils.get_piece_at_board_index(self, board_num + 9)[0] == 'w':
                    for piece in promotion_pieces:
                        possible_moves[(current_square, Utils.get_square_at_board_index(board_num + 9))] += ["P" + piece]
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num + 9))] += ["PC"]
                if file != 1 and Utils.get_piece_at_board_index(self, board_num + 7)[0] == 'w':
                    for piece in promotion_pieces:
                        possible_moves[(current_square, Utils.get_square_at_board_index(board_num + 7))] += ["P" + piece]
                    possible_moves[(current_square, Utils.get_square_at_board_index(board_num + 7))] += ["PC"]

    def generate_king_moves(self, board_num, possible_moves):
        start_index = 0 
        end_index = 8
        piece_on_current_square = Utils.get_square_at_board_index(board_num)
        for direction_index in range(start_index, end_index):
            if Utils.squares_to_edge[board_num][direction_index] > 0:
                target_square = board_num + Utils.direction_offsets[direction_index]
                if Utils.is_friendly_piece(self, target_square):
                    continue
                piece_on_target_square = Utils.get_square_at_board_index(target_square)
                # if target square has an opp square, set flag to capture
                if (not Utils.is_friendly_piece(self, target_square) and Utils.get_piece_at_board_index(self, target_square) != '--'):
                    possible_moves[(piece_on_current_square, piece_on_target_square)] = ["PC"]
                else:
                    possible_moves[(piece_on_current_square, piece_on_target_square)] = ["NM"]
        ### castling, need to add concept of check in this. 
        if self.whites_turn:
            if "K" in self.castling and self.board[7][4] == "wK" and self.board[7][5] == "--" and self.board[7][6] == "--" and self.board[7][7] == "wR":
                possible_moves[((7, 4), (7, 6))] = ["KC"]
            if "Q" in self.castling and self.board[7][4] == "wK" and self.board[7][3] == "--" and self.board[7][2] == "--" and self.board[7][1] == "--" and self.board[7][0] == "wR":
                possible_moves[((7, 4), (7, 2))] = ["QC"]
        else:
            if "k" in self.castling and self.board[0][4] == "bK" and self.board[0][5] == "--" and self.board[0][6] == "--" and self.board[0][7] == "bR":
                possible_moves[((0, 4), (0, 6))] = ["KC"]
            if "q" in self.castling and self.board[0][4] == "bK" and self.board[0][3] == "--" and self.board[0][2] == "--" and self.board[0][1] == "--" and self.board[0][0] == "bR":
                possible_moves[((0, 4), (0, 2))] = ["QC"]


    def generate_knight_moves(self, board_num, possible_moves):
        piece_on_current_square = Utils.get_square_at_board_index(board_num)
        for i in range(len(Utils.knight_offsets_x)):
            x = Utils.get_rank(board_num)
            y = Utils.get_file(board_num)
            dx = Utils.knight_offsets_x[i]
            dy = Utils.knight_offsets_y[i]
            new_rank = x + dx
            new_file = y + dy
            new_pos = (8 - new_rank) * 8 + new_file - 1
            if (not 1 <= new_rank <= 8) or (not 1 <= new_file <= 8):
                continue
            if Utils.is_friendly_piece(self, new_pos):
                continue
            piece_on_target_square = Utils.get_square_at_board_index(new_pos)
            if (not Utils.is_friendly_piece(self, new_pos) and Utils.get_piece_at_board_index(self, new_pos) != '--'):
                possible_moves[(piece_on_current_square, piece_on_target_square)] = ["PC"]
            else:
                possible_moves[(piece_on_current_square, piece_on_target_square)] = ["NM"]

    ## for each pseudo legal move, play it and calculute all of opponents pseudo legal moves.
    ## if any of the responding moves results in the capture of the king, or capture of rook in the case of castling, then the move is invalid
    ## this forces moves to stop a check if a player is currently in check.
    def generate_legal_moves(self):
        pseudo_legal_moves = self.generate_pseudo_legal_moves()
        legal_moves = defaultdict(lambda: [])
        for pseudo_legal_move, flag in pseudo_legal_moves.items():
            move_to_make = Move(pseudo_legal_move[0], pseudo_legal_move[1], self.board)
            self.make_move(move_to_make)
            responses = self.generate_pseudo_legal_moves()
            is_legal = True
            for response, response_flag in responses.items():
                assert isinstance(response, tuple)
                if "PC" in response_flag and "K" in Utils.get_piece_at_index(self, response[1]):
                    is_legal = False
            if is_legal:
                legal_moves[pseudo_legal_move] = flag
            self.undo_move()
        return legal_moves


    def count_moves(self, depth):
        if depth == 0:
            return 1
        legal_moves = self.generate_legal_moves()
        num_pos = 0
        ## not counting when a move has multiple flags, wont be accurate for pawn promotion
        for legal_move, flag in legal_moves.items():
            move_to_make = Move(legal_move[0], legal_move[1], self.board)
            self.make_move(move_to_make)
            num_pos += self.count_moves(depth - 1)
            ### undoing a move may not be accurate, need to restore values back to what they were. 
            self.undo_move()
        return num_pos

    def count_moves_set(self, depth):
        move_dict = {}
        legal_moves = self.generate_legal_moves()
        for legal_move, flag in legal_moves.items():
            move_to_make = Move(legal_move[0], legal_move[1], self.board)
            self.make_move(move_to_make)
            move_dict[Utils.get_chess_notation(move_to_make)] = self.count_moves(depth - 1)
            self.undo_move()
        return move_dict

class Move():
    
    def __init__(self, start_square, end_square, board):
        # print(start_square)
        # print(end_square)
        assert start_square 
        assert end_square
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]