import pygame as p 
import Game
import Utils

WIDTH = HEIGHT = 512
ROWS = COLS = 8
SQUARE_LENGTH = HEIGHT // ROWS 
FPS = 30
IMAGES = {}
PIECES = ['wP', 'bP', 'wR', 'bR', 'wN', 'bN', 'wB', 'bB', 'wK', 'bK', 'wQ', 'bQ']
COLORS = ['#ebecd0', '#779556']

WIN = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption('Chess Project')

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    gamestate = Game.GameState()
    load_images()
    run = True
    selected_square = ()
    clickable = False
    draggable = False
    drag_now = False
    image_to_drag = ""
    '''
    After each mouseclick, coordinates are captured in a tuple current_square
    The piece on that square is square_string
    This function should not handle any game logic, but call functions in game.py
    DOWN: 
    if clickable is true, there are 2 possibilities:
        clicked on new square --> make the move between selected_square and recently clicked square
        clicked on same square --> cancel clickable ability a
    if clickable is false, then we are starting the drag and drop process, so set selected_square to clicked button and drag to true
    MOTION: 
    if drag is true, image should follow cursor
    UP: 
    if selected_square, there are __ possibilities:
        letting go on same square, should set clickable to true and selected_square to same square
        letting go on different square, make move between selected_square and current square and reset all variables.
    '''
    while run:
        clock.tick(FPS)
        mx, my = p.mouse.get_pos()
        for event in p.event.get():
            if event.type == p.QUIT:
                run = False

            # sets square and piece corresponding to position of the mouse.
            current_square = get_current_square(p.mouse)
            current_piece = Utils.get_piece_at_index(gamestate, current_square)

            if event.type == p.MOUSEBUTTONDOWN:
                if (('w' in current_piece and gamestate.whites_turn) or ('b' in current_piece and not gamestate.whites_turn)):
                    if (clickable):
                        selected_square = ()
                        clickable = False
                        draggable = False
                        break
                    else:
                        selected_square = current_square 
                        draggable = True
                        drag_now = True
                    image_key = Utils.get_piece_at_index(gamestate, selected_square)
                    if image_key == '--':
                        break
                    image_to_drag = IMAGES[image_key]

            elif event.type == p.MOUSEBUTTONUP:
                drag_now = False
                if (not clickable and not draggable):
                    break
                if (current_square == selected_square):
                    clickable = True
                    draggable = False
                else:
                    move = Game.Move(selected_square, current_square, gamestate.board)
                    print(Utils.get_chess_notation(move))
                    gamestate.take_turn(move)
                    Utils.print_turn(gamestate)
                    selected_square = ()
                    clickable = False
                    draggable = False

            elif event.type == p.MOUSEMOTION:
                if selected_square and draggable:
                    drag_now = True
                    image_to_drag = IMAGES[Utils.get_piece_at_index(gamestate, selected_square)]

            elif event.type == p.KEYDOWN:
                if (event.key) == p.K_z:
                    print('pressed undo')
                    gamestate.undo_move()
        
        draw_gamestate(screen, gamestate)
        if p.mouse.get_pressed()[0]:
            draw_dragged_piece(screen, mx, my, image_to_drag, drag_now)
        p.display.flip()

def draw_gamestate(screen, gamestate):
    draw_board(screen)
    draw_pieces(screen, gamestate.board)

def draw_board(screen):
    for i in range(ROWS):
        for j in range(COLS):
            p.draw.rect(screen, COLORS[(i + j) % 2], p.Rect(j * SQUARE_LENGTH, i * SQUARE_LENGTH, SQUARE_LENGTH, SQUARE_LENGTH))

def draw_pieces(screen, board):
    for i in range(ROWS):
        for j in range(COLS):
            piece = board[i][j]
            if (piece != '--'):
                screen.blit(IMAGES[piece], p.Rect(j * SQUARE_LENGTH, i * SQUARE_LENGTH, SQUARE_LENGTH, SQUARE_LENGTH))

def draw_dragged_piece(screen, mx, my, image, drag_now):
    if (drag_now):
        screen.blit(image, (mx - 25, my - 25))

def load_images():
    for piece in PIECES:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + "-highres.png"), (SQUARE_LENGTH, SQUARE_LENGTH))

"""
Returns a tuple desribing the coordinates of a square clicked.
"""
def get_current_square(mouse):
    return (mouse.get_pos()[1] // SQUARE_LENGTH, mouse.get_pos()[0] // SQUARE_LENGTH)

if __name__ == '__main__':
    main()