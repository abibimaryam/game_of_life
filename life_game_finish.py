import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import copy


# Создание шаблона соседей
def create_neighbor_pattern():
    size = 5
    pattern = [[0 for _ in range(size)] for _ in range(size)]
    center = (size // 2, size // 2)

    window = tk.Toplevel()
    window.title("Создание шаблона соседей")
    cell_size = 40
    canvas = tk.Canvas(window, width=size * cell_size, height=size * cell_size)
    canvas.pack()

    def draw():
        canvas.delete("all")
        for i in range(size):
            for j in range(size):
                color = "black" if pattern[i][j] == 1 else "white"
                if (i, j) == center:
                    color = "red"
                canvas.create_rectangle(
                    j * cell_size, i * cell_size,
                    (j + 1) * cell_size, (i + 1) * cell_size,
                    fill=color, outline="gray"
                )

    def toggle(event):
        i = event.y // cell_size
        j = event.x // cell_size
        if (i, j) != center:
            pattern[i][j] = 1 - pattern[i][j]
        draw()

    def finish():
        window.destroy()

    canvas.bind("<Button-1>", toggle)
    tk.Button(window, text="Готово", command=finish).pack(pady=5)
    draw()
    window.wait_window()

    neighbors = []
    for i in range(size):
        for j in range(size):
            if pattern[i][j] == 1:
                neighbors.append((i - center[0], j - center[1]))
    return neighbors


#  Подсчёт соседей
def count_neighbors(grid, x, y, neighbors):
    n = len(grid)
    count = 0
    for dx, dy in neighbors:
        nx, ny = (x + dx) % n, (y + dy) % n
        if grid[nx][ny] == 1:
            count += 1
    return count


#  Следующее поколение 
def next_generation(grid, neighbors, birth_rules, survive_rules):
    n = len(grid)
    new_grid = copy.deepcopy(grid)
    for i in range(n):
        for j in range(n):
            c = count_neighbors(grid, i, j, neighbors)
            if grid[i][j] == 1:
                new_grid[i][j] = 1 if c in survive_rules else 0
            else:
                new_grid[i][j] = 1 if c in birth_rules else 0
    return new_grid


#  Приложение 
class LifeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Игра жизнь")

        self.n = 10
        self.cell_size = 20
        self.grid = [[0] * self.n for _ in range(self.n)]

        # стандартные настройки
        self.mode = 1
        self.neigh_label = "8 соседей"
        self.neighbors = [(dx, dy) for dx in (-1, 0, 1)
                          for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
        self.birth_rules = [3]
        self.survive_rules = [2, 3]

        self.running = False
        self.after_id = None
        self.generation = 0

        self.create_ui()
        self.draw_grid()

    # Интерфейс 
    def create_ui(self):
        top = tk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, pady=5)

        tk.Label(top, text="Размер:").pack(side=tk.LEFT, padx=5)
        self.size_spin = tk.Spinbox(top, from_=5, to=100, width=5)
        self.size_spin.delete(0, tk.END)
        self.size_spin.insert(0, str(self.n))
        self.size_spin.pack(side=tk.LEFT)

        tk.Label(top, text="Поколений:").pack(side=tk.LEFT, padx=5)
        self.gen_spin = tk.Spinbox(top, from_=1, to=10000, width=7)
        self.gen_spin.delete(0, tk.END)
        self.gen_spin.insert(0, "10")
        self.gen_spin.pack(side=tk.LEFT)

        tk.Button(top, text="Применить", command=self.apply_size).pack(side=tk.LEFT, padx=5)

        self.mode_btn = tk.Button(top, text="Выбрать режим", command=self.choose_mode)
        self.mode_btn.pack(side=tk.LEFT, padx=10)

        tk.Button(top, text="Очистить", command=self.clear).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="▶", width=3, command=self.start).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="⏸", width=3, command=self.pause).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Шаг", command=self.step).pack(side=tk.LEFT, padx=5)

        self.info_label = tk.Label(self.root, text="Поколение: 0", anchor="w")
        self.info_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(self.root, bg="white", width=self.n * self.cell_size, height=self.n * self.cell_size)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.toggle_cell)

    # Выбор режима
    def choose_mode(self):
        mode = simpledialog.askinteger(
            "Режим",
            "Выберите режим:\n"
            "1) Стандартные правила  8 соседей\n"
            "2) Стандартные правила крест (4 соседа)\n"
            "3) Свои правила + свой шаблон соседей"
        )

        if mode == 1:
            # 8 соседей (Мура)
            self.neighbors = [(dx, dy) for dx in (-1, 0, 1)
                              for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
            self.birth_rules = [3]
            self.survive_rules = [2, 3]
            self.mode = 1
            self.neigh_label = "8 соседей"

        elif mode == 2:
            # крест: 4 соседа (фон Неймана)
            self.neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.birth_rules = [3]
            self.survive_rules = [2, 3]
            self.mode = 2
            self.neigh_label = "крест (4 соседа)"

        elif mode == 3:
            # свой шаблон и правила
            self.neighbors = create_neighbor_pattern()
            br = simpledialog.askstring("Правила", "Введите числа соседей для оживления (через пробел):")
            sr = simpledialog.askstring("Правила", "Введите числа соседей для выживания (через пробел):")
            try:
                self.birth_rules = list(map(int, br.split())) if br else []
                self.survive_rules = list(map(int, sr.split())) if sr else []
            except Exception:
                messagebox.showerror("Ошибка", "Неверный формат правил.")
                return
            self.mode = 3
            self.neigh_label = "пользовательский шаблон"

        else:
            messagebox.showerror("Ошибка", "Неверный режим")
            return

        self.generation = 0
        self.draw_grid()

    #  Игровая логика 
    def apply_size(self):
        val = int(self.size_spin.get())
        self.n = val
        self.grid = [[0] * self.n for _ in range(self.n)]
        self.canvas.config(width=self.n * self.cell_size, height=self.n * self.cell_size)
        self.draw_grid()

    def clear(self):
        self.grid = [[0] * self.n for _ in range(self.n)]
        self.generation = 0
        self.draw_grid()

    def toggle_cell(self, event):
        i = event.y // self.cell_size
        j = event.x // self.cell_size
        if 0 <= i < self.n and 0 <= j < self.n:
            self.grid[i][j] = 1 - self.grid[i][j]
            self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for i in range(self.n):
            for j in range(self.n):
                color = "black" if self.grid[i][j] else "white"
                self.canvas.create_rectangle(
                    j * self.cell_size, i * self.cell_size,
                    (j + 1) * self.cell_size, (i + 1) * self.cell_size,
                    fill=color, outline="#ddd"
                )
        self.info_label.config(
            text=f"Поколение: {self.generation} | Режим: {self.mode} | Шаблон: {self.neigh_label} | Правила B{''.join(map(str,self.birth_rules))}/S{''.join(map(str,self.survive_rules))}"
        )

    def step(self):
        max_gen = int(self.gen_spin.get())
        if self.generation >= max_gen:
            messagebox.showinfo("Конец", "Достигнуто максимальное количество поколений!")
            self.pause()
            self.clear()
            return
        self.grid = next_generation(self.grid, self.neighbors, self.birth_rules, self.survive_rules)
        self.generation += 1
        self.draw_grid()

    def start(self):
        if not self.running:
            self.running = True
            self.run_loop()

    def pause(self):
        self.running = False
        if self.after_id:
            self.canvas.after_cancel(self.after_id)
            self.after_id = None

    def run_loop(self):
        if not self.running:
            return
        self.step()
        self.after_id = self.canvas.after(1000, self.run_loop)  # задержка 1 сек


if __name__ == "__main__":
    root = tk.Tk()
    app = LifeApp(root)
    root.geometry("700x500")
    root.mainloop()
