import tkinter as tk
from tkinter import simpledialog
import heapq
import math


class GraphApp:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, bg='white', width=600, height=400)
        self.canvas.pack()

        self.Radius = 15
        # ключ – id овала, значение – кортеж ((x, y), id текста)
        self.nodes = {}
        self.number_node = 1
        # self.edges: ключ – id линии, значение – кортеж (node1, node2, weight, weight_text)
        self.edges = {}
        self.selected_node = None
        self.mode = 'N'    # 'N' – добавление узла, 'E' – добавление ребра
        self.start_coords = (None, None)
        self.line = None

        # Флаги для анимации и выбора вершин для поиска кратчайшего пути
        self.animating = False
        self.selecting_path = False
        self.selecting_start = False
        self.selecting_end = False
        self.start_vertex = None
        self.end_vertex = None
        self.current_algorithm = None  # "dijkstra" или "floyd"

        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.move_mouse)
        self.canvas.bind("<ButtonRelease-1>", self.release_mouse)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Double-Button-1>", self.double_click)

        # Фрейм для кнопок управления
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.dijkstra_button = tk.Button(
            self.button_frame, text="Dijkstra", command=self.start_dijkstra)
        self.dijkstra_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.floyd_button = tk.Button(
            self.button_frame, text="Floyd", command=self.start_floyd)
        self.floyd_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.reset_button = tk.Button(
            self.button_frame, text="Reset Colors", command=self.reset_colors)
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.clear_button = tk.Button(
            self.button_frame, text="Clear Graph", command=self.clear_graph)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Сохраняем исходные цвета кнопок для сброса
        self.default_dijkstra_button_color = self.dijkstra_button.cget("bg")
        self.default_floyd_button_color = self.floyd_button.cget("bg")

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
            return  # блокировка во время анимации

        # Если идёт выбор вершин для поиска пути – обрабатываем клик отдельно
        if self.selecting_path:
            self.select_path_vertex(event)
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
                # Запрашиваем вес ребра
                weight = simpledialog.askfloat(
                    "Edge Weight", "Enter weight for this edge:", minvalue=0.0)
                if weight is None:
                    weight = 1.0
                # Создаем текст для веса в середине ребра
                x_mid = (self.start_coords[0] + target_center[0]) / 2
                y_mid = (self.start_coords[1] + target_center[1]) / 2
                weight_text = self.canvas.create_text(
                    x_mid, y_mid, text=str(weight), fill="black")
                self.edges[self.line] = (
                    self.selected_node, target, weight, weight_text)
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
            # Сохраняем центр узла для начала ребра
            self.start_coords = self.nodes[node][0]

    def add_node(self, x, y):
        R = self.Radius
        current_node = self.check_node(x, y)
        if current_node is None:
            # Создаем новый узел (овал) и текст с номером вершины
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
            # Обновляем положение для всех ребер, связанных с этим узлом
            for edge_id, edge_data in self.edges.items():
                n1, n2 = edge_data[0], edge_data[1]
                if self.selected_node in (n1, n2):
                    x1, y1 = self.nodes[n1][0]
                    x2, y2 = self.nodes[n2][0]
                    self.canvas.coords(edge_id, x1, y1, x2, y2)
                    # Если у ребра есть текст с весом, перемещаем его в середину
                    if len(edge_data) == 4:
                        weight_text = edge_data[3]
                        x_mid = (x1 + x2) / 2
                        y_mid = (y1 + y2) / 2
                        self.canvas.coords(weight_text, x_mid, y_mid)

    def delete_node(self, x, y):
        node = self.check_node(x, y)
        if node in self.nodes:
            # Удаляем ребра, связанные с узлом
            edges_to_delete = []
            for edge_id, (n1, n2, *rest) in list(self.edges.items()):
                if n1 == node or n2 == node:
                    self.canvas.delete(edge_id)
                    if rest and len(rest) == 2:
                        self.canvas.delete(rest[1])  # удаляем текст веса
                    edges_to_delete.append(edge_id)
            for edge_id in edges_to_delete:
                del self.edges[edge_id]
            # Удаляем текст и сам узел
            self.canvas.delete(self.nodes[node][1])
            self.canvas.delete(node)
            del self.nodes[node]

    def add_edge(self, x, y):
        # Удаляем предыдущую временную линию (если есть)
        if self.line is not None:
            self.canvas.delete(self.line)
            self.line = None
        # Рисуем временную линию от сохранённого центра (self.start_coords) до текущей позиции
        self.line = self.canvas.create_line(
            self.start_coords[0], self.start_coords[1], x, y, fill='red')

    def clear_graph(self):
        """Удаляет все узлы и ребра с холста."""
        for edge_id, edge_data in list(self.edges.items()):
            self.canvas.delete(edge_id)
            self.canvas.delete(edge_data[3])
        self.edges.clear()
        for node, (center, text) in list(self.nodes.items()):
            self.canvas.delete(text)
            self.canvas.delete(node)
        self.nodes.clear()

    def reset_colors(self):
        """Сбрасывает цвет всех узлов на синий и рёбер на красный."""
        for node in self.nodes:
            self.canvas.itemconfig(node, fill="blue")
        for edge_id in self.edges:
            self.canvas.itemconfig(edge_id, fill="red", width=1)

    # ========== Функциональность поиска кратчайшего пути ==========

    def start_dijkstra(self):
        if self.animating or not self.nodes:
            return
        self.disable_buttons()
        self.dijkstra_button.config(state=tk.NORMAL)
        self.reset_colors()
        self.current_algorithm = "dijkstra"
        self.selecting_path = True
        self.selecting_start = True
        self.selecting_end = False
        self.start_vertex = None
        self.end_vertex = None
        self.canvas.config(cursor="crosshair")
        self.dijkstra_button.config(bg="yellow", text="Select start vertex")

    def start_floyd(self):
        if self.animating or not self.nodes:
            return
        self.disable_buttons()
        self.floyd_button.config(state=tk.NORMAL)
        self.reset_colors()
        self.current_algorithm = "floyd"
        self.selecting_path = True
        self.selecting_start = True
        self.selecting_end = False
        self.start_vertex = None
        self.end_vertex = None
        self.canvas.config(cursor="crosshair")
        self.floyd_button.config(bg="yellow", text="Select start vertex")

    def select_path_vertex(self, event):
        """Обрабатывает выбор вершины для поиска кратчайшего пути."""
        x, y = event.x, event.y
        node = self.check_node(x, y)
        if node is None:
            return  # клик по пустому месту – игнорируем
        if self.selecting_start:
            self.start_vertex = node
            self.selecting_start = False
            self.selecting_end = True
            if self.current_algorithm == "dijkstra":
                self.dijkstra_button.config(text="Select end vertex")
            elif self.current_algorithm == "floyd":
                self.floyd_button.config(text="Select end vertex")
        elif self.selecting_end:
            self.end_vertex = node
            self.selecting_path = False
            self.selecting_end = False
            self.canvas.config(cursor="")
            # Сбросим цвета кнопок поиска
            if self.current_algorithm == "dijkstra":
                self.dijkstra_button.config(
                    bg=self.default_dijkstra_button_color, text="Dijkstra")
            elif self.current_algorithm == "floyd":
                self.floyd_button.config(
                    bg=self.default_floyd_button_color, text="Floyd")
            # Запускаем поиск кратчайшего пути
            if self.current_algorithm == "dijkstra":
                path = self.dijkstra(self.start_vertex, self.end_vertex)
            elif self.current_algorithm == "floyd":
                path = self.floyd(self.start_vertex, self.end_vertex)
            if path:
                print("Shortest path:", [self.nodes[n][1] for n in path])
                self.animate_path(path)
            else:
                print("No path found")
                self.enable_buttons()

    def dijkstra(self, start, end):
        """
        Выполняет алгоритм Дейкстры для поиска кратчайшего пути.
        Возвращает список вершин (их id) в порядке прохождения или None, если путь не найден.
        """
        # Построим граф как словарь: для каждого узла – список (neighbor, weight, edge_id)
        graph = {node: [] for node in self.nodes}
        for edge_id, edge_data in self.edges.items():
            if len(edge_data) < 3:
                continue
            n1, n2, weight = edge_data[0], edge_data[1], edge_data[2]
            graph[n1].append((n2, weight, edge_id))
            graph[n2].append((n1, weight, edge_id))  # граф неориентированный

        dist = {node: math.inf for node in self.nodes}
        prev = {node: None for node in self.nodes}
        dist[start] = 0
        pq = [(0, start)]
        while pq:
            d, current = heapq.heappop(pq)
            if current == end:
                break
            if d > dist[current]:
                continue
            for neighbor, w, e_id in graph[current]:
                alt = d + w
                if alt < dist[neighbor]:
                    dist[neighbor] = alt
                    prev[neighbor] = current
                    heapq.heappush(pq, (alt, neighbor))
        if dist[end] == math.inf:
            return None  # путь не найден
        # Восстанавливаем путь
        path = []
        cur = end
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path

    def floyd(self, start, end):
        """
        Выполняет алгоритм Флойда для поиска кратчайшего пути между всеми парами.
        Затем восстанавливает путь от start до end.
        Возвращает список вершин (их id) в порядке прохождения или None, если путь не найден.
        """
        nodes_list = list(self.nodes.keys())
        n = len(nodes_list)
        # Инициализируем матрицу расстояний и матрицу next для восстановления пути
        dist = {u: {v: math.inf for v in nodes_list} for u in nodes_list}
        nxt = {u: {v: None for v in nodes_list} for u in nodes_list}
        for u in nodes_list:
            dist[u][u] = 0
        # Для каждого ребра задаём расстояние и следующий узел
        for edge_id, edge_data in self.edges.items():
            if len(edge_data) < 3:
                continue
            u, v, weight = edge_data[0], edge_data[1], edge_data[2]
            # Если несколько ребер между парой вершин, оставляем минимальное
            if weight < dist[u][v]:
                dist[u][v] = weight
                dist[v][u] = weight
                nxt[u][v] = v
                nxt[v][u] = u

        # Алгоритм Флойда-Уоршелла
        for k in nodes_list:
            for i in nodes_list:
                for j in nodes_list:
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        nxt[i][j] = nxt[i][k]
        if nxt[start][end] is None:
            return None  # путь не найден
        # Восстанавливаем путь
        path = [start]
        while start != end:
            start = nxt[start][end]
            path.append(start)
        return path

    def animate_path(self, path):
        """Анимирует кратчайший путь: вершины подсвечиваются, а рёбра между ними окрашиваются."""
        self.animating = True
        self.animation_path = path
        self.current_path_index = 0
        self.animate_next_path()

    def animate_next_path(self):
        if self.current_path_index < len(self.animation_path):
            node = self.animation_path[self.current_path_index]
            self.canvas.itemconfig(node, fill="orange")
            if self.current_path_index > 0:
                prev_node = self.animation_path[self.current_path_index - 1]
                edge_id = self.find_edge_between(prev_node, node)
                if edge_id is not None:
                    self.canvas.itemconfig(edge_id, fill="purple", width=3)
            self.current_path_index += 1
            self.master.after(500, self.animate_next_path)
        else:
            # После анимации помечаем все вершины пути зелёным
            for n in self.animation_path:
                self.canvas.itemconfig(n, fill="green")
            self.animating = False
            self.enable_buttons()

    def find_edge_between(self, node1, node2):
        """Находит ребро, соединяющее node1 и node2 (если есть)."""
        for edge_id, edge_data in self.edges.items():
            u, v = edge_data[0], edge_data[1]
            if (node1 == u and node2 == v) or (node1 == v and node2 == u):
                return edge_id
        return None

    # ========== Управление кнопками ==========

    def disable_buttons(self):
        self.dijkstra_button.config(state=tk.DISABLED)
        self.floyd_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.dijkstra_button.config(state=tk.NORMAL)
        self.floyd_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Graph Shortest Path Search")
    app = GraphApp(root)
    root.mainloop()
