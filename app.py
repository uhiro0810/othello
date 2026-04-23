from flask import Flask, request, jsonify, render_template
import random
import copy

app = Flask(__name__)

WHITE = 1    # player
BLACK = -1   # AI
EMPTY = 0

game_state = {}


def make_board():
    board = [[EMPTY] * 8 for _ in range(8)]
    board[3][3] = BLACK
    board[4][4] = BLACK
    board[3][4] = WHITE
    board[4][3] = WHITE
    return board


def count_flips(board, x, y, color):
    if board[y][x] != EMPTY:
        return -1
    total = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dy == 0 and dx == 0:
                continue
            k = 0
            nx, ny = x, y
            while True:
                nx += dx
                ny += dy
                if not (0 <= nx < 8 and 0 <= ny < 8):
                    break
                if board[ny][nx] == EMPTY:
                    break
                if board[ny][nx] == -color:
                    k += 1
                elif board[ny][nx] == color:
                    total += k
                    break
    return total


def place_stone(board, x, y, color):
    board[y][x] = color
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dy == 0 and dx == 0:
                continue
            to_flip = []
            nx, ny = x, y
            while True:
                nx += dx
                ny += dy
                if not (0 <= nx < 8 and 0 <= ny < 8):
                    break
                if board[ny][nx] == EMPTY:
                    break
                if board[ny][nx] == -color:
                    to_flip.append((nx, ny))
                elif board[ny][nx] == color:
                    for fx, fy in to_flip:
                        board[fy][fx] = color
                    break


def valid_moves(board, color):
    return [[x, y] for y in range(8) for x in range(8)
            if count_flips(board, x, y, color) > 0]


def count_stones(board):
    black = sum(board[y][x] == BLACK for y in range(8) for x in range(8))
    white = sum(board[y][x] == WHITE for y in range(8) for x in range(8))
    return black, white


def random_playout(board):
    board = copy.deepcopy(board)
    color = BLACK
    while True:
        if not valid_moves(board, WHITE) and not valid_moves(board, BLACK):
            break
        color = -color
        moves = valid_moves(board, color)
        if moves:
            m = random.choice(moves)
            place_stone(board, m[0], m[1], color)
    return board


# Easy: random move
def ai_easy(board):
    moves = valid_moves(board, BLACK)
    return random.choice(moves) if moves else None


# Medium: minimize opponent's valid moves next turn
def ai_medium(board):
    moves = valid_moves(board, BLACK)
    if not moves:
        return None
    best, best_score = moves[0], float('inf')
    for m in moves:
        b = copy.deepcopy(board)
        place_stone(b, m[0], m[1], BLACK)
        score = len(valid_moves(b, WHITE))
        if score < best_score:
            best_score = score
            best = m
    return best


# Hard: Monte Carlo (10 playouts per candidate move)
def ai_hard(board, loops=10):
    moves = valid_moves(board, BLACK)
    if not moves:
        return None
    best, best_wins = moves[0], -1
    for m in moves:
        wins = 0
        for _ in range(loops):
            b = copy.deepcopy(board)
            place_stone(b, m[0], m[1], BLACK)
            final = random_playout(b)
            bc, wc = count_stones(final)
            if bc > wc:
                wins += 1
        if wins > best_wins:
            best_wins = wins
            best = m
    return best


def advance_game(next_color):
    board = game_state['board']
    nm_next = valid_moves(board, next_color)
    nm_other = valid_moves(board, -next_color)

    if not nm_next and not nm_other:
        bc, wc = count_stones(board)
        game_state['game_over'] = True
        game_state['turn'] = 0
        if wc > bc:
            game_state['winner'] = 'player'
            game_state['message'] = f'あなたの勝利！ あなた {wc} - AI {bc}'
        elif bc > wc:
            game_state['winner'] = 'ai'
            game_state['message'] = f'AIの勝利！ AI {bc} - あなた {wc}'
        else:
            game_state['winner'] = 'draw'
            game_state['message'] = f'引き分け！ {wc} 対 {bc}'
    elif not nm_next:
        game_state['turn'] = -next_color
        if next_color == WHITE:
            game_state['message'] = 'あなたはパスです — AIの番へ'
        else:
            game_state['message'] = 'AIはパスです — あなたの番へ'
    else:
        game_state['turn'] = next_color
        if next_color == WHITE:
            game_state['message'] = 'あなたの番です'
        else:
            game_state['message'] = 'AIが考えています...'


def get_state():
    board = game_state['board']
    turn = game_state.get('turn', WHITE)
    bc, wc = count_stones(board)
    vm = valid_moves(board, turn) if not game_state.get('game_over') and turn != 0 else []
    return {
        'board': board,
        'turn': turn,
        'valid_moves': vm,
        'player_score': wc,
        'ai_score': bc,
        'game_over': game_state.get('game_over', False),
        'winner': game_state.get('winner'),
        'message': game_state.get('message', ''),
        'difficulty': game_state.get('difficulty', 'medium'),
        'last_move': game_state.get('last_move'),
        'last_ai_move': game_state.get('last_ai_move'),
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/new_game', methods=['POST'])
def new_game():
    data = request.json or {}
    difficulty = data.get('difficulty', 'medium')
    game_state.clear()
    game_state['board'] = make_board()
    game_state['difficulty'] = difficulty
    game_state['game_over'] = False
    game_state['winner'] = None
    game_state['last_move'] = None
    game_state['last_ai_move'] = None

    first = random.choice([WHITE, BLACK])
    if first == WHITE:
        game_state['turn'] = WHITE
        game_state['message'] = 'あなたが先手です！'
    else:
        game_state['turn'] = BLACK
        game_state['message'] = 'AIが先手です — 考えています...'
    return jsonify(get_state())


@app.route('/api/move', methods=['POST'])
def player_move():
    if game_state.get('game_over'):
        return jsonify({'error': 'game over'}), 400
    if game_state.get('turn') != WHITE:
        return jsonify({'error': 'not your turn'}), 400

    data = request.json or {}
    x, y = data.get('x'), data.get('y')
    board = game_state['board']

    if count_flips(board, x, y, WHITE) <= 0:
        return jsonify({'error': 'invalid move'}), 400

    place_stone(board, x, y, WHITE)
    game_state['last_move'] = [x, y]
    game_state['last_ai_move'] = None
    advance_game(BLACK)
    return jsonify(get_state())


@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    if game_state.get('game_over'):
        return jsonify({'error': 'game over'}), 400
    if game_state.get('turn') != BLACK:
        return jsonify({'error': 'not ai turn'}), 400

    board = game_state['board']
    difficulty = game_state.get('difficulty', 'medium')

    if difficulty == 'easy':
        move = ai_easy(board)
    elif difficulty == 'medium':
        move = ai_medium(board)
    else:
        move = ai_hard(board, loops=10)

    if move:
        place_stone(board, move[0], move[1], BLACK)
        game_state['last_ai_move'] = move
    game_state['last_move'] = None
    advance_game(WHITE)
    return jsonify(get_state())


if __name__ == '__main__':
    app.run(debug=True, port=5000)
