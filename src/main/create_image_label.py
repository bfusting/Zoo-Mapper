from tkinter import Canvas, Menu
from functools import partial
from PIL import Image, ImageTk
import tkinter as tk


class DrawLabelImage(Canvas):
    '''A resizable, removable canvas'''

    def __init__(self, master=None, cnf={}, **kw):
        Canvas.__init__(self, master, cnf, **kw)
        self.config(bd=0, highlightthickness=0)
        self.is_sizing = False
        self.old_width = 0
        self.old_height = 0
        self.old_pos_x = 0
        self.old_pos_y = 0
        self.start_x = 0
        self.start_y = 0
        self.start_root_x = 0
        self.start_root_y = 0
        self.on_resize_complete = None
        self.have_child = False  # To identify whether a component has been created

    def _mousedown(self, event):
        self.startx = event.x
        self.starty = event.y

    def _drag(self, event):
        try:
            self.place(x=self.winfo_x() + (event.x - self.startx), y=self.winfo_y() + (event.y - self.starty))
        except AttributeError:
            raise ValueError("The widget %s is not draggable" % self.widget)

    def set_on_resize_complete(self, on_resize_complete):
        self.on_resize_complete = on_resize_complete

    def on_update(self):
        self.create_rectangle(-1, -1, -2, -2, tag='side', dash=3, outline='grey')
        self.tag_bind('side', "<Button-1>", self._mousedown, add='+')
        self.tag_bind('side', "<B1-Motion>", self._drag, add='+')
        self.tag_bind('side', '<Enter>', lambda event: self.config(cursor='fleur'))
        self.tag_bind('side', '<Leave>', lambda event: self.config(cursor='arrow'))
        for name in ('nw', 'w', 'sw', 'n', 's', 'ne', 'e', 'se'):
            self.create_rectangle(-1, -1, -2, -2, tag=name, outline='blue')
            self.tag_bind(name, "<Enter>", partial(self.on_mouse_enter, name))
            self.tag_bind(name, "<Leave>", partial(self.on_mouse_leave, name))
            self.tag_bind(name, "<Button-1>", partial(self.on_mouse_click, name))
            self.tag_bind(name, "<B1-Motion>", partial(self.on_mouse_move, name))
            self.tag_bind(name, "<ButtonRelease-1>", partial(self.on_mouse_release, name))

    def show(self, is_fill=False):
        # print(self.is_sizing)
        width = self.winfo_width()
        height = self.winfo_height()
        self.coords('side', 6, 6, width - 6, height - 6)
        self.coords('nw', 0, 0, 7, 7)
        self.coords('sw', 0, height - 8, 7, height - 1)
        self.coords('w', 0, (height - 7) / 2, 7, (height - 7) / 2 + 7)
        self.coords('n', (width - 7) / 2, 0, (width - 7) / 2 + 7, 7)
        self.coords('s', (width - 7) / 2, height - 8, (width - 7) / 2 + 7, height - 1)
        self.coords('ne', width - 8, 0, width - 1, 7)
        self.coords('se', width - 8, height - 8, width - 1, height - 1)
        self.coords('e', width - 8, (height - 7) / 2, width - 1, (height - 7) / 2 + 7)
        if is_fill:
            for name in ('nw', 'w', 'sw', 'n', 's', 'ne', 'e', 'se'):
                self.itemconfig(name, fill='blue')

        # self.unbind("<Button-1>")
        # self.unbind("<B1-Motion>")

    def hide(self):
        self.coords('side', -1, -1, -2, -2, )
        for name in ('nw', 'w', 'sw', 'n', 's', 'ne', 'e', 'se'):
            self.coords(name, -1, -1, -2, -2)

    def on_mouse_enter(self, tag_name, event):
        if tag_name in ("nw", "sw", "ne", "se"):
            self["cursor"] = "sizing"
        elif tag_name in ("w", "e"):
            self["cursor"] = "sb_h_double_arrow"
        else:
            self["cursor"] = "sb_v_double_arrow"

    def on_mouse_leave(self, tag_name, event):
        if self.is_sizing:
            return
        self["cursor"] = "arrow"

    def on_mouse_click(self, tag_name, event):
        self.is_sizing = True
        self.start_x = event.x
        self.start_y = event.y
        self.start_root_x = event.x_root
        self.start_root_y = event.y_root
        self.old_width = self.winfo_width()
        self.old_height = self.winfo_height()
        self.old_pos_x = int(self.place_info()['x'])
        self.old_pos_y = int(self.place_info()['y'])

        # self.unbind("<Button-1>")
        # self.unbind("<B1-Motion>")

    def on_mouse_move(self, tag_name, event):
        if not self.is_sizing:
            return
        # print(tag_name)
        # right
        if 'e' in tag_name:
            width = max(0, self.old_width + (event.x_root - self.start_root_x))
            self.place_configure(width=width, x=self.old_pos_x, y=self.old_pos_y)

        # left
        if 'w' in tag_name:
            width = max(0, self.old_width + (self.start_root_x - event.x_root))
            to_x = self.old_pos_x + event.x_root - self.start_root_x
            self.place_configure(width=width, x=to_x, y=self.old_pos_y)

        # bottom
        if 's' in tag_name:
            height = max(0, self.old_height + (event.y_root - self.start_root_y))
            self.place_configure(height=height, x=self.old_pos_x, y=self.old_pos_y)

        # top
        if 'n' in tag_name:
            height = max(0, self.old_height + (self.start_root_y - event.y_root))
            to_y = self.old_pos_y + event.y_root - self.start_root_y
            self.place_configure(height=height, y=to_y)

        self.update_label_image(is_first=True)
        self.after_idle(self.show)
        # self.update()

    def on_mouse_release(self, tag_name, event):
        self.is_sizing = False
        if self.on_resize_complete is not None:
            self.on_resize_complete()
        self["cursor"] = "arrow"

        # self.bind("<Button-1>", self.mousedown, add='+')
        # self.bind("<B1-Motion>", self.drag, add='+')

    def create_widget(self, widget_class, cnf={}, **kw):
        if self.have_child == True:  # If already create, ignore it
            return
        self.have_child = True
        self.widget = widget_class(self, cnf, **kw)
        self.widget.pack(fill='both', expand=True, pady=9, padx=9)
        # You can move components even if you drag them
        self.widget.bind("<Button-1>", self.mousedown, add='+')
        self.widget.bind("<B1-Motion>", self.drag, add='+')
        self.widget.bind('<FocusOut>', lambda event: self.delete('all'))
        self.widget.bind('<FocusIn>', lambda event: (self.on_update(), self.show()))

    def update_label_image(self, is_first=False, is_focusOut=False):
        # print(self.is_sizing)
        # print('update_label_image', is_first,is_focusOut)
        img = Image.open(self.background_file)
        img = img.resize((self.winfo_width() + 3, self.winfo_height() + 3))
        image = ImageTk.PhotoImage(img)
        self.background = image
        self.create_image(-1, -1, anchor=tk.NW, image=self.background)
        #
        # self.bind("<Button-1>", self.mousedown, add='+')
        # self.bind("<B1-Motion>", self.drag, add='+')
        # if not is_first:
        #     self.hide()
        #     self.show()

    def create_label_image(self, con):
        self.background_file = con
        self.update_label_image()
        self.menuBar = Menu(self,tearoff=0)
        self.menuBar.add_command(label='delete', command=lambda: self.destroy())
        self.bind("<Button-1>", self.mousedown, add='+')
        self.bind("<B1-Motion>", self.drag, add='+')
        self.bind('<Leave>',
                  lambda event: (self.delete('all'), self.update_label_image(is_first=True, is_focusOut=True)))
        # self.bind('<FocusOut>', lambda event: (self.delete('all'), self.update_label_image(is_first=True,is_focusOut=True)))
        self.bind('<Enter>', lambda event: (self.on_update(), self.show()))
        self.bind('<Button-3>', self.menubar)
        # self.bind('<FocusIn>', lambda event: (self.on_update(), self.show()))

    def menubar(self,event):
        self.menuBar.post(event.x_root,event.y_root)


    def mousedown(self, event):
        self.focus_set()
        self.__startx = event.x
        self.__starty = event.y

    def drag(self, event):
        if self.is_sizing:
            return
        # print('drag')
        self.place(x=self.winfo_x() + (event.x - self.__startx), y=self.winfo_y() + (event.y - self.__starty))
