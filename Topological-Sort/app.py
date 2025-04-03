import tkinter as tk
import tkinter.messagebox as messagebox


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
        self.order_labels = {}

        self.animating = False
        self.current_traversal_type = None

        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.move_mouse)
        self.canvas.bind("<ButtonRelease-1>", self.release_mouse)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Double-Button-1>", self.double_click)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.topological_button = tk.Button(
            self.button_frame, text="Topological Sort", command=self.start_topological_sort)
        self.topological_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.reset_button = tk.Button(
            self.button_frame, text="Reset Colors", command=self.reset_colors)
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.clear_button = tk.Button(
            self.button_frame, text="Clear Graph", command=self.clear_graph)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.default_topological_button_color = self.topological_button.cget("bg")

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
                self.canvas.itemconfig(self.line, arrow=tk.LAST)
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
            if self.selected_node not in self.nodes:
                self.selected_node = None
                return
                
            R = self.Radius
            self.canvas.coords(self.selected_node, x - R, y - R, x + R, y + R)
            self.canvas.coords(self.nodes[self.selected_node][1], x, y)
            if self.selected_node in self.order_labels:
                label_id = self.order_labels[self.selected_node]
                self.canvas.coords(label_id, x, y + 30)
            self.nodes[self.selected_node] = (
                (x, y), self.nodes[self.selected_node][1])
            for edge, (n1, n2) in self.edges.items():
                x1, y1 = self.nodes[n1][0]
                x2, y2 = self.nodes[n2][0]
                self.canvas.coords(edge, x1, y1, x2, y2)

    def delete_node(self, x, y):
        node = self.check_node(x, y)
        if node in self.nodes:
            if node in self.order_labels:
                label_id = self.order_labels.pop(node)
                self.canvas.delete(label_id)
            edges_to_delete = []
            for edge, (n1, n2) in list(self.edges.items()):
                if n1 == node or n2 == node:
                    self.canvas.delete(edge)
                    edges_to_delete.append(edge)
            for edge in edges_to_delete:
                del self.edges[edge]
            self.canvas.delete(self.nodes[node][1])
            self.canvas.delete(node)
            del self.nodes[node]

    def add_edge(self, x, y):
        if self.line is not None:
            self.canvas.delete(self.line)
            self.line = None
        self.line = self.canvas.create_line(
            self.start_coords[0], self.start_coords[1], x, y, fill='red', arrow=tk.LAST)

    def build_graph(self):
        graph = {node: [] for node in self.nodes}
        for edge in self.edges.values():
            n1, n2 = edge
            if n1 in graph and n2 in graph:
                graph[n1].append(n2)
        return graph

    def topological_sort(self):
        graph = self.build_graph()
        visited = {}
        order = []
        is_cyclic = False

        for node in graph:
            visited[node] = 0

        def dfs(node):
            nonlocal is_cyclic
            if visited[node] == 1:
                is_cyclic = True
                return
            if visited[node] == 2:
                return
            visited[node] = 1
            for neighbor in graph[node]:
                dfs(neighbor)
            visited[node] = 2
            order.append(node)

        for node in graph:
            if visited[node] == 0:
                dfs(node)
                if is_cyclic:
                    return None

        order.reverse()
        return order

    def start_topological_sort(self):
        if self.animating or not self.nodes:
            return
        self.disable_buttons()
        self.clear_order_labels()
        self.topological_button.config(bg="yellow", text="Topological Sort (running)")
        self.reset_colors()
        self.current_traversal_type = "Topological"
        order = self.topological_sort()
        if order is None:
            messagebox.showerror("Error", "Graph contains a cycle. Topological sort is not possible.")
            self.topological_button.config(bg=self.default_topological_button_color, text="Topological Sort")
            self.enable_buttons()
        else:
            self.animation_order = order
            self.current_animation_index = 0
            self.animating = True
            self.animate_next_node()

    def animate_next_node(self):
        if self.current_animation_index > 0:
            prev_node = self.animation_order[self.current_animation_index - 1]
            self.canvas.itemconfig(prev_node, fill="green")
            
        if self.current_animation_index < len(self.animation_order):
            current_node = self.animation_order[self.current_animation_index]
            if current_node not in self.nodes:
                self.animating = False
                self.enable_buttons()
                return
                
            self.canvas.itemconfig(current_node, fill="orange")
            
            x, y = self.nodes[current_node][0]
            if current_node in self.order_labels:
                self.canvas.delete(self.order_labels[current_node])
            label = self.canvas.create_text(
                x, y + 30,
                text=str(self.current_animation_index + 1),
                fill="black",
                font=("Arial", 12, "bold")
            )
            self.order_labels[current_node] = label
            
            self.current_animation_index += 1
            self.master.after(500, self.animate_next_node)
        else:
            self.animating = False
            self.enable_buttons()
            if self.current_traversal_type == "Topological":
                self.topological_button.config(
                    bg=self.default_topological_button_color,
                    text="Topological Sort"
                )
            self.current_traversal_type = None

    def clear_order_labels(self):
        for label in self.order_labels.values():
            self.canvas.delete(label)
        self.order_labels.clear()

    def disable_buttons(self):
        self.topological_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.topological_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)

    def reset_colors(self):
        for node in self.nodes:
            self.canvas.itemconfig(node, fill="blue")
        self.clear_order_labels()

    def clear_graph(self):
        self.clear_order_labels()
        for edge in list(self.edges.keys()):
            self.canvas.delete(edge)
        self.edges.clear()
        for node, (center, text) in list(self.nodes.items()):
            self.canvas.delete(text)
            self.canvas.delete(node)
        self.nodes.clear()
        self.number_node = 1


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Graph Topological Sort")
    app = GraphApp(root)
    root.mainloop()