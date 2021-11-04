import PySimpleGUI as sg
import os
import chess

IMAGE_PATH = 'Images/60'  # path to the chess pieces

blank = os.path.join(IMAGE_PATH, 'blank.png')
bishopB = os.path.join(IMAGE_PATH, 'bB.png')
bishopW = os.path.join(IMAGE_PATH, 'wB.png')
pawnB = os.path.join(IMAGE_PATH, 'bP.png')
pawnW = os.path.join(IMAGE_PATH, 'wP.png')
knightB = os.path.join(IMAGE_PATH, 'bN.png')
knightW = os.path.join(IMAGE_PATH, 'wN.png')
rookB = os.path.join(IMAGE_PATH, 'bR.png')
rookW = os.path.join(IMAGE_PATH, 'wR.png')
queenB = os.path.join(IMAGE_PATH, 'bQ.png')
queenW = os.path.join(IMAGE_PATH, 'wQ.png')
kingB = os.path.join(IMAGE_PATH, 'bK.png')
kingW = os.path.join(IMAGE_PATH, 'wK.png')

PIECE_PROMOTION = [knightW, bishopW, rookW, queenW]

images = {'b': bishopB, 'B': bishopW, 'p': pawnB, 'P': pawnW,
          'n': knightB, 'N': knightW,
          'r': rookB, 'R': rookW, 'k': kingB, 'K': kingW,
          'q': queenB, 'Q': queenW, None: blank}

light_color = '#235f53'
dark_color = '#CCC'
selected_color = '#2891f9'
# '#F0D9B5' '#B58863' vang`
# '#c51f83' '#eceed4' do
# '#235f53' 'white'  xanh


# piece = {""}

board = chess.Board()
# fen="7r/2N4p/1Qn5/1p1R4/k7/8/PPPPPP1P/RNBQKB2 w Q - 2 19"
# rnbqkbnr/ppp3Pp/3pp3/8/8/8/PPPPPP1P/RNBQKBNR w KQkq - 0 5

PROMOTE_RANK = 7

def render_square(image, key, location):
    if (location[0] + location[1]) % 2:
        color = dark_color
    else:
        color = light_color
    return sg.Button('', image_filename=image, size=(1, 1),
                      border_width=0, button_color=color,
                      pad=(0, 0), key=key)

def create_board_layout():
    board_layout = []
    for i in range(7, -1, -1):
        row = []
        for j in range(0, 8):
            if (board.piece_at(i*8+j) == None):
                piece_image = blank
            else:
                piece_image = images[board.piece_at(i*8+j).symbol()]
            row.append(render_square(piece_image, key=(i, j), location=(i, j)))
        board_layout.append(row)
    board_layout.append([sg.Text("     a             b             c             d             e              f              g              h")])
    return board_layout

def update_board(window):
    for i in range(8):
        for j in range(8):

            if (board.piece_at(i*8+j) == None):
                piece_image = blank
            else:
                piece_image = images[board.piece_at(i*8+j).symbol()]
            window[(i, j)].update(image_filename=piece_image)

def change_square_selected(window, position):
    window[position].update(button_color = selected_color)

def restore_square_color(window, position):
    if (position[0] + position[1]) % 2:
        color = dark_color
    else:
        color = light_color
    window[position].update(button_color = color)

class Game:
    is_human_turn = True
    selected = False
    position = (0, 0)

    def piece_at(self, pos):
        return board.piece_type_at(pos[0] * 8 + pos[1])

    def play(self, event):
        self.human_turn(event)
        print(board.legal_moves, board.legal_moves.count())
        print(board.is_checkmate())
        if board.legal_moves.count() == 0:
            if board.is_checkmate(): print("Lose!")
            else: print("Draw!")

        # if not self.is_human_turn:
        #     self.bot_turn()

    def choose_piece_promotion(self):
        choose_layout = []
        row = []
        pie_choosed = 5
        for i in range(2, 6):
            row.append(sg.Button('', image_filename=PIECE_PROMOTION[i-2], size=(1, 1),
                                          border_width=0, button_color=light_color,
                                          pad=(0, 0), key=i))
        choose_layout.append(row)
        choose_window = sg.Window("Choose Piece to Promotion", choose_layout)
        e, v = choose_window.read()
        if (e == sg.WIN_CLOSED):
            pie_choosed = 5
        else:
            pie_choosed = e

        choose_window.close()
        return pie_choosed
    def human_turn(self, event):
        if (not self.selected) and self.piece_at(event) != None:
            self.selected = True
            self.position = event
            print("choose:", self.position)
        elif self.selected:
            if event == self.position:
                self.selected = False
                print("unchoose")
            else:
                if event[0] == PROMOTE_RANK and self.piece_at(self.position) == 1:
                    move = chess.Move(from_square=chess.square(self.position[1], self.position[0]),
                                      to_square=chess.square(event[1], event[0]),
                                      promotion=5)
                    if board.is_legal(move):
                        promo = self.choose_piece_promotion()
                        print(type(promo), promo)
                        move = chess.Move(from_square=chess.square(self.position[1], self.position[0]),
                                          to_square=chess.square(event[1], event[0]),
                                          promotion=int(promo))
                    # print(board.is_legal(move))
                else:
                    move = chess.Move(from_square=chess.square(self.position[1], self.position[0]),
                                      to_square=chess.square(event[1], event[0]))
                # print(board.is_legal(move))
                if board.is_legal(move):
                    board.push(move)
                    update_board(window)
                    self.selected = False
                    self.is_human_turn = False
                    print(board.fen())
                else:
                    if self.piece_at(event) == None:
                        self.selected = False
                        # print("unchoose:")
                    else:
                        restore_square_color(window, self.position)
                        self.position = event
                        # print("choose:", self.position)
                # print(board.legal_moves)
        if self.selected:
            change_square_selected(window, self.position)
        else:
            # print("restore:", self.position)
            restore_square_color(window, self.position)
        # print(board)

    # def bot_turn(self):


board_layout = create_board_layout()

window = sg.Window("Chess", board_layout)
game = Game()

# check het co
# check phong hau

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    if (type(event) is tuple):
        game.play(event)

window.close()
