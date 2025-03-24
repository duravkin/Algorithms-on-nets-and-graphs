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
        # Флаги работы анимации
        self.animating = False
        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.move_mouse)
        self.canvas.bind("<ButtonRelease-1>", self.release_mouse)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Double-Button-1>", self.double_click)
        # Фрейм для кнопок управления
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.find_bridges_button = tk.Button(
            self.button_frame, text="Find Bridges", command=self.start_find_bridges)
        self.find_bridges_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.reset_button = tk.Button(
            self.button_frame, text="Reset Colors", command=self.reset_colors)
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.clear_button = tk.Button(
            self.button_frame, text="Clear Graph", command=self.clear_graph)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=5)
        # Сохраняем исходный цвет кнопок для сброса
        self.default_find_bridges_button_color = self.find_bridges_button.cget("bg")

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

    def find_bridges(self):
        """Находит мосты в графе с помощью алгоритма на основе времени входа."""
        graph = self.build_graph()
        visited = set()
        disc = {}
        low = {}
        parent = {}
        bridges = []

        time = [0]

        def dfs(u):
            visited.add(u)
            disc[u] = low[u] = time[0]
            time[0] += 1
            for v in graph[u]:
                if v not in visited:
                    parent[v] = u
                    dfs(v)
                    low[u] = min(low[u], low[v])
                    if low[v] > disc[u]:
                        bridges.append((u, v))
                elif v != parent.get(u, None):
                    low[u] = min(low[u], disc[v])

        for node in self.nodes:
            if node not in visited:
                parent[node] = None
                dfs(node)

        return bridges

    def start_find_bridges(self):
        if self.animating or not self.nodes:
            return
        self.disable_buttons()
        self.reset_colors()
        self.find_bridges_button.config(bg="yellow", text="Finding bridges...")
        bridges = self.find_bridges()
        self.animate_bridges(bridges)

    def animate_bridges(self, bridges):
        """Анимирует процесс поиска мостов и подсвечивает их."""
        self.animating = True
        self.animation_bridges = bridges
        self.current_animation_index = 0
        self.highlight_next_bridge()

    def highlight_next_bridge(self):
        if self.current_animation_index < len(self.animation_bridges):
            u, v = self.animation_bridges[self.current_animation_index]
            edge_id = None
            for edge, (n1, n2) in self.edges.items():
                if (n1 == u and n2 == v) or (n1 == v and n2 == u):
                    edge_id = edge
                    break
            if edge_id:
                self.canvas.itemconfig(edge_id, fill="orange", width=3)
            self.current_animation_index += 1
            self.master.after(500, self.highlight_next_bridge)
        else:
            self.animating = False
            self.enable_buttons()
            self.find_bridges_button.config(
                bg=self.default_find_bridges_button_color, text="Find Bridges")

    def disable_buttons(self):
        self.find_bridges_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.find_bridges_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)

    def reset_colors(self):
        """Сбрасывает цвет всех узлов и ребер на исходные."""
        for node in self.nodes:
            self.canvas.itemconfig(node, fill="blue")
        for edge in self.edges:
            self.canvas.itemconfig(edge, fill="red", width=1)

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
    root.title("Graph Bridge Finder")
    app = GraphApp(root)
    root.mainloop()