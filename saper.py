import tkinter as tk
from tkinter import messagebox, font
import random
from typing import List, Tuple, Set

class MinesweeperGame:
    """Полноценная игра Сапёр с современным интерфейсом"""
    
    # Цветовая схема
    COLORS = {
        'bg': '#1a1a2e',
        'cell_closed': '#16213e',
        'cell_open': '#0f3460',
        'cell_hover': '#1f4068',
        'mine': '#e94560',
        'flag': '#f39c12',
        'text': '#eaeaea',
        'numbers': {
            1: '#3498db',
            2: '#2ecc71',
            3: '#e74c3c',
            4: '#9b59b6',
            5: '#e67e22',
            6: '#1abc9c',
            7: '#34495e',
            8: '#c0392b'
        }
    }
    
    DIFFICULTIES = {
        'Новичок': (9, 9, 10),
        'Любитель': (16, 16, 40),
        'Профи': (16, 30, 99)
    }
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("💣 Сапёр Pro")
        self.root.configure(bg=self.COLORS['bg'])
        
        # Параметры игры
        self.rows = 9
        self.cols = 9
        self.mines_count = 10
        self.difficulty = 'Новичок'
        
        # Игровое состояние
        self.game_started = False
        self.game_over = False
        self.mines_positions: Set[Tuple[int, int]] = set()
        self.revealed: Set[Tuple[int, int]] = set()
        self.flagged: Set[Tuple[int, int]] = set()
        self.buttons: List[List[tk.Button]] = []
        
        # Таймер
        self.time_elapsed = 0
        self.timer_running = False
        
        self.create_ui()
        self.new_game()
    
    def create_ui(self):
        """Создание интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        header_frame.pack(pady=10, padx=10)
        
        title_font = font.Font(family='Arial', size=20, weight='bold')
        title = tk.Label(header_frame, text="💣 САПЁР", font=title_font,
                        bg=self.COLORS['bg'], fg=self.COLORS['text'])
        title.pack()
        
        # Панель управления
        control_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        control_frame.pack(pady=10, padx=10)
        
        # Информационная панель
        info_frame = tk.Frame(control_frame, bg=self.COLORS['cell_closed'], relief=tk.RAISED, bd=2)
        info_frame.pack(side=tk.LEFT, padx=5)
        
        # Мины
        mines_frame = tk.Frame(info_frame, bg=self.COLORS['cell_closed'])
        mines_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(mines_frame, text="💣", font=('Arial', 14),
                bg=self.COLORS['cell_closed'], fg=self.COLORS['mine']).pack()
        self.mines_label = tk.Label(mines_frame, text="10", font=('Arial', 12, 'bold'),
                                    bg=self.COLORS['cell_closed'], fg=self.COLORS['text'])
        self.mines_label.pack()
        
        # Таймер
        timer_frame = tk.Frame(info_frame, bg=self.COLORS['cell_closed'])
        timer_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(timer_frame, text="⏱️", font=('Arial', 14),
                bg=self.COLORS['cell_closed'], fg=self.COLORS['flag']).pack()
        self.timer_label = tk.Label(timer_frame, text="000", font=('Arial', 12, 'bold'),
                                    bg=self.COLORS['cell_closed'], fg=self.COLORS['text'])
        self.timer_label.pack()
        
        # Кнопки управления
        buttons_frame = tk.Frame(control_frame, bg=self.COLORS['bg'])
        buttons_frame.pack(side=tk.LEFT, padx=5)
        
        new_game_btn = tk.Button(buttons_frame, text="🎮 Новая игра", font=('Arial', 10, 'bold'),
                                 bg=self.COLORS['cell_closed'], fg=self.COLORS['text'],
                                 activebackground=self.COLORS['cell_hover'],
                                 activeforeground=self.COLORS['text'],
                                 relief=tk.RAISED, bd=3, padx=10, pady=5,
                                 command=self.new_game, cursor='hand2')
        new_game_btn.pack(pady=2)
        
        # Выбор сложности
        difficulty_frame = tk.Frame(control_frame, bg=self.COLORS['bg'])
        difficulty_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(difficulty_frame, text="Сложность:", font=('Arial', 9),
                bg=self.COLORS['bg'], fg=self.COLORS['text']).pack()
        
        for diff in self.DIFFICULTIES.keys():
            btn = tk.Button(difficulty_frame, text=diff, font=('Arial', 8),
                          bg=self.COLORS['cell_closed'], fg=self.COLORS['text'],
                          activebackground=self.COLORS['cell_hover'],
                          activeforeground=self.COLORS['text'],
                          relief=tk.RAISED, bd=2, padx=5, pady=2,
                          command=lambda d=diff: self.change_difficulty(d),
                          cursor='hand2')
            btn.pack(side=tk.LEFT, padx=2)
        
        # Игровое поле (контейнер)
        self.game_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.game_frame.pack(pady=10, padx=10)
        
        # Инструкции
        instructions = tk.Label(self.root,
                               text="ЛКМ - открыть • ПКМ - флаг • Средняя кнопка - открыть соседей",
                               font=('Arial', 8), bg=self.COLORS['bg'],
                               fg=self.COLORS['text'], pady=5)
        instructions.pack()
    
    def create_game_board(self):
        """Создание игрового поля"""
        # Очистка старого поля
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        
        self.buttons = []
        
        # Создание сетки кнопок
        for row in range(self.rows):
            button_row = []
            for col in range(self.cols):
                btn = tk.Button(self.game_frame, text="", width=3, height=1,
                              font=('Arial', 10, 'bold'),
                              bg=self.COLORS['cell_closed'],
                              fg=self.COLORS['text'],
                              activebackground=self.COLORS['cell_hover'],
                              relief=tk.RAISED, bd=3,
                              cursor='hand2')
                
                btn.grid(row=row, column=col, padx=1, pady=1)
                
                # Привязка событий
                btn.bind('<Button-1>', lambda e, r=row, c=col: self.on_left_click(r, c))
                btn.bind('<Button-3>', lambda e, r=row, c=col: self.on_right_click(r, c))
                btn.bind('<Button-2>', lambda e, r=row, c=col: self.on_middle_click(r, c))
                
                # Эффект наведения
                btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.COLORS['cell_hover']))
                btn.bind('<Leave>', lambda e, b=btn, r=row, c=col: 
                        b.configure(bg=self.COLORS['cell_closed']) if (r, c) not in self.revealed else None)
                
                button_row.append(btn)
            self.buttons.append(button_row)
    
    def new_game(self):
        """Начать новую игру"""
        self.game_started = False
        self.game_over = False
        self.mines_positions.clear()
        self.revealed.clear()
        self.flagged.clear()
        self.time_elapsed = 0
        self.timer_running = False
        
        self.create_game_board()
        self.update_mines_counter()
        self.update_timer()
    
    def change_difficulty(self, difficulty: str):
        """Изменить сложность"""
        self.difficulty = difficulty
        self.rows, self.cols, self.mines_count = self.DIFFICULTIES[difficulty]
        self.new_game()
    
    def place_mines(self, first_row: int, first_col: int):
        """Размещение мин (избегая первый клик и его соседей - создаём безопасную зону)"""
        # Безопасная зона: клетка первого клика + все соседи
        safe_zone = {(first_row, first_col)}
        safe_zone.update(self.get_neighbors(first_row, first_col))
        
        # Доступные позиции для мин (исключая безопасную зону)
        available_positions = [(r, c) for r in range(self.rows) 
                              for c in range(self.cols)
                              if (r, c) not in safe_zone]
        
        # Размещаем мины только вне безопасной зоны
        self.mines_positions = set(random.sample(available_positions, 
                                                 min(self.mines_count, len(available_positions))))
        self.game_started = True
        self.start_timer()
    
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Получить соседние клетки"""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbors.append((nr, nc))
        return neighbors
    
    def count_adjacent_mines(self, row: int, col: int) -> int:
        """Подсчёт мин вокруг клетки"""
        count = 0
        for nr, nc in self.get_neighbors(row, col):
            if (nr, nc) in self.mines_positions:
                count += 1
        return count
    
    def reveal_cell(self, row: int, col: int):
        """Открыть клетку"""
        if (row, col) in self.revealed or (row, col) in self.flagged:
            return
        
        self.revealed.add((row, col))
        btn = self.buttons[row][col]
        
        if (row, col) in self.mines_positions:
            # Попали на мину
            btn.config(text="💣", bg=self.COLORS['mine'], relief=tk.SUNKEN)
            self.game_over_lose()
            return
        
        # Подсчёт соседних мин
        mines_nearby = self.count_adjacent_mines(row, col)
        btn.config(bg=self.COLORS['cell_open'], relief=tk.SUNKEN)
        
        if mines_nearby > 0:
            btn.config(text=str(mines_nearby), 
                      fg=self.COLORS['numbers'].get(mines_nearby, self.COLORS['text']))
        else:
            # Если мин нет - открываем соседей
            btn.config(text="")
            for nr, nc in self.get_neighbors(row, col):
                if (nr, nc) not in self.revealed:
                    self.reveal_cell(nr, nc)
        
        # Проверка победы
        self.check_win()
    
    def on_left_click(self, row: int, col: int):
        """Обработка левого клика"""
        if self.game_over:
            return
        
        if not self.game_started:
            self.place_mines(row, col)
        
        if (row, col) not in self.flagged:
            self.reveal_cell(row, col)
    
    def on_right_click(self, row: int, col: int):
        """Обработка правого клика (установка флага)"""
        if self.game_over or (row, col) in self.revealed:
            return
        
        btn = self.buttons[row][col]
        
        if (row, col) in self.flagged:
            self.flagged.remove((row, col))
            btn.config(text="", bg=self.COLORS['cell_closed'])
        else:
            self.flagged.add((row, col))
            btn.config(text="🚩", bg=self.COLORS['cell_closed'])
        
        self.update_mines_counter()
        self.check_win()
    
    def on_middle_click(self, row: int, col: int):
        """Обработка средней кнопки (открытие соседей если флагов достаточно)"""
        if self.game_over or (row, col) not in self.revealed:
            return
        
        mines_nearby = self.count_adjacent_mines(row, col)
        flags_nearby = sum(1 for nr, nc in self.get_neighbors(row, col) 
                          if (nr, nc) in self.flagged)
        
        if mines_nearby == flags_nearby and mines_nearby > 0:
            for nr, nc in self.get_neighbors(row, col):
                if (nr, nc) not in self.revealed and (nr, nc) not in self.flagged:
                    self.reveal_cell(nr, nc)
    
    def check_win(self):
        """Проверка условия победы"""
        if self.game_over:
            return
        
        # Победа если все не-минные клетки открыты
        total_cells = self.rows * self.cols
        if len(self.revealed) == total_cells - self.mines_count:
            self.game_over_win()
    
    def game_over_win(self):
        """Победа"""
        self.game_over = True
        self.timer_running = False
        
        # Отметить все мины флагами
        for row, col in self.mines_positions:
            if (row, col) not in self.flagged:
                self.buttons[row][col].config(text="🚩", bg=self.COLORS['flag'])
        
        messagebox.showinfo("🎉 Победа!", 
                           f"Поздравляем! Вы победили!\n"
                           f"Время: {self.time_elapsed} сек\n"
                           f"Сложность: {self.difficulty}")
    
    def game_over_lose(self):
        """Проигрыш"""
        self.game_over = True
        self.timer_running = False
        
        # Показать все мины
        for row, col in self.mines_positions:
            btn = self.buttons[row][col]
            if (row, col) not in self.flagged:
                btn.config(text="💣", bg=self.COLORS['mine'])
        
        # Показать неправильные флаги
        for row, col in self.flagged:
            if (row, col) not in self.mines_positions:
                self.buttons[row][col].config(text="❌", bg=self.COLORS['mine'])
        
        messagebox.showwarning("💥 Бум!", 
                              f"Игра окончена!\n"
                              f"Вы подорвались на мине.\n"
                              f"Время: {self.time_elapsed} сек")
    
    def update_mines_counter(self):
        """Обновление счётчика мин"""
        remaining = self.mines_count - len(self.flagged)
        self.mines_label.config(text=f"{remaining:02d}")
    
    def start_timer(self):
        """Запуск таймера"""
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()
    
    def update_timer(self):
        """Обновление таймера"""
        if self.timer_running:
            self.time_elapsed += 1
            self.timer_label.config(text=f"{self.time_elapsed:03d}")
            self.root.after(1000, self.update_timer)


def main():
    """Запуск игры"""
    root = tk.Tk()
    
    # Центрирование окна
    root.update_idletasks()
    width = 600
    height = 700
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    game = MinesweeperGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
