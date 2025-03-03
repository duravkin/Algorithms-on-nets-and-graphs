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
        self.nodes = {}    # ключ – id овала, значение – кортеж ((x, y), id текста)
        self.number_node = 1
        # self.edges: ключ – id линии, значение – кортеж (node1, node2, weight, weight_text)
        self.edges = {}
        self.selected_node = None
        self.mode = 'N'    # 'N' – добавление узла, 'E' – добавление ребра
        self.start_coords = (None, None)
        self.line = None

        # Флаги для анимации и выбора вершин для построения MST
        self.animating = False
        self.selecting_prim = False   # для алгоритма Прима (выбор стартовой вершины)
        self.current_algorithm = None  # "prim" или "kruskal"

        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.move_mouse)
        self.canvas.bind("<ButtonRelease-1>", self.release_mouse)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Double-Button-1>", self.double_click)

        # Фрейм для кнопок управления
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.prim_button = tk.Button(self.button_frame, text="Prim", command=self.start_prim)
        self.prim_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.kruskal_button = tk.Button(self.button_frame, text="Kruskal", command=self.start_kruskal)
        self.kruskal_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.reset_button = tk.Button(self.button_frame, text="Reset Colors", command=self.reset_colors)
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.clear_button = tk.Button(self.button_frame, text="Clear Graph", command=self.clear_graph)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Сохраняем исходные цвета кнопок для сброса
        self.default_prim_button_color = self.prim_button.cget("bg")
        self.default_kruskal_button_color = self.kruskal_button.cget("bg")

    # ======================= Работа с вершинами и ребрами =======================

    def check_node(self, x, y):
        """
        Возвращает id узла (овала), если в точке (x, y) найден соответствующий элемент.
        Если клик произошёл по тексту, возвращается соответствующий овал.
        """
        overlapping = self.canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1)
        for item in overlapping:
            if item in self.nodes:
                return item
        for item in overlapping:
            for node, (center, text) in self.nodes.items():
                if item == text:
                    return node
        return None

    def left_click(self, event):
        if self.animating:
            return  # блокировка во время анимации

        # Если выбираем стартовую вершину для алгоритма Прима
        if self.selecting_prim:
            self.select_prim_vertex(event)
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
                target_center = self.nodes[target][0]
                self.canvas.coords(self.line, self.start_coords[0], self.start_coords[1],
                                   target_center[0], target_center[1])
                # Запрос веса ребра
                weight = simpledialog.askfloat("Edge Weight", "Enter weight for this edge:", minvalue=0.0)
                if weight is None:
                    weight = 1.0
                x_mid = (self.start_coords[0] + target_center[0]) / 2
                y_mid = (self.start_coords[1] + target_center[1]) / 2
                weight_text = self.canvas.create_text(x_mid, y_mid, text=str(weight), fill="black")
                self.edges[self.line] = (self.selected_node, target, weight, weight_text)
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
            self.start_coords = self.nodes[node][0]

    def add_node(self, x, y):
        R = self.Radius
        current_node = self.check_node(x, y)
        if current_node is None:
            node = self.canvas.create_oval(x - R, y - R, x + R, y + R, fill='blue')
            text = self.canvas.create_text(x, y, text=str(self.number_node), fill='white')
            self.number_node += 1
            self.nodes[node] = ((x, y), text)
        else:
            self.selected_node = current_node

    def move_node(self, x, y):
        if self.selected_node is not None:
            R = self.Radius
            self.canvas.coords(self.selected_node, x - R, y - R, x + R, y + R)
            self.canvas.coords(self.nodes[self.selected_node][1], x, y)
            self.nodes[self.selected_node] = ((x, y), self.nodes[self.selected_node][1])
            for edge_id, edge_data in self.edges.items():
                u, v = edge_data[0], edge_data[1]
                if self.selected_node in (u, v):
                    x1, y1 = self.nodes[u][0]
                    x2, y2 = self.nodes[v][0]
                    self.canvas.coords(edge_id, x1, y1, x2, y2)
                    if len(edge_data) == 4:
                        weight_text = edge_data[3]
                        x_mid = (x1 + x2) / 2
                        y_mid = (y1 + y2) / 2
                        self.canvas.coords(weight_text, x_mid, y_mid)

    def delete_node(self, x, y):
        node = self.check_node(x, y)
        if node in self.nodes:
            edges_to_delete = []
            for edge_id, (u, v, *rest) in list(self.edges.items()):
                if u == node or v == node:
                    self.canvas.delete(edge_id)
                    if rest and len(rest) == 2:
                        self.canvas.delete(rest[1])
                    edges_to_delete.append(edge_id)
            for edge_id in edges_to_delete:
                del self.edges[edge_id]
            self.canvas.delete(self.nodes[node][1])
            self.canvas.delete(node)
            del self.nodes[node]

    def add_edge(self, x, y):
        if self.line is not None:
            self.canvas.delete(self.line)
            self.line = None
        self.line = self.canvas.create_line(self.start_coords[0], self.start_coords[1], x, y, fill='red')

    def clear_graph(self):
        for edge_id in list(self.edges.keys()):
            self.canvas.delete(edge_id)
        self.edges.clear()
        for node, (center, text) in list(self.nodes.items()):
            self.canvas.delete(text)
            self.canvas.delete(node)
        self.nodes.clear()

    def reset_colors(self):
        for node in self.nodes:
            self.canvas.itemconfig(node, fill="blue")
        for edge_id in self.edges:
            self.canvas.itemconfig(edge_id, fill="red", width=1)

    # ======================= MST: Алгоритм Прима и Краскала =======================

    def start_prim(self):
        """Запускает алгоритм Прима для построения MST с выбором стартовой вершины."""
        if self.animating or not self.nodes:
            return
        self.disable_buttons()
        self.reset_colors()
        self.current_algorithm = "prim"
        self.selecting_prim = True
        self.canvas.config(cursor="crosshair")
        self.prim_button.config(bg="yellow", text="Select start vertex")

    def select_prim_vertex(self, event):
        """Выбор стартовой вершины для алгоритма Прима."""
        x, y = event.x, event.y
        node = self.check_node(x, y)
        if node is None:
            return
        self.selecting_prim = False
        self.canvas.config(cursor="")
        self.prim_button.config(bg=self.default_prim_button_color, text="Prim")
        mst_edges = self.prim(node)
        if mst_edges:
            print("Prim MST edges:", mst_edges)
            self.animate_mst(mst_edges)
        else:
            print("No MST found")
            self.enable_buttons()

    def prim(self, start):
        """
        Реализует алгоритм Прима для построения минимального остовного дерева.
        Возвращает список id рёбер, входящих в MST или None, если MST построить не удалось.
        """
        visited = set()
        mst_edges = []
        visited.add(start)
        pq = []
        # Добавляем все рёбра, исходящие из стартовой вершины
        for edge_id, edge_data in self.edges.items():
            u, v, weight = edge_data[0], edge_data[1], edge_data[2]
            if u == start and v not in visited:
                heapq.heappush(pq, (weight, edge_id, u, v))
            elif v == start and u not in visited:
                heapq.heappush(pq, (weight, edge_id, v, u))
        while pq and len(visited) < len(self.nodes):
            weight, edge_id, u, v = heapq.heappop(pq)
            if v in visited:
                continue
            mst_edges.append(edge_id)
            visited.add(v)
            # Добавляем новые рёбра, выходящие из только что добавленной вершины
            for e_id, e_data in self.edges.items():
                a, b, w = e_data[0], e_data[1], e_data[2]
                if a == v and b not in visited:
                    heapq.heappush(pq, (w, e_id, a, b))
                elif b == v and a not in visited:
                    heapq.heappush(pq, (w, e_id, b, a))
        if len(visited) == len(self.nodes):
            return mst_edges
        else:
            return None

    def start_kruskal(self):
        """Запускает алгоритм Краскала для построения MST."""
        if self.animating or not self.nodes:
            return
        self.disable_buttons()
        self.reset_colors()
        self.current_algorithm = "kruskal"
        self.kruskal_button.config(bg="yellow", text="Kruskal (running)")
        mst_edges = self.kruskal()
        if mst_edges:
            print("Kruskal MST edges:", mst_edges)
            self.animate_mst(mst_edges)
        else:
            print("No MST found")
            self.enable_buttons()
        self.kruskal_button.config(bg=self.default_kruskal_button_color, text="Kruskal")

    def kruskal(self):
        """
        Реализует алгоритм Краскала для построения минимального остовного дерева.
        Возвращает список id рёбер, входящих в MST или None, если MST построить не удалось.
        """
        edges_list = []
        for edge_id, edge_data in self.edges.items():
            u, v, weight = edge_data[0], edge_data[1], edge_data[2]
            edges_list.append((weight, edge_id, u, v))
        edges_list.sort(key=lambda x: x[0])
        parent = {node: node for node in self.nodes}
        rank = {node: 0 for node in self.nodes}

        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u

        def union(u, v):
            ru = find(u)
            rv = find(v)
            if ru == rv:
                return False
            if rank[ru] < rank[rv]:
                parent[ru] = rv
            elif rank[ru] > rank[rv]:
                parent[rv] = ru
            else:
                parent[rv] = ru
                rank[ru] += 1
            return True

        mst_edges = []
        for weight, edge_id, u, v in edges_list:
            if union(u, v):
                mst_edges.append(edge_id)
        roots = set(find(node) for node in self.nodes)
        if len(roots) == 1:
            return mst_edges
        else:
            return None

    def animate_mst(self, mst_edges):
        """Анимирует MST: рёбра по очереди подсвечиваются пурпурным, а вершины – оранжевым с последующим окончательным зелёным цветом."""
        self.animating = True
        self.mst_edges = mst_edges
        self.current_mst_index = 0
        self.animate_next_mst()

    def animate_next_mst(self):
        if self.current_mst_index < len(self.mst_edges):
            edge_id = self.mst_edges[self.current_mst_index]
            self.canvas.itemconfig(edge_id, fill="purple", width=3)
            edge_data = self.edges[edge_id]
            u, v = edge_data[0], edge_data[1]
            self.canvas.itemconfig(u, fill="orange")
            self.canvas.itemconfig(v, fill="orange")
            self.current_mst_index += 1
            self.master.after(500, self.animate_next_mst)
        else:
            for node in self.nodes:
                self.canvas.itemconfig(node, fill="green")
            self.animating = False
            self.enable_buttons()

    # ======================= Управление кнопками =======================

    def disable_buttons(self):
        self.prim_button.config(state=tk.DISABLED)
        self.kruskal_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.prim_button.config(state=tk.NORMAL)
        self.kruskal_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Graph MST: Prim and Kruskal")
    app = GraphApp(root)
    root.mainloop()
