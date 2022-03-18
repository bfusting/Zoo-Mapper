from tkinter import *
from PIL import Image,ImageTk

class Resizable:
    def __init__(self,label,image):
        self.label=label
        self.image=image
        self.label.master.bind('<Motion>',self.position)        
        self.flag=False 

    def position(self,event):
        #print("resizing")
        self.dimentions=(self.label.winfo_width(),self.label.winfo_height())
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

root=Tk()
root.geometry('400x300')

img_label=Label(bd=0)
img_label.pack()
image=Image.open('enclosure.jpg')
photoimage=ImageTk.PhotoImage(image.resize((100,100),Image.ANTIALIAS))
img_label.config(image=photoimage)
Resizable(img_label,image)

root.mainloop()