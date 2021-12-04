from builtins import print

import PySimpleGUI as sg
import chess
import config as cf
import timeit
from operator import itemgetter
import random

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

    def message(self, mess):
        mess_layout = []
        text_mess = [sg.Text(text=mess, pad=(30, 20))]
        mess_layout.append(text_mess)
        mess_window = sg.Window(mess, mess_layout)
        e, v = mess_window.read()
        if (e == sg.WIN_CLOSED):
            mess_window.close()
class Game:
    is_human_turn = True
    selected = False
    position = (0, 0)
    PROMOTE_RANK = [0, 7]

    def __init__(self, is_human_turn):
        self.is_human_turn = is_human_turn

    def piece_at(self, pos):
        return board.piece_type_at(pos[0] * 8 + pos[1])

    def calc_piece_quantity(self):
        global board
        piece_quantity = 0
        for i in range(8):
            for j in range(8):
                if board.piece_type_at(i*8+j) != None:
                    piece_quantity += 1
        # print(piece_quantity)
        return piece_quantity

    def play(self, event):
        if self.is_human_turn: self.human_turn(event)

        if not self.is_human_turn:
            if board.legal_moves.count() == 0:
                if board.is_checkmate(): gui.message("You Win!")
                else: gui.message("Draw!")
                return
            print("Piece quantity: ", game.calc_piece_quantity())
            if game.calc_piece_quantity() == 7 or game.calc_piece_quantity() == 8:
                cf.piece_position_score['k'] = cf.piece_position_score['k_e']
                print("New:", cf.piece_position_score['k'])
            self.bot_turn()
            print(board.fen())

            if board.legal_moves.count() == 0:
                if board.is_checkmate(): gui.message("You Lose!")
                else: gui.message("Draw!")
                return

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
                        promo = gui.choose_piece_promotion()
                        move = chess.Move(from_square=chess.square(self.position[1], self.position[0]),
                                          to_square=chess.square(event[1], event[0]),
                                          promotion=int(promo))
                else:
                    move = chess.Move(from_square=chess.square(self.position[1], self.position[0]),
                                      to_square=chess.square(event[1], event[0]))
                if board.is_legal(move):
                    print("-------HUMAN--------")
                    global present_score, present_hash
                    score = bot.calculate_score(move)
                    hash = bot.calculate_hash(move)
                    present_score += score
                    present_hash ^= hash
                    board.push(move)
                    print("Score:", present_score)
                    print("Hash:", present_hash)
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
        global present_score, hit, move_visited, present_hash
        move_visited = 0
        hit = 0

        # bot.d.clear()
        best_move = bot.iterative_deepening()
        print(best_move)
        score = bot.calculate_score(best_move)
        hash = bot.calculate_hash(best_move)
        present_score += score
        present_hash ^= hash
        board.push(best_move)
        gui.update_board(window)
        self.is_human_turn = True
        print("Kich thuoc Transposision table:", len(bot.transpos_table))
        print("Hash:", present_hash)
        print("Node hit:", hit)
        print("Move visited:", move_visited)
        print("Score:", present_score)
        print(best_move)

class Bot:

    MAX_DEPTH = 0
    table = []
    # score of board searched
    transpos_table = dict()
    recent_use = dict()
    # list of move that should be search first
    pv_move = dict()

    def init_zobrist(self):
        check = []
        for i in range(12):
            self.table.append([])
        for i in range(12):
            for j in range(64):

                rand_num = random.randrange(1<<64 - 1)
                while rand_num in check:
                    rand_num = random.randrange(1<<64 - 1)
                check.append(rand_num)
                self.table[i].append(rand_num)

    def get_hash(self, board: chess.Board):
        h = 0
        for i in range(64):
            if board.piece_at(i) != None:
                h = h ^ self.table[cf.piece[board.piece_at(i).symbol()]][i]
        h = h ^ board.turn
        return h

    def calculate_hash(self, move: chess.Move):
        hash = 0
        from_square = move.from_square
        to_square = move.to_square
        piece_at_from_square = board.piece_at(from_square)
        piece_at_to_square = board.piece_at(to_square)

        # Nhap thanh
        if (piece_at_from_square.piece_type == chess.KING) & (abs(from_square - to_square) in range(2, 5)):
            if from_square > to_square:
                hash = hash ^ self.table[cf.piece[piece_at_from_square.symbol()]][from_square]
                hash = hash ^ self.table[cf.piece[piece_at_from_square.symbol()]][from_square - 2]
                hash = hash ^ self.table[cf.piece[board.piece_at(from_square - 4).symbol()]][from_square - 4]
                hash = hash ^ self.table[cf.piece[board.piece_at(from_square - 4).symbol()]][from_square - 1]
            else:
                hash = hash ^ self.table[cf.piece[piece_at_from_square.symbol()]][from_square]
                hash = hash ^ self.table[cf.piece[piece_at_from_square.symbol()]][from_square + 2]
                hash = hash ^ self.table[cf.piece[board.piece_at(from_square + 3).symbol()]][from_square + 3]
                hash = hash ^ self.table[cf.piece[board.piece_at(from_square + 3).symbol()]][from_square + 1]
        # Phong
        elif (piece_at_from_square.piece_type == chess.PAWN) & ((to_square in range(56, 64)) or (to_square in range(0, 8))):
            hash = hash ^ self.table[cf.piece[piece_at_from_square.symbol()]][from_square]
            if (piece_at_to_square != None):
                hash = hash ^ self.table[cf.piece[piece_at_to_square.symbol()]][to_square]
            hash = hash ^ self.table[cf.piece[chess.Piece(piece_type=move.promotion, color=piece_at_from_square.color).symbol()]][to_square]
        # An tot qua duong
        elif (piece_at_from_square.piece_type == chess.PAWN) & (abs(from_square-to_square) in [7, 9]) & (piece_at_to_square == None):
            hash = hash ^ self.table[cf.piece[piece_at_from_square.symbol()]][from_square]
            hash = hash ^ self.table[cf.piece[piece_at_from_square.symbol()]][to_square]
            if to_square > from_square:
                hash = hash ^ self.table[cf.piece[board.piece_at(to_square-8).symbol()]][to_square - 8]
            else:
                hash = hash ^ self.table[cf.piece[board.piece_at(to_square+8).symbol()]][to_square + 8]
        else:
            hash = hash ^ self.table[cf.piece[piece_at_from_square.symbol()]][from_square]
            hash = hash ^ self.table[cf.piece[piece_at_from_square.symbol()]][to_square]
            if piece_at_to_square != None:
                hash = hash ^ self.table[cf.piece[piece_at_to_square.symbol()]][to_square]

        return hash ^ piece_at_from_square.color ^ (not piece_at_from_square.color)

    def get_piece_score(self, piece : chess.Piece, pos):
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

    def get_piece_score_without_position(self, piece : chess.Piece):
        if piece == None:
            return 0
        symbol = piece.symbol().lower()
        color = piece.color
        if color:  # color = WHITE
            return cf.piece_score[symbol]
        else:
            return -cf.piece_score[symbol]

    def calculate_score_normal(self, move:chess.Move):
        from_square = move.from_square
        to_square = move.to_square
        piece_at_from_square = board.piece_at(from_square)
        piece_at_to_square = board.piece_at(to_square)

        score = 0
        # Nhap thanh
        if (piece_at_from_square.piece_type == chess.KING) & (abs(from_square-to_square) in range(2, 5)):
            if from_square > to_square:
                score -= self.get_piece_score(piece_at_from_square, from_square)
                score += self.get_piece_score(piece_at_from_square, from_square - 2)
                score -= self.get_piece_score(board.piece_at(from_square-4), from_square - 4)
                score += self.get_piece_score(board.piece_at(from_square-4), from_square - 1)
            else:
                score -= self.get_piece_score(piece_at_from_square, from_square)
                score += self.get_piece_score(piece_at_from_square, from_square + 2)
                score -= self.get_piece_score(board.piece_at(from_square + 3), from_square + 3)
                score += self.get_piece_score(board.piece_at(from_square + 3), from_square + 1)
        # Phong
        elif (piece_at_from_square.piece_type == chess.PAWN) & ((to_square in range(56, 64)) or (to_square in range(0, 8))):
            score -= self.get_piece_score(piece_at_from_square, from_square)
            score -= self.get_piece_score(piece_at_to_square, to_square)
            score += self.get_piece_score(chess.Piece(piece_type=move.promotion, color=piece_at_from_square.color), to_square)
        # An tot qua duong
        elif (piece_at_from_square.piece_type == chess.PAWN) & (abs(from_square - to_square) in [7, 9]) & (piece_at_to_square == None):
            score -= self.get_piece_score(piece_at_from_square, from_square)
            score += self.get_piece_score(piece_at_from_square, to_square)
            if to_square > from_square:
                score -= self.get_piece_score(board.piece_at(to_square - 8), to_square - 8)
            else:
                score -= self.get_piece_score(board.piece_at(to_square + 8), to_square + 8)
        else:
            score -= self.get_piece_score(piece_at_from_square, from_square)
            score += self.get_piece_score(piece_at_from_square, to_square)
            score -= self.get_piece_score(piece_at_to_square, to_square)

        return score

    def calculate_score_last_game(self, move:chess.Move):
        from_square = move.from_square
        to_square = move.to_square
        piece_at_from_square = board.piece_at(from_square)
        piece_at_to_square = board.piece_at(to_square)
        king_pos = 0
        for i in range(64):
            if board.piece_type_at(i) == chess.KING:
                if board.piece_at(i).color != piece_at_from_square.color:
                    king_pos = i
                    break

        x_from = int(from_square/8)
        y_from = from_square%8
        x_to = int(to_square/8)
        y_to = to_square % 8
        x_king = int(king_pos/8)
        y_king = king_pos%8
        prev_score = abs(x_from - x_king) + abs(y_from - y_king)
        score = abs(x_to - x_king) + abs(y_to - y_king)
        if piece_at_from_square.color == True: value = 300
        else: value = -300
        return int((14 - (score - prev_score))*value/14) - self.get_piece_score_without_position(piece_at_to_square)

    def get_score(self, board):
        score = 0
        for i in range(8):
            for j in range(8):
                pos = i*8+j
                score += self.get_piece_score(board.piece_at(pos), pos)
        return score

    def iterative_deepening(self):
        max_depth = 4
        if game.calc_piece_quantity() < 7:
            cf.piece_position_score['k'] = cf.piece_position_score['k_e']

        if game.calc_piece_quantity() < 5:
            self.calculate_score = self.calculate_score_last_game
        else:
            self.calculate_score = self.calculate_score_normal

        start = timeit.default_timer()

        for depth in range(2, max_depth+1):
            self.MAX_DEPTH = depth
            best_move = self.minimax(0, -800011, 800011, isMaxPlayer=False)

        end = timeit.default_timer()
        print("Time: ", end - start)
        # if best_move instanceof: print(1)
        # else: print(2)
        if (type(best_move) is chess.Move) == False: return list(board.legal_moves)[0]
        if not board.is_legal(best_move): return list(board.legal_moves)[0]
        return best_move

    def minimax(self, depth, alpha, beta, isMaxPlayer:bool):
        global present_score, hit, present_hash, move_visited

        if board.legal_moves.count() == 0:
            if board.is_checkmate():
                if isMaxPlayer:
                    return -800010
                else:
                    return 800010
            else:
                return 0

        if depth == self.MAX_DEPTH:
            return present_score

        better_move = []
        value = self.transpos_table.get(present_hash)
        if value != None:
            if value[1] >= self.MAX_DEPTH - depth:
                hit = hit + 1
                if depth == 0:
                    return self.pv_move[present_hash][0][2]
                else:
                    return value[0]
            else:
            #     self.transpos_table.pop(present_hash)
                better_move = self.pv_move[present_hash].copy()

        possibleMove = board.legal_moves
        # sort by score of move
        move_list = []
        for m in possibleMove:
            move = chess.Move.from_uci(str(m))
            temp_score = self.calculate_score(move)
            temp_hash = self.calculate_hash(move)
            move_list.append((temp_score, temp_hash, move))

        move_list.sort(key=itemgetter(0), reverse=isMaxPlayer)

        for move in move_list:
            better_move.append(move)

        if isMaxPlayer:
            alpha = -800010
        else:
            beta = 800010

        self.pv_move[present_hash] = []
        best_move = better_move[0][2]
        for move in better_move:
            temp_score = move[0]
            temp_hash = move[1]
            board.push(move[2])

            present_score += temp_score
            present_hash ^= temp_hash
            move_visited = move_visited + 1

            score = self.minimax(depth + 1, alpha, beta, not isMaxPlayer)

            board.pop()
            present_score -= temp_score
            present_hash ^= temp_hash

            if not isMaxPlayer:
                if score < beta:
                    beta = score
                    best_move = move[2]
                    self.pv_move[present_hash].append(move)
                if score <= alpha:
                    self.transpos_table[present_hash] = (score, self.MAX_DEPTH - depth)
                    if len(self.pv_move[present_hash]) == 0: self.pv_move[present_hash].append(move)
                    self.pv_move[present_hash].reverse()
                    if depth > 0: return score
            else:
                if score > alpha:
                    alpha = score
                    best_move = move[2]
                    self.pv_move[present_hash].append(move)
                if score >= beta:
                    self.transpos_table[present_hash] = (score, self.MAX_DEPTH - depth)
                    if len(self.pv_move[present_hash]) == 0: self.pv_move[present_hash].append(move)
                    self.pv_move[present_hash].reverse()
                    if depth > 0: return score

        self.pv_move[present_hash].reverse()

        if depth == 0: return best_move
        if isMaxPlayer:
            self.transpos_table[present_hash] = (alpha, self.MAX_DEPTH - depth)
            return alpha
        else:
            self.transpos_table[present_hash] = (beta, self.MAX_DEPTH - depth)
            return beta

    calculate_score = calculate_score_normal

#MAIN
gui = GUI()
game = Game(is_human_turn=True)
bot = Bot()


board = chess.Board(fen="8/2Q5/k2K4/8/8/8/8/8 w - - 3 70")
# 2k4q/P7/8/8/4K3/8/8/5Q2 w - - 1 56
move_visited = 0
present_score = bot.get_score(board)
bot.init_zobrist()
present_hash = bot.get_hash(board)
hit = 0

board_layout = gui.create_board_layout()
window = sg.Window("Chess", board_layout, margins=(0,0))

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break
    if (type(event) is tuple):
        game.play(event)

window.close()
