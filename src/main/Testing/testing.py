from tkinter import *
from PIL import Image,ImageTk

class Resizable:
    def __init__(self, resized_canvas, image, photoimage, canvas_image):
        '''self.resized_canvas=resized_canvas
        self.image=image
        self.resized_canvas.master.bind('<Motion>',self.position)        
        self.flag=False '''
        self.resized_canvas = resized_canvas
        self.image = image
        self.photoimage = photoimage
        self.flag = False
        self.canvas_image = canvas_image
        self.resized_canvas.master.bind('<Motion>', self.position)

    def position(self,event):
        #print("resizing")
        self.dimensions=(self.resized_canvas.winfo_width(),self.resized_canvas.winfo_height())
        self.x,self.y = event.x,event.y
        self.coordinates = (int(self.dimensions[0] + self.resized_canvas.coords(self.canvas_image)[0]), 
            int(self.dimensions[1] + self.resized_canvas.coords(self.canvas_image)[1])) #bottom right corner of image is location + 1/2 widths
        #print('coordinates:', self.coordinates)
        #print('event coordinates', self.x, self.y)
        # TODO - ADD CLAUSES FOR EACH CORNER OF THE IMAGE
        if (
            #self.x in range (self.dimensions[0]-10,self.dimensions[0] + 10,1) and 
            #self.y in range (self.dimensions[1]-10,self.dimensions[1] + 10,1)
            self.x in range(self.coordinates[0] - 10, self.coordinates[0] + 10, 1) and
            self.y in range(self.coordinates[1] - 10, self.coordinates[1] + 10, 1)
        ):
            #print('in range')
            self.resized_canvas.config(cursor='sizing')
            self.resized_canvas.master.bind('<ButtonRelease-1>',self.end)
            self.resized_canvas.bind('<Button-1>',self.start)
        #else:
            #self.resized_canvas.config(cursor='')    
            #self.resized_canvas.unbind('<Button-1>')

    def end(self,event):
        self.flag=True
        self.resized_canvas.master.unbind('<ButtonRelease-1>')
        #print('ended')

    def start(self,event):
        self.flag=False
        self.resize()

    def resize(self):
        #print('resizing')
        if not self.flag:
            self.resized_canvas.config(cursor='sizing')
            try:
                self.photoimage=ImageTk.PhotoImage(self.image.resize((self.x,self.y),Image.ANTIALIAS))
            except:
                pass
            #self.resized_canvas.config(image=self.photoimage)
            #self.resized_canvas.config(width=self.x, height=self.y)
            #self.resized_canvas.create_image(self.x, self.y, image=photoimage, anchor=NW)
            self.resized_canvas.itemconfig(canvas_image, image=self.photoimage)
            self.resized_canvas.config(width=self.x, height=self.y)
            self.resized_canvas.update()
            self.resized_canvas.after(1,self.resize)

root=Tk()
root.geometry('600x600')

#img_label=Label(bd=0)
#img_label.pack()
image=Image.open('C:\\Users\\colli\\Code\\ZooMapper\\Zoo-Mapper\\src\main\\enclosure.jpg')
photoimage=ImageTk.PhotoImage(image.resize((300,300),Image.ANTIALIAS))
canvas = Canvas(root, width=photoimage.width(), height=photoimage.height())
canvas.pack()
canvas_image = canvas.create_image(0, 0, image=photoimage, anchor=NW)

#img_label.config(image=photoimage)

Resizable(resized_canvas=canvas, image=image, photoimage=photoimage, canvas_image = canvas_image)

root.mainloop()
