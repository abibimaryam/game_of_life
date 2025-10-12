import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import threading

class GameOfLife:
    def __init__(self, master):
        self.master = master
        self.master.title("Игра Жизнь")
        self.running = False
        self.delay = 3  # задержка между поколениями (сек)
        self.generation = 0

        # Запрос размера поля
        self.n = simpledialog.askinteger("Размер поля", "Введите размер поля (n x n):", minvalue=3, maxvalue=50)
        if not self.n:
            master.destroy()
            return

        # Выбор режима
        self.mode = simpledialog.askinteger(
            "Режим правил",
            "Выберите режим:\n"
            "1 — стандартные правила\n"
            "2 — новый шаблон соседей\n"
            "3 — новые правила и шаблон",
            minvalue=1, maxvalue=3
        )
        if not self.mode:
            master.destroy()
            return

        # Инициализация шаблона соседей
        self.neighbor_mask = self.get_neighbor_mask()

        # Настройка правил
        if self.mode == 3:
            self.birth_rule = simpledialog.askstring(
                "Правило рождения",
                "Введите количество живых соседей для возрождения клетки (через запятую, напр. 3):"
            )
            self.survive_rule = simpledialog.askstring(
                "Правило выживания",
                "Введите количество живых соседей для выживания клетки (через запятую, напр. 2,3):"
            )
            self.birth_rule = [int(x) for x in self.birth_rule.split(',')]
            self.survive_rule = [int(x) for x in self.survive_rule.split(',')]
        else:
            self.birth_rule = [3]
            self.survive_rule = [2, 3]

        # Поле клеток
        self.grid = [[0 for _ in range(self.n)] for _ in range(self.n)]
        self.buttons = []

        frame = tk.Frame(master)
        frame.pack()

        for i in range(self.n):
            row = []
            for j in range(self.n):
                b = tk.Button(frame, width=2, height=1, bg="white",
                              command=lambda i=i, j=j: self.toggle_cell(i, j))
                b.grid(row=i, column=j)
                row.append(b)
            self.buttons.append(row)

        # Панель управления
        control_frame = tk.Frame(master)
        control_frame.pack(pady=10)

        self.start_btn = tk.Button(control_frame, text="Старт", command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(control_frame, text="Остановить", command=self.stop)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.step_btn = tk.Button(control_frame, text="Пошагово", command=self.step_once)
        self.step_btn.pack(side=tk.LEFT, padx=5)

        self.gen_label = tk.Label(control_frame, text="Поколение: 0")
        self.gen_label.pack(side=tk.LEFT, padx=15)

        # Запрос количества поколений
        self.num_generations = simpledialog.askinteger("Поколения", "Введите количество поколений (0 — бесконечно):", minvalue=0)
        if self.num_generations is None:
            master.destroy()
            return

    def get_neighbor_mask(self):
        """Позволяет пользователю задать шаблон соседей"""
        if self.mode == 1:
            mask = [[1,1,1],[1,0,1],[1,1,1]]
        else:
            size = simpledialog.askinteger("Шаблон", "Введите размер шаблона (нечётное число, напр. 3, 5, 7):", minvalue=3, maxvalue=7)
            if not size:
                size = 3
            mask = [[0]*size for _ in range(size)]

            top = tk.Toplevel()
            top.title("Введите шаблон соседей (X — сосед, 0 — клетка)")
            tk.Label(top, text="Кликните на ячейки, чтобы отметить соседей (0 — центр)").pack()

            buttons = []
            for i in range(size):
                row = []
                for j in range(size):
                    b = tk.Button(top, width=2, height=1, bg="white")
                    b.grid(row=i, column=j)
                    row.append(b)
                buttons.append(row)

            center = size // 2
            buttons[center][center].configure(text='0', bg='lightgrey', state='disabled')

            def toggle(i, j):
                if buttons[i][j]['bg'] == 'white':
                    buttons[i][j]['bg'] = 'black'
                    mask[i][j] = 1
                else:
                    buttons[i][j]['bg'] = 'white'
                    mask[i][j] = 0
            for i in range(size):
                for j in range(size):
                    if not (i == center and j == center):
                        buttons[i][j].configure(command=lambda i=i, j=j: toggle(i, j))

            def confirm():
                top.destroy()

            tk.Button(top, text="Готово", command=confirm).pack(pady=5)
            top.wait_window()
        return mask

    def toggle_cell(self, i, j):
        self.grid[i][j] = 1 - self.grid[i][j]
        self.buttons[i][j].configure(bg="black" if self.grid[i][j] else "white")

    def count_neighbors(self, x, y):
        count = 0
        size = len(self.neighbor_mask)
        offset = size // 2
        for i in range(size):
            for j in range(size):
                if self.neighbor_mask[i][j] == 1:
                    ni, nj = x + i - offset, y + j - offset
                    if 0 <= ni < self.n and 0 <= nj < self.n:
                        count += self.grid[ni][nj]
        return count

    def next_generation(self):
        new_grid = [[0 for _ in range(self.n)] for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                neighbors = self.count_neighbors(i, j)
                if self.grid[i][j] == 1:
                    if neighbors in self.survive_rule:
                        new_grid[i][j] = 1
                else:
                    if neighbors in self.birth_rule:
                        new_grid[i][j] = 1
        self.grid = new_grid
        self.update_display()

    def update_display(self):
        for i in range(self.n):
            for j in range(self.n):
                self.buttons[i][j].configure(bg="black" if self.grid[i][j] else "white")
        self.gen_label.configure(text=f"Поколение: {self.generation}")

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.run).start()

    def stop(self):
        self.running = False

    def step_once(self):
        if not self.running:
            self.generation += 1
            self.next_generation()

    def run(self):
        self.generation = 0
        while self.running and (self.num_generations == 0 or self.generation < self.num_generations):
            self.generation += 1
            self.next_generation()
            time.sleep(self.delay)
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfLife(root)
    root.mainloop()
