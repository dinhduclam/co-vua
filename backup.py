import PySimpleGUI as sg
import chess
import config as cf
import timeit
from operator import itemgetter
import random
# piece = {""}
move_visited = 0
# score = 0
board = chess.Board()
present_score = 0

class GUI:

    def render_square(self, image, key, location):
        if (location[0] + location[1]) % 2 == 0:
            color = cf.dark_color
        else:
            color = cf.light_color
        return sg.Button('', image_filename=image,
                         border_width=0, button_color=color,
                         pad=(0, 0), key=key)

    def create_board_layout(self):
        board_layout = []
        for i in range(7, -1, -1):
            row = [sg.Text(text=str(i+1), justification='center')]
            #
            for j in range(0, 8):
                if (board.piece_at(i * 8 + j) == None):
                    piece_image = cf.blank
                else:
                    piece_image = cf.images[board.piece_at(i * 8 + j).symbol()]
                row.append(self.render_square(piece_image, key=(i, j), location=(i, j)))
            board_layout.append(row)

        row = [sg.Text(" ")]
        for i in range(8):
            row.append(sg.Text(chr(ord('a') + i), size=(7, 1), justification='center', pad=(0, 0)))
        board_layout.append(row)

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
    PROMOTE_RANK = [0, 7]

    def __init__(self, is_human_turn):
        self.is_human_turn = is_human_turn

    def piece_at(self, pos):
        return board.piece_type_at(pos[0] * 8 + pos[1])

    def play(self, event):
        if self.is_human_turn: self.human_turn(event)

        if not self.is_human_turn:
            if board.legal_moves.count() == 0:
                if board.is_checkmate(): print("You Win!")
                else: print("Draw!")
                return

            self.bot_turn()

            if board.legal_moves.count() == 0:
                if board.is_checkmate(): print("You Lose!")
                else: print("Draw!")
                return

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
        elif self.selected:
            if event == self.position:
                self.selected = False
            else:
                if event[0] in self.PROMOTE_RANK and self.piece_at(self.position) == chess.PAWN:
                    move = chess.Move(from_square=chess.square(self.position[1], self.position[0]),
                                      to_square=chess.square(event[1], event[0]),
                                      promotion=chess.QUEEN)
                    if board.is_legal(move):
                        promo = self.choose_piece_promotion()
                        move = chess.Move(from_square=chess.square(self.position[1], self.position[0]),
                                          to_square=chess.square(event[1], event[0]),
                                          promotion=int(promo))
                else:
                    move = chess.Move(from_square=chess.square(self.position[1], self.position[0]),
                                      to_square=chess.square(event[1], event[0]))
                if board.is_legal(move):
                    print("-------HUMAN--------")
                    global present_score
                    score = bot.calculate_score(move)
                    present_score += score
                    board.push(move)
                    print("Score:", bot.evaluated(board), present_score)
                    print(move)
                    # print("Hash:", bot.hash(board))
                    gui.update_board(window)
                    window.refresh()
                    self.selected = False
                    self.is_human_turn = False
                else:
                    if self.piece_at(event) == None:
                        self.selected = False
                    else:
                        gui.restore_square_color(window, self.position)
                        self.position = event
        if self.selected:
            gui.change_square_selected(window, self.position)
        else:
            gui.restore_square_color(window, self.position)

    def bot_turn(self):
        print("--------BOT---------")
        global present_score
        global move_visited
        move_visited = 0

        start = timeit.default_timer()
        best_move = bot.min(board, 0, -800010)
        end = timeit.default_timer()
        print("Time: ", end-start)
        score = bot.calculate_score(best_move)
        present_score += score
        board.push(best_move)
        gui.update_board(window)
        self.is_human_turn = True
        # print("Hash:", bot.hash(board))
        print("Move visited:", move_visited)
        print("Score:", bot.evaluated(board), present_score)
        print(best_move)

class Bot:

    MAX_DEPTH = 5
    table = []

    def init_zobrist(self):
        for i in range(12):
            self.table.append([])
        for i in range(12):
            for j in range(64):
                self.table[i].append(random.randrange(1000000))

    def hash(self, board: chess.Board):
        h = 0
        for i in range(64):
            if board.piece_at(i) != None:
                h = h ^ self.table[cf.piece[board.piece_at(i).symbol()]][i]
        return h

    def get_score(self, piece : chess.Piece, pos):
        if piece == None:
            return 0
        symbol = piece.symbol().lower()
        color = piece.color
        row = int(pos/8)
        col = pos%8
        if color:  # color = WHITE
            return cf.piece_score[symbol] + cf.piece_position_score[symbol][7 - row][col]
        else:
            return -(cf.piece_score[symbol] + cf.piece_position_score[symbol][row][col])

    def calculate_score(self, move:chess.Move):
        from_square = move.from_square
        to_square = move.to_square
        piece_at_from_square = board.piece_at(from_square)
        piece_at_to_square = board.piece_at(to_square)

        score = 0
        # Nhap thanh
        if (piece_at_from_square.piece_type == chess.KING) & (abs(from_square-to_square) in range(2, 5)):
            if from_square > to_square:
                score -= self.get_score(piece_at_from_square, from_square)
                score += self.get_score(piece_at_from_square, from_square - 2)
                score -= self.get_score(board.piece_at(from_square-4), from_square - 4)
                score += self.get_score(board.piece_at(from_square-4), from_square - 1)
            else:
                score -= self.get_score(piece_at_from_square, from_square)
                score += self.get_score(piece_at_from_square, from_square + 2)
                score -= self.get_score(board.piece_at(from_square + 3), from_square + 3)
                score += self.get_score(board.piece_at(from_square + 3), from_square + 1)
        # Phong
        elif (piece_at_from_square.piece_type == chess.PAWN) & ((to_square in range(56, 64)) or (to_square in range(0, 8))):
            score -= self.get_score(piece_at_from_square, from_square)
            score -= self.get_score(piece_at_to_square, to_square)
            score += self.get_score(chess.Piece(piece_type=move.promotion, color=piece_at_from_square.color), to_square)
        else:
            score -= self.get_score(piece_at_from_square, from_square)
            score += self.get_score(piece_at_from_square, to_square)
            score -= self.get_score(piece_at_to_square, to_square)

        return score

    def evaluated(self, board):
        score = 0
        for i in range(8):
            for j in range(8):
                pos = i*8+j
                score += self.get_score(board.piece_at(pos), pos)
        return score

    def max(self, board, depth, beta):
        global present_score
        anpha = -800000
        global move_visited
        if board.legal_moves.count() == 0:
            if board.is_checkmate():
                return anpha-1
            else:
                return 0
        if (depth == self.MAX_DEPTH):
            return present_score
        possibleMove = board.legal_moves
        # sort by score of move
        move_list = []
        for m in possibleMove:
            move = chess.Move.from_uci(str(m))
            temp_score = self.calculate_score(move)
            move_list.append((temp_score, move))
        move_list.sort(key=itemgetter(0), reverse=True)

        for move in move_list:
            # move = chess.Move.from_uci(str(m))
            temp_score = move[0]
            present_score += temp_score
            board.push(move[1])
            move_visited = move_visited + 1
            score = self.min(board, depth+1, anpha)

            board.pop()
            present_score -= temp_score
            if  score >= beta:
                return score
            if score > anpha:
                anpha = score
                best_move = move[1]
        if depth == 0: return best_move
        return anpha

    def min(self, board, depth, anpha):
        global present_score
        beta = 800000
        global move_visited
        if board.legal_moves.count() == 0:
            if board.is_checkmate():
                return beta+1
            else:
                return 0
        if (depth == self.MAX_DEPTH):
            return present_score

        possibleMove = board.legal_moves
        # sort by score of move
        move_list = []
        for m in possibleMove:
            move = chess.Move.from_uci(str(m))
            temp_score = self.calculate_score(move)
            move_list.append((temp_score, move))
        move_list.sort(key=itemgetter(0), reverse=False)

        for move in move_list:
            # move = chess.Move.from_uci(str(m))
            temp_score = move[0]
            board.push(move[1])
            present_score += temp_score
            move_visited = move_visited + 1
            score = self.max(board, depth+1, beta)
            board.pop()
            present_score -= temp_score
            if score <= anpha:
                return score
            if score < beta:
                beta = score
                best_move = move[1]

        if depth == 0: return best_move
        return beta

#MAIN
gui = GUI()
game = Game(is_human_turn=True)
bot = Bot()

bot.init_zobrist()
board_layout = gui.create_board_layout()
window = sg.Window("Chess", board_layout, margins=(0,0))

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    if (type(event) is tuple):
        game.play(event)

window.close()
