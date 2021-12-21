import unittest
import Game

class TestChessMethods(unittest.TestCase):

    # squares_to_edge[i] = [n, s, e, w, sw, ne, se, nw]
    def test_precompute_data(self):
        data = Game.precompute_data()
        self.assertEqual(data[0], [0, 7, 7, 0, 0, 0, 7, 0])
        self.assertEqual(data[13], [1, 6, 2, 5, 5, 1, 2, 1])
        self.assertEqual(data[63], [7, 0, 0, 7, 0, 0, 0, 7])

    def test_fen_to_array(self):
        board, white_to_move, castling, enpassant, halfmove, fullmove = Game.fen_to_array("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.assertEqual(board[0][0], "bR")
        self.assertEqual(board[4][4], "--")
        self.assertEqual(white_to_move, True)
        self.assertEqual(castling, "KQkq")
        self.assertEqual(enpassant, "-")
        self.assertEqual(halfmove, "0")
        self.assertEqual(fullmove, "1")
        board, white_to_move, castling, enpassant, halfmove, fullmove = Game.fen_to_array("5rk1/q2b1pp1/1p2p1np/1B1pP3/1b6/5N2/1PQ2PPP/2R3K1 b - - 2 20")
        self.assertEqual(board[1][0], "bQ")
        self.assertEqual(board[5][5], "wN")
        self.assertEqual(white_to_move, False)

    def test_count_moves(self):
        gs = Game.GameState()
        count = gs.count_moves(1)
        self.assertEqual(count, 20)
        count = gs.count_moves(2)
        self.assertEqual(count, 400)
        # count = gs.count_moves(3)
        # self.assertEqual(count, 8902)
        count = gs.count_moves(4)
        self.assertEqual(count, 197281)
    
    def test_get_board_num_from_notation(self):
        gs = Game.GameState()
        self.assertEqual(gs.get_board_num_from_notation("a1"), 56)
        self.assertEqual(gs.get_board_num_from_notation("h3"), 47)
        self.assertEqual(gs.get_board_num_from_notation("e4"), 36)

if __name__ == '__main__':
    unittest.main()