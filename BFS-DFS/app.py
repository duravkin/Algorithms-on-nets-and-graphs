import tkinter as tk


class GraphApp:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, bg='white', width=600, height=400)
        self.canvas.pack()
        self.Radius = 15

        self.nodes = dict()
        self.edges = list()
        self.selected_node = None
        self.mode = 'N'

        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.move_mouse)
        self.canvas.bind("<Button-3>", self.right_click)

    def check_node(self, x, y):
        overlapping = self.canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1)
        if len(overlapping) > 0:
            return overlapping[0]
        return None

    def left_click(self, event):
        x, y = event.x, event.y
        if self.mode == 'N':
            self.add_node(x, y)

    def move_mouse(self, event):
        x, y = event.x, event.y
        R = self.Radius

        # Сброс выбора узла, если кнопка мыши отпущена
        if event.state == 0:
            self.selected_node = None
        elif self.mode == 'N':
            self.move_node(x, y)

    def right_click(self, event):
        x, y = event.x, event.y
        if self.mode == 'N':
            self.delete_node(x, y)

    def add_node(self, x, y):
        R = self.Radius
        # Проверяем, не находится ли новая вершина рядом с другими
        current_node = self.check_node(x, y)
        if current_node is None:
            # Если вершина не найдена, создаем новую
            node = self.canvas.create_oval(
                x - R, y - R, x + R, y + R, fill='blue')
            text = self.canvas.create_text(
                x, y, text=str(len(self.nodes) + 1), fill='white')

            self.nodes[node] = ((x, y), text)
        else:
            # Если вершина уже есть, выбираем ее
            self.selected_node = current_node

    def move_node(self, x, y):
        # Если узел уже выбран, перемещаем его
        if self.selected_node is not None:
            R = self.Radius
            self.canvas.coords(self.selected_node, x - R, y - R, x + R, y + R)
            self.canvas.coords(self.nodes[self.selected_node][1], x, y)

    def delete_node(self, x, y):
        node = self.check_node(x, y)
        if node in self.nodes:
            self.canvas.delete(node)
            self.nodes.pop(node)


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
