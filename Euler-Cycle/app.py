import tkinter as tk
from tkinter import messagebox


class GraphApp:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, bg='white', width=600, height=400)
        self.canvas.pack()

        self.Radius = 15
        self.nodes = {}
        self.number_node = 1
        self.edges = {}
        self.selected_node = None
        self.mode = 'N'
        self.start_coords = (None, None)
        self.line = None

        self.animating = False

        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.move_mouse)
        self.canvas.bind("<ButtonRelease-1>", self.release_mouse)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Double-Button-1>", self.double_click)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.euler_button = tk.Button(
            self.button_frame, text="Find Eulerian Cycle", command=self.start_eulerian)
        self.euler_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.reset_button = tk.Button(
            self.button_frame, text="Reset Colors", command=self.reset_colors)
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.clear_button = tk.Button(
            self.button_frame, text="Clear Graph", command=self.clear_graph)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=5)

    def check_node(self, x, y):
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
            self.start_coords = self.nodes[node][0]

    def add_node(self, x, y):
        R = self.Radius
        current_node = self.check_node(x, y)
        if current_node is None:
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
            self.nodes[self.selected_node] = (
                (x, y), self.nodes[self.selected_node][1])
            for edge_id, edge_data in self.edges.items():
                n1, n2 = edge_data[0], edge_data[1]
                if self.selected_node in (n1, n2):
                    x1, y1 = self.nodes[n1][0]
                    x2, y2 = self.nodes[n2][0]
                    self.canvas.coords(edge_id, x1, y1, x2, y2)

    def delete_node(self, x, y):
        node = self.check_node(x, y)
        if node in self.nodes:
            edges_to_delete = []
            for edge_id, (n1, n2) in list(self.edges.items()):
                if n1 == node or n2 == node:
                    self.canvas.delete(edge_id)
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
        self.line = self.canvas.create_line(
            self.start_coords[0], self.start_coords[1], x, y, fill='red')

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

    def all_degrees_even(self):
        degrees = {node: 0 for node in self.nodes}
        for u, v in self.edges.values():
            degrees[u] += 1
            degrees[v] += 1
        return all(degree % 2 == 0 for degree in degrees.values())

    def is_connected(self):
        if not self.nodes:
            return False
        visited = set()
        start_node = next(iter(self.nodes.keys()))
        stack = [start_node]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                neighbors = []
                for u, v in self.edges.values():
                    if u == node:
                        neighbors.append(v)
                    elif v == node:
                        neighbors.append(u)
                for neighbor in neighbors:
                    if neighbor not in visited:
                        stack.append(neighbor)
        return len(visited) == len(self.nodes)

    def find_eulerian_cycle_edges(self):
        if not self.is_connected() or not self.all_degrees_even():
            return None

        adj = {node: [] for node in self.nodes}
        for edge_id, (u, v) in self.edges.items():
            adj[u].append((v, edge_id))
            adj[v].append((u, edge_id))

        start_node = next(iter(self.nodes))
        stack = [start_node]
        path = []
        edge_order = []

        while stack:
            current = stack[-1]
            if adj[current]:
                next_node, edge_id = adj[current].pop()
                adj[next_node].remove((current, edge_id))
                stack.append(next_node)
                edge_order.append(edge_id)
            else:
                path.append(stack.pop())

        if len(edge_order) != len(self.edges):
            return None
        return edge_order[::-1]

    def start_eulerian(self):
        if self.animating:
            return
        self.disable_buttons()
        self.reset_colors()
        cycle_edges = self.find_eulerian_cycle_edges()
        if cycle_edges is None:
            messagebox.showinfo("Info", "No Eulerian Cycle exists!")
            self.enable_buttons()
            return
        self.animate_eulerian_cycle(cycle_edges)

    def animate_eulerian_cycle(self, edges_order):
        self.animating = True
        self.animation_edges = edges_order
        self.current_edge_index = 0
        self.animate_next_edge()

    def animate_next_edge(self):
        if self.current_edge_index < len(self.animation_edges):
            edge_id = self.animation_edges[self.current_edge_index]
            self.canvas.itemconfig(edge_id, fill="green", width=3)
            u, v = self.edges[edge_id]
            if self.current_edge_index == 0:
                self.canvas.itemconfig(u, fill="orange")
            self.canvas.itemconfig(v, fill="orange")
            self.current_edge_index += 1
            self.master.after(500, self.animate_next_edge)
        else:
            self.animating = False
            self.enable_buttons()

    def disable_buttons(self):
        self.euler_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.euler_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Eulerian Cycle Finder")
    app = GraphApp(root)
    root.mainloop()