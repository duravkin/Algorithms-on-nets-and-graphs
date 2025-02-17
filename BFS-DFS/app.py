import tkinter as tk

class GraphApp:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, bg='white', width=600, height=400)
        self.canvas.pack()

        self.Radius = 15
        self.nodes = {}    # ключ – id овала, значение – кортеж ((x, y), id текста)
        self.edges = {}    # ключ – id линии (ребра), значение – кортеж (id узла1, id узла2)
        self.selected_node = None
        self.mode = 'N'    # 'N' – добавление узла, 'E' – добавление ребра
        self.start_coords = (None, None)
        self.line = None

        # Флаг, указывающий, что анимация обхода запущена
        self.animating = False

        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.move_mouse)
        self.canvas.bind("<ButtonRelease-1>", self.release_mouse)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Double-Button-1>", self.double_click)

        # Фрейм для кнопок обхода
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.bfs_button = tk.Button(self.button_frame, text="BFS", command=self.start_bfs)
        self.bfs_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.dfs_button = tk.Button(self.button_frame, text="DFS", command=self.start_dfs)
        self.dfs_button.pack(side=tk.LEFT, padx=10, pady=5)

    def check_node(self, x, y):
        overlapping = self.canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1)
        for item in overlapping:
            if item in self.nodes:
                return item
        return None

    def left_click(self, event):
        if self.animating:
            return  # блокируем создание/перемещение во время анимации
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
                self.edges[self.line] = (self.selected_node, target)
                print("Edge created")
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
            self.start_coords = (x, y)

    def add_node(self, x, y):
        R = self.Radius
        current_node = self.check_node(x, y)
        if current_node is None:
            node = self.canvas.create_oval(
                x - R, y - R, x + R, y + R, fill='blue')
            text = self.canvas.create_text(
                x, y, text=str(len(self.nodes) + 1), fill='white')
            self.nodes[node] = ((x, y), text)
        else:
            self.selected_node = current_node

    def move_node(self, x, y):
        if self.selected_node is not None:
            R = self.Radius
            self.canvas.coords(self.selected_node, x - R, y - R, x + R, y + R)
            self.canvas.coords(self.nodes[self.selected_node][1], x, y)
            # Обновляем координаты в словаре
            self.nodes[self.selected_node] = ((x, y), self.nodes[self.selected_node][1])
            # Обновляем положение ребер, связанных с узлом
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
        if self.line is not None:
            self.canvas.delete(self.line)
            self.line = None
        self.line = self.canvas.create_line(
            self.start_coords[0], self.start_coords[1], x, y, fill='red')

    def build_graph(self):
        """Строит представление графа в виде словаря смежности"""
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
        """Обход графа в ширину (BFS) с возвратом порядка посещения узлов"""
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
        """Обход графа в глубину (DFS) с возвратом порядка посещения узлов"""
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
        # Выбираем первый добавленный узел как стартовую точку
        start_node = next(iter(self.nodes))
        order = self.bfs(start_node)
        print("BFS order:", order)
        self.animate_order(order)

    def start_dfs(self):
        if self.animating or not self.nodes:
            return
        self.disable_buttons()
        start_node = next(iter(self.nodes))
        order = self.dfs(start_node)
        print("DFS order:", order)
        self.animate_order(order)

    def animate_order(self, order):
        """Запускает анимацию обхода: узлы по очереди подсвечиваются оранжевым,
        затем становятся зелёными."""
        self.animating = True
        self.animation_order = order
        self.current_animation_index = 0
        self.animate_next_node()

    def animate_next_node(self):
        # Если не первый узел, меняем цвет предыдущего на зеленый (посещённый)
        if self.current_animation_index > 0:
            prev_node = self.animation_order[self.current_animation_index - 1]
            self.canvas.itemconfig(prev_node, fill="green")
        if self.current_animation_index < len(self.animation_order):
            current_node = self.animation_order[self.current_animation_index]
            self.canvas.itemconfig(current_node, fill="orange")
            self.current_animation_index += 1
            # Задержка 500 мс перед подсветкой следующего узла
            self.master.after(500, self.animate_next_node)
        else:
            self.animating = False
            self.enable_buttons()

    def disable_buttons(self):
        self.bfs_button.config(state=tk.DISABLED)
        self.dfs_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.bfs_button.config(state=tk.NORMAL)
        self.dfs_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
