import random
import tkinter as tk
from tkinter import messagebox

class App(tk.Tk):
    def __init__(self):
        super(App, self).__init__()
        self.title("オセロゲーム")
        self.geometry("{}x{}+{}+{}".format(550, 550, 300, 100))
        self.resizable(0, 0)
        self.iconbitmap("Othello/img/othello.ico")
        self.configure(bg="white")
        self.turn = 1
        self.num_pass = 0
        self.candidates = {}
        self.flag = True
        self.tmp = []
        self.set_widgets()
        self.search_candidate()
        self.color_candidate()

    def set_widgets(self):
        # オセロ盤
        self.board = tk.Canvas(self, bg="lime green", width=350, height=350)
        self.board.pack(pady=(30, 0))
        # オセロ盤の設定
        self.board2info = [-1] * 10 + [[0, -1][i in [0, 9]] for i in range(10)] * 8 + [-1] * 10
        # tag
        self.numstr = '12345678'
        self.alpstr = "abcdefgh"
        # tagからクリックされたtagの位置を得る
        self.tag2pos = {}
        # 1次元の座標からtagを得る
        self.z2tag = {}
        # 長方形を配置する
        for i, y in zip(self.numstr, range(15, 336, 40)):
            for j, x in zip(self.alpstr, range(15, 336, 40)):
                pos = x, y, x+40, y+40
                tag = i + j
                self.tag2pos[tag] = pos
                self.board.create_rectangle(*pos, fill="lime green", tags=tag)
                self.z2tag[self.z_coordinate(tag)] = tag
                self.board.tag_bind(tag, "<ButtonPress-1>", self.pressed)
        # 初期設定
        for p, i in zip([1, 2], "45"):
            for q, j in zip([2, 1], "de"):
                color = ["black", "white"][p-q]
                tag = i + j
                self.board2info[self.z_coordinate(tag)] = [1, 2][p-q]
                self.board.create_oval(*self.tag2pos[tag], fill=color, tags=tag)
        self.get_board_info()

        # Label
        self.turn = 1
        self.info = tk.Canvas(self, bg="white", width=300, height=100)
        self.info.pack(pady=(30,0))
        self.var = tk.StringVar()
        self.update_label()
        self.label = tk.Label(self.info, bg="white", font=("Helvetica", 15), textvariable=self.var)
        self.label.pack()

    def get_board_info(self):
        board_format = " {:2d} " * 10
        print("", *[board_format.format(*self.board2info[i:i+10]) \
            for i in range(0, 100, 10)], sep='\n')

    def z_coordinate(self, tag):
        x = self.alpstr.index(tag[1])+1
        y = self.numstr.index(tag[0])+1
        return y*10 + x

    def update_label(self):
        self.var.set("{}のターン".format(["CPU", "あなた"][self.turn]))

    def pressed(self, event):
        id = self.board.find_closest(event.x, event.y)
        tag = self.board.gettags(id[0])[0]
        # print("Tag {} pressed".format(tag))
        # 符号から1次元の座標に変換
        z = self.z_coordinate(tag)
        if self.board2info[z] !=0: # 空白でなければ
            return
        if tag not in self.candidates: # クリックされたところが、置けない場合
            return
        # 候補手の色を元に戻す
        self.back_candidate()
        # 盤の更新
        self.update_board(tag)
        # 手番の変更
        self.turn = 0
        # ラベルの更新
        self.update_label()
        self.get_board_info()
        ##### Computer #####
        self.search_candidate()

    def search_candidate(self):
        self.candidates = {}
        for y in self.numstr:
            for x in self.alpstr:
                tag = y + x
                if self.board2info[self.z_coordinate(tag)] != 0:
                    continue
                self._search(tag)
        res = self.color_candidate()
        if self.num_pass == 2:
            print("Finish")
            I = sum(1 for v in self.board2info if v == 2)
            CPU = sum(1 for v in self.board2info if v == 1)
            messagebox.showinfo("Result", "あなた: {}\nCPU: {}".format(I, CPU))
            return

        if res == -1:
            print("Pass")
            self.turn = self.turn ^ 1
            self.upfate_label()
            self.search_candidate()

        if self.turn:
            return
        self.after(1000, self.next_turn)

    def next_turn(self):
        self.back_candidate()
        try:
            tag = random.choice(list(self.candidates.keys()))
        except:
            return
        self.update_board(tag)
        self.turn = self.turn ^ 1
        self.update_label()
        self.get_board_info()
        self.search_candidate()

    def _search(self, tag):
        z = self.z_coordinate(tag)
        for num in [-10, 10, 1, -1, -11, 11, -9, 9]:
            self.flag = False
            self.tmp = []
            res = self._run_search(z+num, num)
            if res == -1:
                continue
            if tag in self.candidates:
                self.candidates[tag] += self.tmp
            else:
                self.candidates[tag] = self.tmp

    def _run_search(self, z, num):
        v = self.board2info[z]
        if v in [-1, 0]:
            return -1
        if v == (self.turn+1):
            return z if self.flag else -1
        self.flag = True
        self.tmp.append(z)
        return self ._run_search(z+num, num)

    def color_candidate(self):
        if len(self.candidates) == 0:
            self.num_pass += 1
            return -1
        for tag in self.candidates.keys():
            self.board.itemconfig(tag, fill="lawn green")
        self.num_pass = 0
        return 1

    def back_candidate(self):
        if len(self.candidates) == 0:
            return -1
        for tag in self.candidates.keys():
            self.board.itemconfig(tag, fill="lime green")

    def update_board(self, tag):
        for z in self.candidates[tag]:
            ctag = self.z2tag[z]
            self.board.create_oval(*self.tag2pos[ctag], fill=["black", "white"][self.turn])
            self.board2info[z] = [1, 2][self.turn]
        self.board.create_oval(*self.tag2pos[tag], fill=["black", "white"][self.turn])
        self.board2info[self.z_coordinate(tag)] = [1, 2][self.turn]

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()