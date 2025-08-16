import random
import tkinter
import tkinter.messagebox

# 定義
WHITE = 1   # プレイヤー
BLACK = -1   # コンピュータ
EMPTY = 0
board = []
progress = 0   # ゲーム進行を管理する変数
turn = 0
mx = 0   # マスの列
my = 0   # マスの行
mc = 0   # クリックしたかどうかを判別する変数
put_able_list = []   # 石を置けるマスのリスト
back_board = []   # 盤面を保存するリスト
white_win = 0   # 白の勝利数
black_win = 0   # 黒の勝利数
draw = 0   # 引き分けの数
game = 0   # 総プレイ数

# クリックしたときに発動する関数
def click(e):
    global mx, my, mc
    mx = int(e.x / 80)   # クリックしたx座標から列を導出
    my = int(e.y / 80)   # クリックしたy座標から行を導出
    mc = 1   # mcに1を代入してクリックされたことを判定する
    return

# 盤面を表示する関数
def game_board():
    canvas.delete('all')   # キャンバスを初期化
    for i in range(9):
        X = i * 80   # 左から数えたマス目
        Y = i * 80   # 上から数えたマス目
        canvas.create_line(0, Y + 80, 640, Y + 80, fill = 'black', width = 2)   # 点(0, Y + 80), (640, Y + 80)を線で結ぶ(線の色は黒、幅2px)
        canvas.create_line(X + 80, 0, X + 80, 640, fill = 'black', width = 2)   # 点(X + 80, 0), (X + 80, 640)を線で結ぶ
    for y in range(8):
        for ｘ in range(8):
            X = x * 80   # マスの左端のx座標
            Y = y * 80   # マスの上端のy座標
            if board[y][x] == BLACK:
                canvas.create_oval(X + 10, Y + 10, X + 70, Y + 70, fill = 'black', width = 0)   #(X + 10, Y + 10), (X + 70, Y + 70)を直径の両端とする黒い円を描画
            if board[y][x] == WHITE:
                canvas.create_oval(X + 10, Y + 10, X + 70, Y + 70, fill = 'white', width = 0)
            if turn == 1:   # 自分のターンのときのみ配置可能なマスを表示
                if (reverse_stones_count(x, y, turn) > 0) and (mc == 0):   # 配置可能なマスであり、クリックしていない場合
                    if progress == 1:
                        canvas.create_rectangle(X + 1, Y + 1, X + 79, Y + 79, fill = 'gold', width = 0)
    canvas.update()   # キャンバスを更新
    return

# 盤面の初期化
def start_board():
    global board
    board.clear()
    for i in range(8):
        board.append([0] * 8)
    for y in range(8):
        for x in range(8):
            if ((x, y) == (3, 3)) or ((x, y) == (4, 4)):
                board[y][x] = BLACK
            elif ((x, y) == (3, 4)) or ((x, y) == (4, 3)):
                board[y][x] = WHITE
            else:
                board[y][x] = EMPTY
    return

#(x, y)マスに特定の色の石を置く関数
def put_stones(x, y, color): 
    board[y][x] = color
    for dy in range(-1, 2):
        for dx in range(-1, 2):   # 8方向のマスの状態を調べる
            k = 0   # 返せる石の個数
            nx = x
            ny = y
            while True:
                nx += dx
                ny += dy
                if (nx < 0) or (nx >= 8) or (ny < 0) or (ny >= 8):   # 指定するマスが盤面上にない場合
                    break
                if board[ny][nx] == EMPTY:
                    break
                if board[ny][nx] == color * (-1):   # 指定したマスに置かれている石が相手の石の場合
                    k += 1
                if board[ny][nx] == color:
                    for i in range(k):
                        nx -= dx
                        ny -= dy
                        board[ny][nx] = color   # 間の石を返す
                    break
    return

# 石を置いたときに返せる石の個数を調べる関数
def reverse_stones_count(x, y, color):
    if board[y][x] != EMPTY:   # 指定したマスに石が置かれていた場合
        return -1
    total = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):   # 8方向のマスの状態を調べる
            k = 0   # 返せる石の個数
            nx = x
            ny = y
            while True:
                nx += dx
                ny += dy
                if (nx < 0) or (nx >= 8) or (ny < 0) or (ny >= 8):   # 指定するマスが盤面上にない場合
                    break
                if board[ny][nx] == EMPTY:
                    break
                if board[ny][nx] == color * (-1):   # 指定したマスに置かれている石が相手の石の場合
                    k += 1
                if board[ny][nx] == color:
                    total += k
                    break
    return total


# 石を置けるマスがあるかどうかを調べる関数
def put_able(color):
    put_able_list.clear()
    for y in range(8):
        for x in range(8):
            if reverse_stones_count(x, y, color) > 0:
                put_able_list.append([x, y])
    if len(put_able_list) >= 1:   # 置けるマスがある場合
        return True
    return False


# 最終的なそれぞれの石の数を数える
def stones_count():
    global black_stone, white_stone
    black_stone = 0
    white_stone = 0
    for y in range(8):
        for x in range(8):
            if board[y][x] == BLACK:
                black_stone += 1
            if board[y][x] == WHITE:
                white_stone += 1
    return black_stone, white_stone

# 盤面を保存する
def save_board():
    back_board.clear
    for i in range(8):
        back_board.append([0] * 8)
    for y in range(8):
        for x in range(8):
            back_board[y][x] = board[y][x]
    return

# 盤面の状態を保存したものに戻す
def back():
    for y in range(8):
        for x in range(8):
            board[y][x] = back_board[y][x]
    return

# シミュレーションで打ち合う
def simulation_2(color):
    while True:
        if (put_able(WHITE) == False) and (put_able(BLACK) == False):   # どちらも石を置けない場合
            break
        color *= -1
        if put_able(color) == True:
            i = random.randint(0, len(put_able_list) - 1)
            x = put_able_list[i][0]
            y = put_able_list[i][1]
            put_stones(x, y, color)
    return

# 相手が石を置けるマスが少なくなるように手を選択
def AI_1():
    save_board()
    win = []
    for i in range(8):
        win.append([0] * 8)
    for y in range(8):
        for x in range(8):
            if reverse_stones_count(x, y, BLACK) > 0:   # 石が置ける場合
                game_board()   # 盤面を更新
                put_stones(x, y, BLACK)
                if put_able(WHITE) == True:
                    mass_numbers = len(put_able_list) 
                    win[y][x] = mass_numbers   # マスごとにその後のプレイヤーの石の置けるマスの数を記録する
                    back()
            else:
                win[y][x] = 100   # 置けないマスには大きい数を記録する
    min_number = 100
    for j in range(8):
        for i in range(8):
            if win[j][i] <= min_number:
                min_number = win[j][i]
                x = i
                y = j
    return x, y

# モンテカルロ法
def AI_2(loops):
    save_board()   # 現在の盤面を保存
    win = []
    for i in range(8):
        win.append([0] * 8)   # マスごとの勝った回数を記録
    for y in range(8):
        for x in range(8):
            if reverse_stones_count(x, y, BLACK) > 0:   # 石が置ける場合
                game_board()   # 盤面を更新
                for i in range(loops):
                    put_stones(x, y, BLACK)
                    simulation_2(BLACK)   # 勝敗が決まるまでランダムに石を打ち合う
                    black_stone, white_stone = stones_count()
                    if black_stone > white_stone:   # コンピュータ(黒)が勝利した場合
                        win[y][x] += 1   # 勝利数のカウント
                    back()   # 盤面をシミュレーション前の状態に戻す
    max_number = 0
    for j in range(8):
        for i in range(8):
            if win[j][i] >= max_number:
                max_number = win[j][i]
                x = i   # 勝利数が最大のマスの列
                y = j   # 勝利数が最大のマスの行
    return x, y

# ゲームの進行
def game_progress():
    global progress, turn, mx, my, mc, white_win, black_win, draw, game
    if progress == 0:   # ゲーム開始前
        progress = 1   # progを1にして次に進む、先に１にして配置可能なマスを表示
        turn = random.choice([-1, 1])
        start_board()
        game_board()
    elif progress == 1:  # ゲーム中
        if turn == 1:
            '''''
            if mc == 1:   #クリックされた場合
                if reverse_stones_count(mx, my, turn) > 0:   # 石を置ける場合
                    put_stones(mx, my, turn)
                    game_board()
                    progress = 2
        else:
            '''''
            while True:   # ランダム
                mx = random.randint(0, 7)
                my = random.randint(0, 7)
                if reverse_stones_count(mx, my, turn) > 0:   # 石を置ける場合
                    put_stones(mx, my, turn)
                    game_board()
                    progress = 2
                    break
        else:
            # cx, cy = AI_1()   # その後に相手が石を置けるマスの数を最小にする
            cx, cy = AI_2(10)   # モンテカルロ法
            put_stones(cx, cy, BLACK)
            progress = 2
        mc = 0   # クリックの処理を終了する
    elif progress == 2:   # 石を置いた後、次のプレイヤーがプレイを行えるかを調べる
        turn *= -1    # 次のターンにする
        if (put_able(BLACK) == False) and (put_able(WHITE) == False):   # どちらのプレイヤーも石を打てない場合
            EMPTY_count = 0
            for y in range(8):
                for x in range(8):
                    if board[y][x] == EMPTY:
                        EMPTY_count += 1
            '''''
            if EMPTY_count != 0:
                tkinter.messagebox.showinfo('', 'どちらのプレイヤーも打てないため終了です')
            '''''
            progress = 3
        elif put_able(turn) == False:   # 片方のプレイヤーが石を打てない場合
            '''''
            if turn == WHITE:
                tkinter.messagebox.showinfo('', 'あなた：パス')
            else:
                tkinter.messagebox.showinfo('', 'コンピュータ：パス')
            '''''
        else:   # どちらも石を打てる場合
            progress = 1
            game_board()   # 配置可能なマスを表示
    elif progress == 3:   # 勝敗の判定
        game_board()
        black_stone, white_stone = stones_count()
        # tkinter.messagebox.showinfo('', f'あなた：{white_stone}、コンピュータ：{black_stone}')
        if white_stone > black_stone:
            white_win += 1
            # tkinter.messagebox.showinfo('', 'あなたの勝利')
        elif white_stone < black_stone:
            black_win += 1
            # tkinter.messagebox.showinfo('', 'コンピュータの勝利')
        else:
            draw += 1
            # tkinter.messagebox.showinfo('', '引き分け')
        game += 1
        print(f'白：{white_win}  黒：{black_win}  引き分け：{draw}  総プレイ数：{game}  AIの勝率{black_win / game * 100}')
        progress = 0
    root.after(1, game_progress)   # 100ミリ秒後にgame_progress関数を呼び起こす
    return
    

# ウィンドウの作成
root = tkinter.Tk()    # ウィンドウのオブジェクトを準備
root.title('オセロ')   #ウィンドウのタイトルを指定
root.resizable(False, False)   # ウィンドウのサイズ変更の可不可を指定
root.bind('<Button>', click)   # マウスをクリックされたときにclick関数を呼び起こす

# キャンバスの作成
canvas = tkinter.Canvas(width = 640, height = 640, bg = 'green')   # キャンバスをウィンドウに配置
canvas.pack()   # キャンバスをウィンドウに配置

game_progress()

# ウィンドウの表示
root.mainloop()   # ウィンドウを表示する無限ループ