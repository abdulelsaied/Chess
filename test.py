import unittest
import Game
import Utils

class TestChessMethods(unittest.TestCase):

    # squares_to_edge[i] = [n, s, e, w, sw, ne, se, nw]
    def test_precompute_data(self):
        data = Utils.precompute_data()
        self.assertEqual(data[0], [0, 7, 7, 0, 0, 0, 7, 0])
        self.assertEqual(data[13], [1, 6, 2, 5, 5, 1, 2, 1])
        self.assertEqual(data[63], [7, 0, 0, 7, 0, 0, 0, 7])

    def test_fen_to_array(self):
        board, white_to_move, castling, enpassant, halfmove, fullmove = Utils.fen_to_array("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.assertEqual(board[0][0], "bR")
        self.assertEqual(board[4][4], "--")
        self.assertEqual(white_to_move, True)
        self.assertEqual(castling, "KQkq")
        self.assertEqual(enpassant, "-")
        self.assertEqual(halfmove, "0")
        self.assertEqual(fullmove, "1")
        board, white_to_move, castling, enpassant, halfmove, fullmove = Utils.fen_to_array("5rk1/q2b1pp1/1p2p1np/1B1pP3/1b6/5N2/1PQ2PPP/2R3K1 b - - 2 20")
        self.assertEqual(board[1][0], "bQ")
        self.assertEqual(board[5][5], "wN")
        self.assertEqual(white_to_move, False)

    def test_count_moves(self):
        gs = Game.GameState()
        # count = gs.count_moves(1)
        # self.assertEqual(count, 20)
        # count = gs.count_moves(2)
        # self.assertEqual(count, 400)
        # count = gs.count_moves(3)
        # self.assertEqual(count, 8902)
        # self.assertEqual(count["a2a3"], 380)
        # self.assertEqual(count["b2b3"], 420)
        # self.assertEqual(count["c2c3"], 420)
        # self.assertEqual(count["d2d3"], 539)
        # self.assertEqual(count["e2e3"], 599)
        # self.assertEqual(count["f2f3"], 380)
        # self.assertEqual(count["g2g3"], 420)
        # self.assertEqual(count["h2h3"], 380)
        # self.assertEqual(count["a2a4"], 420)
        # self.assertEqual(count["b2b4"], 421)
        # self.assertEqual(count["c2c4"], 441)
        # self.assertEqual(count["d2d4"], 560)
        # self.assertEqual(count["e2e4"], 600)
        # self.assertEqual(count["f2f4"], 401)
        # self.assertEqual(count["g2g4"], 421)
        # self.assertEqual(count["h2h4"], 420)
        # self.assertEqual(count["b1a3"], 400)
        # self.assertEqual(count["b1c3"], 440)
        # self.assertEqual(count["g1f3"], 440)
        # self.assertEqual(count["g1h3"], 400)
        count = gs.count_moves(4)
        self.assertEqual(count, 197281)
    
    def test_get_board_num_from_notation(self):
        self.assertEqual(Utils.get_board_num_from_notation("a1"), 56)
        self.assertEqual(Utils.get_board_num_from_notation("h3"), 47)
        self.assertEqual(Utils.get_board_num_from_notation("e4"), 36)

if __name__ == '__main__':
    unittest.main()