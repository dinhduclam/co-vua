import PySimpleGUI as sg
import chess
import config as cf

# piece = {""}

board = chess.Board(fen="7r/2N4p/1Qn5/1p1R4/k7/8/PPPPPP1P/RNBQKB2 w Q - 2 19")

# rnbqkbnr/ppp3Pp/3pp3/8/8/8/PPPPPP1P/RNBQKBNR w KQkq - 0 5

class GUI:

    def render_square(self, image, key, location):
        if (location[0] + location[1]) % 2 == 0:
            color = cf.dark_color
        else:
            color = cf.light_color
        return sg.Button('', image_filename=image, size=(1, 1),
                         border_width=0, button_color=color,
                         pad=(0, 0), key=key)

    def create_board_layout(self):
        board_layout = []
        for i in range(7, -1, -1):
            row = []
            for j in range(0, 8):
                if (board.piece_at(i * 8 + j) == None):
                    piece_image = cf.blank
                else:
                    piece_image = cf.images[board.piece_at(i * 8 + j).symbol()]
                row.append(self.render_square(piece_image, key=(i, j), location=(i, j)))
            board_layout.append(row)
        board_layout.append([sg.Text(
            "     a             b             c             d             e              f              g              h")])
        return board_layout

    def update_board(self, window):
        for i in range(8):
            for j in range(8):
                if (board.piece_at(i * 8 + j) == None):
                    piece_image = cf.blank
                else:
                    piece_image = cf.images[board.piece_at(i * 8 + j).symbol()]
                window[(i, j)].update(image_filename=piece_image)

    def change_square_selected(self, window, position):
        if (position[0] + position[1]) % 2 == 0:
            color = cf.selected_dark_color
        else:
            color = cf.selected_light_color
        window[position].update(button_color=color)

    def restore_square_color(self, window, position):
        if (position[0] + position[1]) % 2 == 0:
            color = cf.dark_color
        else:
            color = cf.light_color
        window[position].update(button_color=color)

class Game:
    is_human_turn = True
    selected = False
    position = (0, 0)
    PROMOTE_RANK = 7

    def piece_at(self, pos):
        return board.piece_type_at(pos[0] * 8 + pos[1])

    def play(self, event):
        if self.is_human_turn: self.human_turn(event)

        if not self.is_human_turn:
            print("Score:", bot.evaluated(board))
            print(board)

            if board.legal_moves.count() == 0:
                if board.is_checkmate(): print("Lose!")
                else: print("Draw!")
                return
            print(board.legal_moves)
            best_move = bot.min(board, 0, -800000)
            print(best_move)
            board.push(best_move)
            gui.update_board(window)
            self.is_human_turn = True

        # self.is_human_turn = True
        # if not self.is_human_turn:
        #     self.bot_turn()

    def choose_piece_promotion(self):
        choose_layout = []
        row = []
        pie_choosed = 5
        for i in range(2, 6):
            row.append(sg.Button('', image_filename=cf.PIECE_PROMOTION[i-2], size=(1, 1),
                                          border_width=0, button_color=cf.light_color,
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
                if event[0] == self.PROMOTE_RANK and self.piece_at(self.position) == 1:
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
                    gui.update_board(window)
                    window.refresh()
                    self.selected = False
                    self.is_human_turn = False
                else:
                    if self.piece_at(event) == None:
                        self.selected = False
                        # print("unchoose:")
                    else:
                        gui.restore_square_color(window, self.position)
                        self.position = event
                        # print("choose:", self.position)
                # print(board.legal_moves)
        if self.selected:
            gui.change_square_selected(window, self.position)
        else:
            # print("restore:", self.position)
            gui.restore_square_color(window, self.position)
        # print(board)

    # def bot_turn(self):

class Bot:

    MAX_DEPTH = 3

    def evaluated(self, board):
        score = 0
        for i in range(8):
            for j in range(8):
                if (board.piece_type_at(i*8 + j) != None):
                    piece_symbol = board.piece_at(i * 8 + j).symbol().lower()
                    if board.color_at(i*8 + j):  #color = WHITE
                        score += cf.piece_score[piece_symbol] + cf.piece_position_score[piece_symbol][7-i][j]
                    else:
                        score -= cf.piece_score[piece_symbol] + cf.piece_position_score[piece_symbol][i][j]
        return score

    def max(self, board, depth, beta):
        anpha = -800000
        if board.legal_moves.count() == 0:
            if board.is_checkmate():
                return anpha
            else:
                return 0
        if (depth == self.MAX_DEPTH):
            return self.evaluated(board)
        possibleMove = board.legal_moves
        for m in possibleMove:
            move = chess.Move.from_uci(str(m))
            board.push(move)
            score = self.min(board, depth+1, anpha)
            board.pop()

            if score >= beta:
                return score
            if score > anpha:
                anpha = score
                best_move = move
        if depth == 0: return best_move
        return anpha

    def min(self, board, depth, anpha):
        beta = 800000
        if board.legal_moves.count() == 0:
            if board.is_checkmate():
                return beta
            else:
                return 0
        if (depth == self.MAX_DEPTH):
            return self.evaluated(board)

        possibleMove = board.legal_moves
        for m in possibleMove:
            move = chess.Move.from_uci(str(m))
            board.push(move)
            score = self.max(board, depth+1, beta)
            board.pop()
            if score <= anpha:
                return score
            if score <= beta:
                beta = score
                best_move = move

        if depth == 0: return best_move
        return beta

#MAIN
gui = GUI()
game = Game()
bot = Bot()
board_layout = gui.create_board_layout()
window = sg.Window("Chess", board_layout)


while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    if (type(event) is tuple):
        game.play(event)

window.close()
