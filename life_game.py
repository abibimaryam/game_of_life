import tkinter as tk
from tkinter import simpledialog, messagebox
import time
import copy

# === Подсчет соседей ===
def count_neighbors(grid, x, y, neighbors):
    n = len(grid)
    count = 0
    for dx, dy in neighbors:
        nx, ny = (x + dx) % n, (y + dy) % n
        if grid[nx][ny] == 1:
            count += 1
    return count

# === Следующее поколение ===
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

# === Отрисовка поля ===
def draw_grid(canvas, grid, cell_size):
    canvas.delete("all")
    n = len(grid)
    for i in range(n):
        for j in range(n):
            color = "black" if grid[i][j] == 1 else "white"
            canvas.create_rectangle(
                j * cell_size, i * cell_size,
                (j + 1) * cell_size, (i + 1) * cell_size,
                fill=color, outline="gray"
            )
    canvas.update()

# === Окно для создания шаблона соседей ===
def create_neighbor_pattern():
    size = 5  # шаблон 5x5
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
                    color = "red"  # центр клетки
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
    tk.Button(window, text="Готово", command=finish).pack()
    draw()
    window.wait_window()

    neighbors = []
    for i in range(size):
        for j in range(size):
            if pattern[i][j] == 1:
                neighbors.append((i - center[0], j - center[1]))
    return neighbors

# === Основная программа ===
def game_of_life():
    root = tk.Tk()
    root.withdraw()

    n = simpledialog.askinteger("Размер", "Введите размер поля n x n:")
    mode = simpledialog.askinteger("Режим", "Выберите режим:\n1) Стандартные правила\n2) Свой шаблон соседей\n3) Свои правила и шаблон соседей")

    # === Настройка правил и соседей ===
    if mode == 1:
        neighbors = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if not (i == 0 and j == 0)]
        birth_rules = [3]
        survive_rules = [2, 3]
    elif mode == 2:
        messagebox.showinfo("Шаблон", "Нарисуйте шаблон соседей (центр — красный квадрат).")
        neighbors = create_neighbor_pattern()
        birth_rules = [3]
        survive_rules = [2, 3]
    elif mode == 3:
        messagebox.showinfo("Шаблон", "Нарисуйте шаблон соседей (центр — красный квадрат).")
        neighbors = create_neighbor_pattern()
        birth_rules = list(map(int, simpledialog.askstring("Правила", "Введите числа соседей для оживления (через пробел):").split()))
        survive_rules = list(map(int, simpledialog.askstring("Правила", "Введите числа соседей для выживания (через пробел):").split()))
    else:
        messagebox.showerror("Ошибка", "Неверный режим")
        return

    # === Создание поля ===
    grid = [[0 for _ in range(n)] for _ in range(n)]

    # === Окно для установки живых клеток ===
    config = tk.Toplevel()
    config.title("Начальное поле")
    cell_size = 20
    canvas = tk.Canvas(config, width=n * cell_size, height=n * cell_size)
    canvas.pack()

    def draw_setup():
        canvas.delete("all")
        for i in range(n):
            for j in range(n):
                color = "black" if grid[i][j] == 1 else "white"
                canvas.create_rectangle(
                    j * cell_size, i * cell_size,
                    (j + 1) * cell_size, (i + 1) * cell_size,
                    fill=color, outline="gray"
                )
        canvas.update()

    def toggle_cell(event):
        i = event.y // cell_size
        j = event.x // cell_size
        grid[i][j] = 1 - grid[i][j]
        draw_setup()

    def start_game():
        config.destroy()

    canvas.bind("<Button-1>", toggle_cell)
    tk.Button(config, text="Запуск", command=start_game).pack()
    draw_setup()
    config.wait_window()

    # === Выбор количества поколений ===
    gen_input = simpledialog.askstring("Поколения", "Введите количество поколений или 'inf' для бесконечного:")
    infinite = (gen_input == 'inf')
    generations = int(gen_input) if not infinite else None

    # === Главное окно игры ===
    main = tk.Toplevel()
    main.title("Игра жизнь")
    canvas_game = tk.Canvas(main, width=n * cell_size, height=n * cell_size)
    canvas_game.pack()

    stop_flag = tk.BooleanVar(value=False)

    def stop_game():
        stop_flag.set(True)

    tk.Button(main, text="Остановить", command=stop_game, bg="red", fg="white").pack(pady=5)


    draw_grid(canvas_game, grid, cell_size)
    gen = 0

    # === Цикл игры ===
    while (infinite or gen < generations) and not stop_flag.get():
        draw_grid(canvas_game, grid, cell_size)
        main.update()
        time.sleep(0.5)
        grid = next_generation(grid, neighbors, birth_rules, survive_rules)
        gen += 1

    messagebox.showinfo("Стоп", f"Симуляция завершена после {gen} поколений.")
    main.destroy()


if __name__ == "__main__":
    game_of_life()
