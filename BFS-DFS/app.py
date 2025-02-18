import tkinter as tk


class GraphApp:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, bg='white', width=600, height=400)
        self.canvas.pack()

        self.Radius = 15
        # ключ – id овала, значение – кортеж ((x, y), id текста)
        self.nodes = {}
        self.number_node = 1
        # ключ – id линии, значение – кортеж (id узла1, id узла2)
        self.edges = {}
        self.selected_node = None
        self.mode = 'N'    # 'N' – добавление узла, 'E' – добавление ребра
        self.start_coords = (None, None)
        self.line = None

        # Флаги работы анимации и выбора стартовой вершины
        self.animating = False
        self.current_traversal_type = None
        self.selecting_start = False

        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.move_mouse)
        self.canvas.bind("<ButtonRelease-1>", self.release_mouse)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Double-Button-1>", self.double_click)

        # Фрейм для кнопок управления
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.bfs_button = tk.Button(
            self.button_frame, text="BFS", command=self.start_bfs)
        self.bfs_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.dfs_button = tk.Button(
            self.button_frame, text="DFS", command=self.start_dfs)
        self.dfs_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.reset_button = tk.Button(
            self.button_frame, text="Reset Colors", command=self.reset_colors)
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.clear_button = tk.Button(
            self.button_frame, text="Clear Graph", command=self.clear_graph)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Сохраняем исходный цвет кнопок для сброса
        self.default_bfs_button_color = self.bfs_button.cget("bg")
        self.default_dfs_button_color = self.dfs_button.cget("bg")

    def check_node(self, x, y):
        """
        Возвращает id узла (овала), если в точке (x, y) найден соответствующий элемент.
        Если клик произошёл по тексту, возвращается соответствующий овал.
        """
        overlapping = self.canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1)
        for item in overlapping:
            if item in self.nodes:
                return item
        # Если не найден овал, проверяем текстовые объекты
        for item in overlapping:
            for node, (center, text) in self.nodes.items():
                if item == text:
                    return node
        return None

    def left_click(self, event):
        if self.animating:
            return  # запрещаем действия во время анимации
        # Если находимся в режиме выбора стартовой вершины – вызываем соответствующий метод
        if self.selecting_start:
            self.select_start_vertex(event)
            return
        x, y = event.x, event.y
        self.mode = 'N'
        self.add_node(x, y)

    def move_mouse(self, event):
        if self.animating:
            return
        x, y = event.x, event.y
        if self.mode == 'N':
            self.move_node(x, y)
        elif self.mode == 'E':
            self.add_edge(x, y)

    def release_mouse(self, event):
        if self.animating:
            return
        x, y = event.x, event.y
        if self.mode == 'E':
            target = self.check_node(x, y)
            if target is not None and target != self.selected_node:
                # Устанавливаем конечную точку линии в центр целевого узла
                target_center = self.nodes[target][0]
                self.canvas.coords(self.line, self.start_coords[0], self.start_coords[1],
                                   target_center[0], target_center[1])
                self.edges[self.line] = (self.selected_node, target)
            else:
                if self.line is not None:
                    self.canvas.delete(self.line)
            self.mode = 'N'
            self.selected_node = None
            self.line = None

    def right_click(self, event):
        if self.animating:
            return
        x, y = event.x, event.y
        self.delete_node(x, y)

    def double_click(self, event):
        if self.animating:
            return
        x, y = event.x, event.y
        node = self.check_node(x, y)
        if node is not None:
            self.selected_node = node
            self.mode = 'E'
            # Сохраняем центр узла как исходную точку для линии
            self.start_coords = self.nodes[node][0]

    def add_node(self, x, y):
        R = self.Radius
        current_node = self.check_node(x, y)
        if current_node is None:
            # Создаём новый узел: овал и текст
            node = self.canvas.create_oval(
                x - R, y - R, x + R, y + R, fill='blue')
            text = self.canvas.create_text(
                x, y, text=str(self.number_node), fill='white')
            self.number_node += 1
            self.nodes[node] = ((x, y), text)
        else:
            self.selected_node = current_node

    def move_node(self, x, y):
        if self.selected_node is not None:
            R = self.Radius
            self.canvas.coords(self.selected_node, x - R, y - R, x + R, y + R)
            self.canvas.coords(self.nodes[self.selected_node][1], x, y)
            # Обновляем координаты узла в словаре
            self.nodes[self.selected_node] = (
                (x, y), self.nodes[self.selected_node][1])
            # Обновляем координаты для всех ребер, связанных с этим узлом
            for edge, (n1, n2) in self.edges.items():
                x1, y1 = self.nodes[n1][0]
                x2, y2 = self.nodes[n2][0]
                self.canvas.coords(edge, x1, y1, x2, y2)

    def delete_node(self, x, y):
        node = self.check_node(x, y)
        if node in self.nodes:
            # Удаляем ребра, связанные с узлом
            edges_to_delete = []
            for edge, (n1, n2) in list(self.edges.items()):
                if n1 == node or n2 == node:
                    self.canvas.delete(edge)
                    edges_to_delete.append(edge)
            for edge in edges_to_delete:
                del self.edges[edge]
            # Удаляем текст и сам узел
            self.canvas.delete(self.nodes[node][1])
            self.canvas.delete(node)
            del self.nodes[node]

    def add_edge(self, x, y):
        # Каждый раз удаляем предыдущую временную линию (если есть)
        if self.line is not None:
            self.canvas.delete(self.line)
            self.line = None
        # Рисуем временную линию от сохранённого центра (self.start_coords) до текущей позиции
        self.line = self.canvas.create_line(
            self.start_coords[0], self.start_coords[1], x, y, fill='red')

    def build_graph(self):
        """Строит представление графа в виде словаря смежности."""
        graph = {}
        for node in self.nodes:
            graph[node] = []
        for edge in self.edges.values():
            n1, n2 = edge
            if n1 in graph and n2 in graph:
                graph[n1].append(n2)
                graph[n2].append(n1)
        return graph

    def bfs(self, start):
        """Обход графа в ширину (BFS). Возвращает список узлов в порядке обхода."""
        graph = self.build_graph()
        visited = set()
        order = []
        queue = [start]
        visited.add(start)
        while queue:
            current = queue.pop(0)
            order.append(current)
            for neighbor in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def dfs(self, start):
        """Обход графа в глубину (DFS). Возвращает список узлов в порядке обхода."""
        graph = self.build_graph()
        visited = set()
        order = []

        def dfs_visit(node):
            visited.add(node)
            order.append(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs_visit(neighbor)

        dfs_visit(start)
        return order

    def start_bfs(self):
        if self.animating or not self.nodes:
            return
        self.disable_buttons()
        self.bfs_button.config(state=tk.NORMAL)
        self.reset_colors()
        self.current_traversal_type = "BFS"
        self.selecting_start = True
        self.canvas.config(cursor="crosshair")
        self.bfs_button.config(bg="yellow", text="Select start vertex")

    def start_dfs(self):
        if self.animating or not self.nodes:
            return
        self.disable_buttons()
        self.dfs_button.config(state=tk.NORMAL)
        self.reset_colors()
        self.current_traversal_type = "DFS"
        self.selecting_start = True
        self.canvas.config(cursor="crosshair")
        self.dfs_button.config(bg="yellow", text="Select start vertex")

    def select_start_vertex(self, event):
        """Выбираем вершину для старта обхода при клике, когда включен режим выбора."""
        x, y = event.x, event.y
        node = self.check_node(x, y)
        if node is None:
            # Если клик по пустому месту – игнорируем
            return
        # Сбрасываем режим выбора стартовой вершины и восстанавливаем курсор
        self.selecting_start = False
        self.canvas.config(cursor="")
        if self.current_traversal_type == "BFS":
            self.bfs_button.config(bg="yellow", text="BFS (running)")
            order = self.bfs(node)
            self.animate_order(order)
        elif self.current_traversal_type == "DFS":
            self.dfs_button.config(bg="yellow", text="DFS (running)")
            order = self.dfs(node)
            self.animate_order(order)

    def animate_order(self, order):
        """Анимирует обход: узлы последовательно подсвечиваются оранжевым, затем становятся зелёными."""
        self.animating = True
        self.animation_order = order
        self.current_animation_index = 0
        self.animate_next_node()

    def animate_next_node(self):
        # Если уже был подсвечен предыдущий узел, меняем его цвет на зеленый (посещённый)
        if self.current_animation_index > 0:
            prev_node = self.animation_order[self.current_animation_index - 1]
            self.canvas.itemconfig(prev_node, fill="green")
        if self.current_animation_index < len(self.animation_order):
            current_node = self.animation_order[self.current_animation_index]
            self.canvas.itemconfig(current_node, fill="orange")
            self.current_animation_index += 1
            # Задержка 500 мс перед обработкой следующего узла
            self.master.after(500, self.animate_next_node)
        else:
            self.animating = False
            self.enable_buttons()
            # Сброс цвета и текста активной кнопки обхода
            if self.current_traversal_type == "BFS":
                self.bfs_button.config(
                    bg=self.default_bfs_button_color, text="BFS")
            elif self.current_traversal_type == "DFS":
                self.dfs_button.config(
                    bg=self.default_dfs_button_color, text="DFS")
            self.current_traversal_type = None

    def disable_buttons(self):
        self.bfs_button.config(state=tk.DISABLED)
        self.dfs_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.bfs_button.config(state=tk.NORMAL)
        self.dfs_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)

    def reset_colors(self):
        """Сбрасывает цвет всех узлов на синий."""
        for node in self.nodes:
            self.canvas.itemconfig(node, fill="blue")

    def clear_graph(self):
        """Удаляет все узлы и ребра с холста."""
        # Удаляем все ребра
        for edge in list(self.edges.keys()):
            self.canvas.delete(edge)
        self.edges.clear()
        # Удаляем все узлы и связанные тексты
        for node, (center, text) in list(self.nodes.items()):
            self.canvas.delete(text)
            self.canvas.delete(node)
        self.nodes.clear()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Graph traversal (BFS & DFS)")
    app = GraphApp(root)
    root.mainloop()
