import tkinter as tk


class GraphApp:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, bg='white', width=600, height=400)
        self.canvas.pack()
        self.Radius = 15

        self.nodes = {}    # Ключ – id овала, значение – кортеж ((x, y), id текста)
        self.edges = {}    # Ключ – id линии (ребра), значение – кортеж (id узла1, id узла2)
        self.selected_node = None
        self.mode = 'N'  # 'N' – добавление узла, 'E' – добавление ребра
        self.start_coords = (None, None)
        self.line = None

        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.move_mouse)
        self.canvas.bind("<ButtonRelease-1>", self.release_mouse)  # исправлено
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Double-Button-1>", self.double_click)

    def check_node(self, x, y):
        overlapping = self.canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1)
        # Возвращаем только те элементы, которые являются узлами (находятся в self.nodes)
        for item in overlapping:
            if item in self.nodes:
                return item
        return None

    def left_click(self, event):
        x, y = event.x, event.y
        self.mode = 'N'
        self.add_node(x, y)

    def move_mouse(self, event):
        x, y = event.x, event.y

        if self.mode == 'N':
            self.move_node(x, y)
        elif self.mode == 'E':
            self.add_edge(x, y)

    def release_mouse(self, event):
        x, y = event.x, event.y
        if self.mode == 'E':
            target = self.check_node(x, y)
            if target is not None and target != self.selected_node:
                # Ребро сохраняется как созданная временная линия
                self.edges[self.line] = (self.selected_node, target)
            else:
                # Если целевой узел не найден, удаляем временную линию
                if self.line is not None:
                    self.canvas.delete(self.line)
            # Сбрасываем режим и временные переменные
            self.mode = 'N'
            self.selected_node = None
            self.line = None

    def right_click(self, event):
        x, y = event.x, event.y
        self.delete_node(x, y)

    def double_click(self, event):
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
            # Создаем новый узел: овал и текст
            node = self.canvas.create_oval(x - R, y - R, x + R, y + R, fill='blue')
            text = self.canvas.create_text(x, y, text=str(len(self.nodes) + 1), fill='white')
            self.nodes[node] = ((x, y), text)
        else:
            # Если узел уже есть, выбираем его для перемещения
            self.selected_node = current_node

    def move_node(self, x, y):
        if self.selected_node is not None:
            R = self.Radius
            # Перемещаем овал
            self.canvas.coords(self.selected_node, x - R, y - R, x + R, y + R)
            # Перемещаем текст
            self.canvas.coords(self.nodes[self.selected_node][1], x, y)
            # Обновляем координаты узла в словаре
            self.nodes[self.selected_node] = ((x, y), self.nodes[self.selected_node][1])
            # Обновляем координаты для всех связанных ребер
            for edge, (n1, n2) in self.edges.items():
                x1, y1 = self.nodes[n1][0]
                x2, y2 = self.nodes[n2][0]
                self.canvas.coords(edge, x1, y1, x2, y2)

    def delete_node(self, x, y):
        node = self.check_node(x, y)
        if node in self.nodes:
            # Удаляем все ребра, связанные с узлом
            edges_to_delete = []
            for edge, (n1, n2) in self.edges.items():
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
        self.line = self.canvas.create_line(self.start_coords[0], self.start_coords[1], x, y, fill='red')


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
