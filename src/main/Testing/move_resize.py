# Import the required libraries
from tkinter import *
from PIL import Image, ImageTk
from numpy import inner

class Resizable:
    def __init__(self, inner_canvas, photoImage, canvas_image, raw_image):
        self.inner_canvas=inner_canvas
        self.photoImage=photoImage
        self.canvas_image = canvas_image
        self.raw_image = raw_image
        self.inner_canvas.master.bind('<Motion>',self.position)        
        self.flag=False


    def position(self,event):
        #print("position")
        self.dimensions=(self.inner_canvas.winfo_width(),self.inner_canvas.winfo_height())
        self.coordinates = (int(self.dimensions[0] + self.inner_canvas.coords(self.canvas_image)[0]), int(self.dimensions[1] + self.inner_canvas.coords(self.canvas_image)[1])) #bottom right corner of image is location + 1/2 widths
        #print('dimensions width, height: ', self.canvas.winfo_width(), self.canvas.winfo_height())
        #print('canvas location = ', canvas.coords(self.canvas_image))
        #print('pic coords:', self.coordinates[0], self.coordinates[1])
        self.x,self.y = event.x,event.y
        #print('event coords:', self.x, self.y)
        if (
            #self.x in range (self.dimensions[0]-10,self.dimensions[0] + 10,1) and 
            #self.y in range (self.dimensions[1]-10,self.dimensions[1] + 10,1)
            self.x in range(self.coordinates[0] - 100, self.coordinates[1] + 100, 1) and
            self.y in range(self.coordinates[1] - 10, self.coordinates[1] + 100, 1)
        ):
            print("in range")
            self.inner_canvas.config(cursor='sizing')
            self.inner_canvas.master.bind('<ButtonRelease-1>',self.end)
            self.inner_canvas.bind('<Button-1>',self.start)
        else:
            self.inner_canvas.config(cursor='')    
            self.inner_canvas.unbind('<Button-1>')

    def end(self,event):
        self.flag=True
        self.inner_canvas.master.unbind('<ButtonRelease-1>')

    def start(self,event):
        self.flag=False
        self.resize()

    def resize(self):
        if not self.flag:
            self.inner_canvas.config(cursor='sizing')
            try:
                #self.photoimage=ImageTk.PhotoImage(self.image.resize((self.x,self.y),Image.ANTIALIAS))
                self.photoImage=ImageTk.PhotoImage(self.raw_image.resize((self.x, self.y), Image.ANTIALIAS))
            except:
                pass
            self.inner_canvas.config(image=photoImage) # MUST BE CHANGED TO APPROPRIATELY RESIZE IMG
            self.inner_canvas.update()
            self.inner_canvas.after(1, self.resize)

win = Tk()
win.geometry('800x600')

canvas = Canvas(win, width=600, height=400, bg="white")
image = Image.open("C:\\Users\\colli\\Code\\ZooMapper\\Zoo-Mapper\\src\main\\enclosure.jpg")
photoImage = ImageTk.PhotoImage(Image.open("C:\\Users\\colli\\Code\\ZooMapper\\Zoo-Mapper\\src\main\\enclosure.jpg"))
innerCanvas = Canvas(width=photoImage.width(), height=photoImage.height())
canvas.create_window(50, 25, anchor=NW, window=innerCanvas)
canvas_img = innerCanvas.create_image(0, 0, anchor=NW, image=photoImage)


canvas.create_window(50, 25, anchor=NW, window=innerCanvas)
canvas.pack(pady=20)

#Resizableimage, canvas_image=canvas_img)
Resizable(inner_canvas=innerCanvas, photoImage=photoImage, canvas_image=canvas_img, raw_image=image)


win.mainloop()