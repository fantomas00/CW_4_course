import tkinter as tk
from tkinter import ttk
import node


def placeholder():
    return False


global node_count


class SelectNode:
    def __init__(self, window, canvas, s_node):
        self.node = s_node
        self.canvas = canvas

        self.node_window = tk.Toplevel(window)
        self.node_window.wm_title("Node Information: Node {}".format(self.node.id))
        self.node_window.iconbitmap("icon/node.ico")

        neighbor_title = tk.Label(self.node_window, text="NEIGHBOR TABLE", width=20)
        neighbor_title.grid(row=0, column=0, stick="nsew")
        self.neighbor_tree = ttk.Treeview(self.node_window, height=10, columns="Node", show="headings")
        self.neighbor_tree.grid(row=1, column=0, stick="nsew")

        self.distance_title = tk.Label(self.node_window, text="DISTANCE TABLE", width=30)
        self.distance_title.grid(row=0, column=1, stick="nsew")
        self.distance_tree = ttk.Treeview(self.node_window, height=10, columns=("Node", "Distance"), show="headings")
        self.distance_tree.grid(row=1, column=1, stick="nsew")

        self.neighbor_tree.heading("Node", text="Node")
        self.neighbor_tree.column("Node", width=5, anchor="center")
        for entry in self.node.get_connected_nodes():
            self.neighbor_tree.insert("", "end", values=entry)

        self.distance_tree.heading("Node", text="Node")
        self.distance_tree.column("Node", width=5, anchor="center")
        self.distance_tree.heading("Distance", text="Distance")
        self.distance_tree.column("Distance", width=100, anchor="center")
        self.reload_distance_table()

        label = tk.Label(self.node_window, text="ACTIONS", width=40)
        label.grid(row=0, column=2, stick="nsew")

        self.menu_frame = tk.Frame(self.node_window)
        self.reload_menu()

    def reload_distance_table(self):
        self.distance_tree.delete(*self.distance_tree.get_children())
        for entry in list(self.node.get_distance_table()):
            if entry[1] == float("inf"):
                entry[1] = "NOT CALCULATED"
            self.distance_tree.insert("", "end", values=entry)

    def reload_menu(self):
        self.menu_frame.destroy()
        self.menu_frame.__init__(self.node_window)
        self.menu_frame.grid(row=1, column=2, stick="nsew")
        self.menu_frame.rowconfigure(3, weight=1)
        self.menu_frame.columnconfigure(0, weight=1)
        if self.node.enabled:
            dist_calc_button = tk.Button(self.menu_frame, text="Calculate Node Distances", command=self.calc_distance)
            dist_calc_button.grid(row=0, column=0, stick="nsew")

            disable_button = tk.Button(self.menu_frame, text="Disable Node", command=self.disable_node, anchor="center")
            disable_button.grid(row=1, column=0, stick="nsew")

            if self.node.station:
                send_button = tk.Button(self.menu_frame, text="Send Message",
                                        command=self.send_message, anchor="center")
                send_button.grid(row=2, column=0, stick="nsew")
        else:
            enable_button = tk.Button(self.menu_frame, text="Enable Node", command=self.enable_node, anchor="center")
            enable_button.grid(row=0, column=0, stick="nsew")

    def disable_node(self):
        self.node.enabled = False
        self.canvas.itemconfig(self.node.shape, fill="darkrblue")
        self.reload_menu()

    def enable_node(self):
        self.node.enabled = True
        self.canvas.itemconfig(self.node.shape, fill="lightyellow")
        self.reload_menu()

    def calc_distance(self):
        self.node.dijkstra()
        self.reload_distance_table()

    def send_message(self):
        return True


class SelectChannel:
    def __init__(self, window, canvas, channel, channel_shape):
        self.channel = channel
        self.shape = channel_shape
        self.canvas = canvas

        self.chnl_window = tk.Toplevel(window)
        self.chnl_window.wm_title("Channel Information")
        self.chnl_window.iconbitmap("icon/node.ico")

        neighbor_title = tk.Label(self.chnl_window, text="CONNECTED NODES", width=20)
        neighbor_title.grid(row=0, column=0, stick="nsew")
        self.nodes = tk.Label(self.chnl_window, text="{} {}".format(channel.node1, channel.node2), width=20)
        self.nodes.grid(row=1, column=0, stick="nsew")

        label = tk.Label(self.chnl_window, text="ACTIONS", width=40)
        label.grid(row=0, column=1, stick="nsew")

        self.menu_frame = tk.Frame(self.chnl_window)
        self.reload_menu()

    def reload_menu(self):
        self.menu_frame.destroy()
        self.menu_frame.__init__(self.chnl_window)
        self.menu_frame.grid(row=1, column=1, stick="nsew")
        self.menu_frame.rowconfigure(2, weight=1)
        self.menu_frame.columnconfigure(0, weight=1)
        if self.channel.enabled:

            disable_button = tk.Button(self.menu_frame, text="Disable Channel", command=self.disable_chnl,
                                       anchor="center")
            disable_button.grid(row=1, column=0, stick="nsew")
        else:
            enable_button = tk.Button(self.menu_frame, text="Enable Channel", command=self.enable_chnl,
                                      anchor="center")
            enable_button.grid(row=0, column=0, stick="nsew")

    def disable_chnl(self):
        self.channel.enabled = False
        self.canvas.itemconfig(self.shape, fill="darkblue")
        self.reload_menu()

    def enable_chnl(self):
        self.channel.enabled = True
        self.canvas.itemconfig(self.shape, fill="black")
        self.reload_menu()


# noinspection PyTypeChecker
class Main:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Coursework")
        self.window.state("zoomed")
        self.window.geometry("{}x{}".format(self.window.winfo_screenwidth(), self.window.winfo_screenheight()))
        self.window.iconbitmap("icon/inet.ico")

        self.canvas = tk.Canvas(self.window, bg="grey")
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.channel_mode = tk.StringVar()
        self.channel_mode.set("duplex")
        self.generation_mode = tk.BooleanVar()
        self.generation_mode.set(True)
        self.station_mode = tk.BooleanVar()
        self.station_mode.set(False)

        self.menu_bar = tk.Menu(self.window)
        self.node_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.node_menu.add_command(label="New Node", command=self.add_node_mode)
        self.node_menu.add_command(label="Remove Node", command=self.remove_node_mode)
        self.node_menu.add_checkbutton(label="Station",
                                       onvalue=1,
                                       offvalue=0,
                                       variable=self.station_mode)
        self.node_menu.add_separator()
        self.node_menu.add_command(label="Create Channel", command=self.add_channel_mode)
        self.node_menu.add_command(label="Remove Channel", command=self.remove_channel_mode)
        self.node_menu.add_separator()
        self.node_menu.add_checkbutton(label="Duplex",
                                       onvalue="duplex",
                                       offvalue="half-duplex",
                                       variable=self.channel_mode)
        self.node_menu.add_checkbutton(label="Half-Duplex",
                                       onvalue="half-duplex",
                                       offvalue="duplex",
                                       variable=self.channel_mode)
        self.node_menu.add_separator()
        self.node_menu.add_checkbutton(label="Set Channel Costs",
                                       onvalue=True,
                                       offvalue=False,
                                       variable=self.generation_mode)
        self.node_menu.add_checkbutton(label="Random Channel Costs",
                                       onvalue=False,
                                       offvalue=True,
                                       variable=self.generation_mode)
        self.menu_bar.add_cascade(label="Create", menu=self.node_menu)

        self.search_mode = tk.BooleanVar()
        self.search_mode.set(True)

        self.search_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.search_menu.add_checkbutton(label="Shortest Path",
                                         onvalue=True,
                                         offvalue=False,
                                         variable=self.search_mode)
        self.search_menu.add_checkbutton(label="Least Nodes",
                                         onvalue=False,
                                         offvalue=True,
                                         variable=self.search_mode)
        self.menu_bar.add_cascade(label="Search", menu=self.search_menu)

        self.transmission_mode = tk.BooleanVar()
        self.transmission_mode.set(True)

        self.transmission_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.transmission_menu.add_checkbutton(label="Virtual Channel",
                                               onvalue=True,
                                               offvalue=False,
                                               variable=self.transmission_mode)
        self.transmission_menu.add_checkbutton(label="Datagram",
                                               onvalue=False,
                                               offvalue=True,
                                               variable=self.transmission_mode)
        self.menu_bar.add_cascade(label="Transmission", menu=self.transmission_menu)

        self.window.config(menu=self.menu_bar)

        self.node_list = {}
        self.channel_list = {}
        self.faux_node = None
        self.channel_line = None
        self.start_coords = None
        global node_count
        node_count = 0
        self.first_node_selected = None

        self.canvas.bind("<Double-Button-1>", self.select)

        self.window.mainloop()

    def add_node_mode(self):
        self.unbind()
        self.faux_node = self.canvas.create_oval(0, 0, 20, 20, fill="lightyellow", outline="black", width=1)
        self.canvas.bind("<Button-1>", self.add_node)
        self.canvas.bind("<Motion>", self.cursor_node_display)

    def cursor_node_display(self, event):
        shp_coords = self.canvas.coords(self.faux_node)
        self.canvas.move(self.faux_node, event.x-shp_coords[0]-10, event.y-shp_coords[1]-10)

    def add_node(self, event):
        global node_count
        r = 20
        x1 = event.x-r
        y1 = event.y-r
        x2 = event.x+r
        y2 = event.y+r
        node_text = self.canvas.create_text(event.x, event.y - 30,
                                            fill="black", font=("Courier", 15, "bold"), text=node_count)
        if self.station_mode.get():
            node_shape = self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightyellow", outline="black", width=1)
            new_node = node.Node(node_shape, node_text, node_count, event.x, event.y, station=True)
        else:
            node_shape = self.canvas.create_oval(x1, y1, x2, y2, fill="lightyellow", outline="black", width=1)
            new_node = node.Node(node_shape, node_text, node_count, event.x, event.y)
        self.node_list[node_count] = new_node
        self.canvas.delete(self.faux_node)
        self.unbind()
        node_count += 1

    def remove_node_mode(self):
        self.unbind()
        self.canvas.bind("<Button-1>", self.remove_node)

    def remove_node(self, event):
        select_list = self.canvas.find_withtag("current")
        if select_list:
            select_id = select_list[0]
            for k, v in list(self.node_list.items()):
                if select_id == v.shape or select_id == v.text:
                    for channel in self.node_list[k].get_channels():
                        for shp, obj in list(self.channel_list.items()):
                            if obj == channel:
                                self.canvas.delete(shp)
                    self.node_list[k].remove()
                    self.canvas.delete(v.shape)
                    self.canvas.delete(v.text)
                    self.unbind()

    def add_channel_mode(self):
        self.unbind()
        self.canvas.bind("<Button-1>", self.add_channel)

    def cursor_channel_display(self, event):
        line_coords = self.canvas.coords(self.channel_line)
        self.canvas.coords(self.channel_line,
                           line_coords[0],
                           line_coords[1],
                           line_coords[2],
                           line_coords[3],
                           line_coords[0],
                           line_coords[1],
                           event.x,
                           event.y)

    def add_channel(self, event):
        select_list = self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
        if select_list:
            select_id = select_list[0]
            for k, v in list(self.node_list.items()):
                if select_id == v.shape or select_id == v.text:
                    if not self.first_node_selected:
                        self.canvas.bind("<Motion>", self.cursor_channel_display)
                        if self.channel_mode.get() == "duplex":
                            self.channel_line = self.canvas.create_line(v.x, v.y,
                                                                        event.x, event.y, fill="black", width=5)
                        else:
                            self.channel_line = self.canvas.create_line(v.x, v.y,
                                                                        event.x, event.y, fill="black", width=5,
                                                                        dash=(5, 1))
                        self.first_node_selected = v
                    elif self.first_node_selected != v:
                        line_coords = self.canvas.coords(self.channel_line)
                        new_line = self.canvas.create_line(line_coords[0], line_coords[1], v.x, v.y,
                                                           fill="black", width=5,
                                                           dash=self.canvas.itemcget(self.channel_line, "dash"),
                                                           tags="channel")
                        new_channel = node.Channel(self.first_node_selected, v, self.channel_mode.get(),
                                                   self.channel_mode.get(), 0, False)
                        v.connect(self.first_node_selected, self.channel_mode.get(), new_channel)
                        self.channel_list[new_line] = new_channel
                        self.unbind()
                        self.first_node_selected = False

    def remove_channel_mode(self):
        self.unbind()
        self.canvas.bind("<Button-1>", self.remove_channel)

    def remove_channel(self, event):
        select_list = self.canvas.find_withtag("current")
        if select_list:
            select_id = select_list[0]
            if select_id in self.channel_list:
                channel = self.channel_list[select_id]
                self.node_list[channel.node1].disconnect(self.node_list[channel.node2])
                self.canvas.delete(select_id)
                del self.channel_list[select_id]

    def select(self, event):
        select_list = self.canvas.find_withtag("current")
        if select_list:
            select_id = select_list[0]
            if select_id in self.channel_list:
                select = SelectChannel(self.window, self.canvas, self.channel_list[select_id], select_id)
            for k, v in list(self.node_list.items()):
                if select_id == v.shape:
                    select = SelectNode(self.window, self.canvas, v)

    def unbind(self):
        for event in self.canvas.bind():
            if event != "<Double-Button-1>" and event != "<B1-Motion>":
                self.canvas.unbind(event)
        if self.faux_node:
            self.canvas.delete(self.faux_node)
            self.faux_node = None
        if self.channel_line:
            self.canvas.delete(self.channel_line)
            self.channel_line = None


if __name__ == '__main__':
    Main()
