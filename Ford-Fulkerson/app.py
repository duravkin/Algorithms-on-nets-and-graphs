import tkinter as tk
from tkinter import simpledialog, messagebox
from collections import deque, defaultdict


class GraphApp:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, bg='white', width=600, height=400)
        self.canvas.pack()

        self.Radius = 15
        self.nodes = {}  # {node_id: ( (x, y), text_id )}
        self.number_node = 1
        self.edges = {}  # {edge_id: {'from': node_id, 'to': node_id, 'capacity': int, 'flow': int, 'text_id': text_id}}
        self.selected_node = None
        self.mode = 'N'
        self.start_coords = (None, None)
        self.line = None
        self.animating = False
        self.source = None
        self.sink = None

        # Цвета состояний
        self.colors = {
            'default': 'blue',
            'source': '#008000',
            'sink': '#800000',
            'active_edge': '#008b8b',
            'final_edge': '#0000ff'
        }

        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.move_mouse)
        self.canvas.bind("<ButtonRelease-1>", self.release_mouse)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Double-Button-1>", self.double_click)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.max_flow_button = tk.Button(
            self.button_frame, text="Max Flow", command=self.init_max_flow)
        self.max_flow_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.reset_button = tk.Button(
            self.button_frame, text="Reset Colors", command=self.reset_colors)
        self.reset_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.clear_button = tk.Button(
            self.button_frame, text="Clear Graph", command=self.clear_graph)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.default_button_color = self.max_flow_button.cget("bg")
        self.animation_steps = []
        self.current_animation_step = 0
        self.current_path_edges = []
        self.selection_phase = None  # 'source_selection', 'sink_selection'

    def check_node(self, x, y):
        overlapping = self.canvas.find_overlapping(
            x - 5, y - 5, x + 5, y + 5)
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
            
        if self.selection_phase:
            self.handle_selection(event.x, event.y)
            return

        x, y = event.x, event.y
        self.mode = 'N'
        self.add_node(x, y)

    def handle_selection(self, x, y):
        node = self.check_node(x, y)
        if node is None:
            return

        if self.selection_phase == 'source_selection':
            self.select_source(node)
        elif self.selection_phase == 'sink_selection':
            self.select_sink(node)

    def select_source(self, node):
        if self.source:
            self.canvas.itemconfig(self.source, fill=self.colors['default'])
        self.source = node
        self.canvas.itemconfig(node, fill=self.colors['source'])
        self.selection_phase = 'sink_selection'
        self.max_flow_button.config(bg="yellow", text="Click on sink node")
        # messagebox.showinfo("Select Sink", "Click on sink node")

    def select_sink(self, node):
        if node == self.source:
            messagebox.showerror("Error", "Sink cannot be same as source")
            return
        if self.sink:
            self.canvas.itemconfig(self.sink, fill=self.colors['default'])
        self.sink = node
        self.canvas.itemconfig(node, fill=self.colors['sink'])
        self.selection_phase = None
        self.prepare_max_flow_animation()

    def move_mouse(self, event):
        if self.animating or self.selection_phase:
            return
        x, y = event.x, event.y
        if self.mode == 'N':
            self.move_node(x, y)
        elif self.mode == 'E':
            self.add_edge(x, y)

    def release_mouse(self, event):
        if self.animating or self.selection_phase:
            return
        x, y = event.x, event.y
        if self.mode == 'E':
            target = self.check_node(x, y)
            if target is not None and target != self.selected_node:
                target_center = self.nodes[target][0]
                self.canvas.coords(self.line, self.start_coords[0], self.start_coords[1],
                                   target_center[0], target_center[1])
                
                capacity = simpledialog.askinteger(
                    "Capacity", "Enter edge capacity:",
                    parent=self.master, 
                    minvalue=0, 
                    initialvalue=1
                )
                
                if capacity is None:
                    self.canvas.delete(self.line)
                    self.mode = 'N'
                    self.selected_node = None
                    self.line = None
                    return
                
                text_x = (self.start_coords[0] + target_center[0]) // 2
                text_y = (self.start_coords[1] + target_center[1]) // 2
                text_id = self.canvas.create_text(
                    text_x, text_y,
                    text=f"0/{capacity}",
                    fill="black",
                    font=("Arial", 10))
                
                self.edges[self.line] = {
                    'from': self.selected_node,
                    'to': target,
                    'capacity': capacity,
                    'flow': 0,
                    'text_id': text_id
                }
                self.canvas.itemconfig(self.line, arrow=tk.LAST, fill="black")
            else:
                if self.line is not None:
                    self.canvas.delete(self.line)
            
            self.mode = 'N'
            self.selected_node = None
            self.line = None

    def right_click(self, event):
        if self.animating or self.selection_phase:
            return
        x, y = event.x, event.y
        self.delete_node(x, y)

    def double_click(self, event):
        if self.animating or self.selection_phase:
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
                x - R, y - R, x + R, y + R, fill=self.colors['default'])
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
            self.nodes[self.selected_node] = (
                (x, y), self.nodes[self.selected_node][1])
            for edge, edge_info in self.edges.items():
                if edge_info['from'] == self.selected_node or edge_info['to'] == self.selected_node:
                    x1, y1 = self.nodes[edge_info['from']][0]
                    x2, y2 = self.nodes[edge_info['to']][0]
                    self.canvas.coords(edge, x1, y1, x2, y2)
                    self.canvas.coords(edge_info['text_id'], (x1+x2)//2, (y1+y2)//2)

    def delete_node(self, x, y):
        node = self.check_node(x, y)
        if node in self.nodes:
            edges_to_delete = []
            for edge, edge_info in list(self.edges.items()):
                if edge_info['from'] == node or edge_info['to'] == node:
                    self.canvas.delete(edge_info['text_id'])
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

    def init_max_flow(self):
        if self.animating or not self.nodes:
            return

        self.reset_colors()
        self.selection_phase = 'source_selection'
        self.max_flow_button.config(state=tk.DISABLED)
        self.max_flow_button.config(bg="yellow", text="Click on source node")
        # messagebox.showinfo("Select Source", "Click on source node")

    def prepare_max_flow_animation(self):
        edges_data = []
        node_ids = list(self.nodes.keys())
        for edge_info in self.edges.values():
            edges_data.append({
                'from': edge_info['from'],
                'to': edge_info['to'],
                'capacity': edge_info['capacity'],
                'flow': 0
            })
            edges_data.append({
                'from': edge_info['to'],
                'to': edge_info['from'],
                'capacity': 0,
                'flow': 0
            })

        parent = {}
        max_flow = 0
        residual = defaultdict(dict)
        for edge in edges_data:
            u = edge['from']
            v = edge['to']
            residual[u][v] = edge['capacity'] - edge['flow']

        self.animation_steps = []
        while True:
            queue = deque()
            queue.append(self.source)
            parent = {node: None for node in node_ids}
            parent[self.source] = -1

            found = False
            while queue and not found:
                u = queue.popleft()
                for v in residual[u]:
                    if parent[v] is None and residual[u][v] > 0:
                        parent[v] = u
                        if v == self.sink:
                            found = True
                            break
                        queue.append(v)

            if not found:
                break

            path_flow = float('inf')
            v = self.sink
            path = []
            while v != self.source:
                u = parent[v]
                path_flow = min(path_flow, residual[u][v])
                path.insert(0, (u, v))
                v = u

            self.animation_steps.append(('path', path.copy(), path_flow))

            v = self.sink
            while v != self.source:
                u = parent[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow

                forward_edge = None
                backward_edge = None
                for edge_id, edge_info in self.edges.items():
                    if edge_info['from'] == u and edge_info['to'] == v:
                        forward_edge = edge_id
                    if edge_info['from'] == v and edge_info['to'] == u:
                        backward_edge = edge_id

                if forward_edge is not None:
                    new_flow = self.edges[forward_edge]['flow'] + path_flow
                    self.animation_steps.append(('update', forward_edge, new_flow))
                elif backward_edge is not None:
                    new_flow = self.edges[backward_edge]['flow'] - path_flow
                    self.animation_steps.append(('update', backward_edge, new_flow))

                v = u

            max_flow += path_flow

        self.animation_steps.append(('done', max_flow))
        self.current_animation_step = 0
        self.animating = True
        self.disable_buttons()
        self.max_flow_button.config(bg="yellow", text="Running...")
        self.animate_max_flow_step()

    def animate_max_flow_step(self):
        if self.current_animation_step >= len(self.animation_steps):
            self.animating = False
            self.max_flow_button.config(bg=self.default_button_color, text="Max Flow")
            self.enable_buttons()
            self.finalize_animation()
            return

        step = self.animation_steps[self.current_animation_step]
        if step[0] == 'path':
            for u, v in step[1]:
                self.highlight_edge(u, v)
            self.current_path_edges = step[1]
            self.current_animation_step += 1
            self.master.after(1500, self.animate_max_flow_step)
        elif step[0] == 'update':
            edge_id = step[1]
            new_flow = step[2]
            self.edges[edge_id]['flow'] = new_flow
            capacity = self.edges[edge_id]['capacity']
            self.canvas.itemconfig(self.edges[edge_id]['text_id'], 
                                 text=f"{new_flow}/{capacity}")
            self.current_animation_step += 1
            self.master.after(500, self.animate_max_flow_step)
        elif step[0] == 'done':
            messagebox.showinfo("Max Flow", f"Maximum flow: {step[1]}")
            self.animating = False
            self.max_flow_button.config(bg=self.default_button_color, text="Max Flow")
            self.enable_buttons()

    def finalize_animation(self):
        for edge_id, edge_info in self.edges.items():
            if edge_info['flow'] > 0:
                self.canvas.itemconfig(edge_id, fill=self.colors['final_edge'], width=2)

    def highlight_edge(self, u, v):
        for edge_id, edge_info in self.edges.items():
            if edge_info['from'] == u and edge_info['to'] == v:
                self.canvas.itemconfig(edge_id, fill=self.colors['active_edge'], width=2)
            elif edge_info['from'] == v and edge_info['to'] == u:
                self.canvas.itemconfig(edge_id, fill="#ff6666", width=2)

    def reset_colors(self):
        for node in self.nodes:
            self.canvas.itemconfig(node, fill=self.colors['default'])
        
        for edge_id, edge_info in self.edges.items():
            self.canvas.itemconfig(edge_id, fill="black", width=1)
            edge_info['flow'] = 0
            self.canvas.itemconfig(edge_info['text_id'], 
                                 text=f"0/{edge_info['capacity']}")
        
        if self.source:
            self.canvas.itemconfig(self.source, fill=self.colors['default'])
        if self.sink:
            self.canvas.itemconfig(self.sink, fill=self.colors['default'])
        self.source = None
        self.sink = None

    def disable_buttons(self):
        self.max_flow_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.max_flow_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)

    def clear_graph(self):
        self.reset_colors()
        for edge in list(self.edges.keys()):
            self.canvas.delete(self.edges[edge]['text_id'])
            self.canvas.delete(edge)
        self.edges.clear()
        for node, (center, text) in list(self.nodes.items()):
            self.canvas.delete(text)
            self.canvas.delete(node)
        self.nodes.clear()
        self.number_node = 1
        self.source = None
        self.sink = None


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Max Flow Finder")
    app = GraphApp(root)
    root.mainloop()