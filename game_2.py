import tkinter as tk
from tkinter import ttk
import random

class Life:
    def __init__(self, n=30, wrap=True):
        self.n = n
        self.wrap = wrap
        self.grid = [[0]*n for _ in range(n)]
        self.generation = 0

    def clear(self):
        self.grid = [[0]*self.n for _ in range(self.n)]
        self.generation = 0

    def randomize(self, p=0.2):
        self.grid = [[1 if random.random() < p else 0 for _ in range(self.n)] for _ in range(self.n)]
        self.generation = 0

    def count_neighbors(self, x, y):
        n = self.n
        cnt = 0
        # Только 4 соседа: вверх, вниз, влево, вправо
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.wrap:
                nx %= n
                ny %= n
                cnt += self.grid[ny][nx]
            elif 0 <= nx < n and 0 <= ny < n:
                cnt += self.grid[ny][nx]
        return cnt


    def step(self):
        n=self.n
        new=[[0]*n for _ in range(n)]
        for y in range(n):
            for x in range(n):
                nb=self.count_neighbors(x,y)
                if self.grid[y][x]==1 and nb in (2,3): new[y][x]=1
                elif self.grid[y][x]==0 and nb==3: new[y][x]=1
        changed=(new!=self.grid)
        self.grid=new
        if changed: self.generation+=1
        return changed

class LifeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Игра жизнь")
        self.geometry("800x700")
        self.life=Life(25)
        self.running=False
        self.cell_size=25
        self.speed=150
        self.target_gens=0
        self._build_ui()
        self._bind()
        self._draw_all()

    def _build_ui(self):
        control=ttk.Frame(self,padding=5)
        control.pack(fill="x")

        ttk.Label(control,text="Размер n:").pack(side="left")
        self.n_var=tk.IntVar(value=self.life.n)
        ttk.Spinbox(control,from_=5,to=200,textvariable=self.n_var,width=5).pack(side="left",padx=5)
        ttk.Button(control,text="Применить",command=self._resize).pack(side="left",padx=5)

        ttk.Label(control,text="Поколений:").pack(side="left")
        self.gen_var=tk.IntVar(value=0)
        ttk.Spinbox(control,from_=0,to=1000,textvariable=self.gen_var,width=6).pack(side="left",padx=5)

        ttk.Button(control,text="Случайно",command=self._random).pack(side="left",padx=5)
        ttk.Button(control,text="Очистить",command=self._clear).pack(side="left",padx=5)
        ttk.Button(control,text="▶",command=self._start).pack(side="left",padx=5)
        ttk.Button(control,text="⏸",command=self._pause).pack(side="left",padx=5)
        ttk.Button(control,text="Шаг",command=self._step_once).pack(side="left",padx=5)


        self.canvas=tk.Canvas(self,bg="white",highlightthickness=1,highlightbackground="gray")
        self.canvas.pack(expand=True,fill="both",padx=10,pady=10)

        self.status=ttk.Label(self,text="",anchor="w")
        self.status.pack(fill="x")
        self.colormap=("white","#111")

    def _bind(self):
        self.canvas.bind("<Button-1>",self._click_on)
        self.canvas.bind("<Button-3>",self._click_off)
        self.canvas.bind("<B1-Motion>",self._click_on)
        self.canvas.bind("<B3-Motion>",self._click_off)
        self.canvas.bind("<Double-Button-1>", self._dbl_left_clear)  # NEW: двойной клик ЛКМ

    # управление
    def _resize(self):
        n=self.n_var.get()
        self.life=Life(n)
        self._draw_all()

    def _random(self):
        self.life.randomize(0.25)
        self._draw_all()

    def _clear(self):
        self.running=False
        self.life.clear()
        self._draw_all()

    def _start(self):
        self.running=True
        self.target_gens=self.gen_var.get()
        self._loop()

    def _pause(self):
        self.running=False

    def _step_once(self):
        self.life.step()
        self._draw_all()

    # отрисовка / ввод
    def _click_on(self,ev):
        c=self._coords_to_cell(ev.x,ev.y)
        if c:
            x,y=c
            self.life.grid[y][x]=1
            self._draw_cell(x,y)

    def _click_off(self,ev):
        c=self._coords_to_cell(ev.x,ev.y)
        if c:
            x,y=c
            self.life.grid[y][x]=0
            self._draw_cell(x,y)

    def _dbl_left_clear(self, ev):  # обработчик двойного клика 
        c = self._coords_to_cell(ev.x, ev.y)
        if c:
            x, y = c
            self.life.grid[y][x] = 0   # делаем белой (мертвой)
            self._draw_cell(x, y)
 

    def _coords_to_cell(self,x,y):
        s=self.cell_size
        cx=x//s; cy=y//s
        if 0<=cx<self.life.n and 0<=cy<self.life.n: return cx,cy
        return None

    def _draw_all(self):
        self.canvas.delete("all")
        n=self.life.n; s=self.cell_size
        for y in range(n):
            for x in range(n):
                self._draw_cell(x,y)
        for i in range(n+1):
            self.canvas.create_line(0,i*s,n*s,i*s,fill="#ddd")
            self.canvas.create_line(i*s,0,i*s,n*s,fill="#ddd")
        self._update_status()

    def _draw_cell(self,x,y):
        s=self.cell_size
        c=self.colormap[self.life.grid[y][x]]
        self.canvas.create_rectangle(x*s,y*s,(x+1)*s,(y+1)*s,fill=c,outline=c)

    def _update_status(self):
        self.status.config(text=f"Размер {self.life.n}×{self.life.n} | Поколение: {self.life.generation}")

    def _loop(self):
        if not self.running: return
        if self.target_gens>0 and self.life.generation>=self.target_gens:
            self.running=False
            return
        self.life.step()
        self._draw_all()
        self.after(self.speed,self._loop)

if __name__=="__main__":
    LifeGUI().mainloop()
