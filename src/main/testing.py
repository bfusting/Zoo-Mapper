# Import the required libraries
from tkinter import *
from PIL import Image, ImageTk
from cv2 import resize
from matplotlib.pyplot import text


class Resizable:
    def __init__(self,canvas,image):
        self.canvas=canvas
        self.image=image
        self.canvas.master.bind('<Motion>',self.position)        
        self.flag=False 

    def position(self,event):
        #print("resizing")
        self.dimentions=(self.canvas.winfo_width(),self.canvas.winfo_height())
        self.x,self.y = event.x,event.y
        if (
            self.x in range (self.dimentions[0]-10,self.dimentions[0] + 10,1) and 
            self.y in range (self.dimentions[1]-10,self.dimentions[1] + 10,1)
        ):
            self.label.config(cursor='sizing')
            self.label.master.bind('<ButtonRelease-1>',self.end)
            self.label.bind('<Button-1>',self.start)
        else:
            self.label.config(cursor='')    
            self.label.unbind('<Button-1>')

    def end(self,event):
        self.flag=True
        self.label.master.unbind('<ButtonRelease-1>')

    def start(self,event):
        self.flag=False
        self.resize()

    def resize(self):
        if not self.flag:
            self.label.config(cursor='sizing')
            try:
                self.photoimage=ImageTk.PhotoImage(self.image.resize((self.x,self.y),Image.ANTIALIAS))
            except:
                pass
            self.label.config(image=self.photoimage)
            self.label.update()
            self.label.after(1,self.resize)
            self.canvas.create_image()

class Move:
   def __init__(self, canvas) -> None:
       canvas.bind("<B1-Motion>", Move.move)

   def left(e):
      x = -20
      y = 0
      canvas.move(img, x, y)

   def right(e):
      x = 20
      y = 0
      canvas.move(img, x, y)

   def up(e):
      x = 0
      y = -20
      canvas.move(img, x, y)

   def down(e):
      x = 0
      y = 20
      canvas.move(img, x, y)

   # Define a function to allow the image to move within the canvas
   def move(e):
      global image
      image = ImageTk.PhotoImage(Image.open("C:\\Users\\colli\\Code\\ZooMapper\\Zoo-Mapper\\src\main\\enclosure.jpg"))
      img = canvas.create_image(e.x, e.y, image=image)


# Create an instance of tkinter frame
win = Tk()

# Set the size of the tkinter window
win.geometry("700x350")

# Define a Canvas widget
canvas = Canvas(win, width=600, height=400, bg="white")
canvas.pack(pady=20)

# Add Images to Canvas widget
image = ImageTk.PhotoImage(Image.open("C:\\Users\\colli\\Code\\ZooMapper\\Zoo-Mapper\\src\main\\enclosure.jpg"))
img = canvas.create_image(250, 120, anchor=NW, image=image)


# Bind the move function
#canvas.bind("<B1-Motion>", Move.move)
Move(canvas)

win.mainloop()