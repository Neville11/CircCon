import math

class component(object):
    def __init__(self,cx,cy):
        self.cx,self.cy=cx,cy

class resistor(component):
    def draw(self,canvas):
        start=(self.cx-20,self.cy)
        numPoints=9
        dx,dy=5,10
        for i in range(0,numPoints):
            if i==0 or i==8:end=(start[0]+dx,start[1]+dy//2)
            elif i%2==1:end=(start[0]+dx,start[1]-dy)
            else:
                end=(start[0]+dx,start[1]+dy)
            canvas.create_line(start,end)
            start=end
            
class diode(component):
    def draw(self,canvas):
        size=20
        x1,y1=self.cx+size//2,self.cy
        x2,y2=x1-size,y1-size//2
        x3,y3=x2,y2+size
        canvas.create_polygon(x1,y1,x2,y2,x3,y3)
        canvas.create_line(x1,y1-size//2,x1,y1+size//2, width="2")
        
class transistor(component):
    def draw(self,canvas):
        r=15
        canvas.create_oval(self.cx-r,self.cy-r,self.cx+r,self.cy+r,fill="white",outline="black")
        lineStart=(self.cx-r//2,self.cy-r//2)
        lineEnd=(lineStart[0],lineStart[1]+r)
        port1=(self.cx+ r*math.cos((math.pi)-2*math.pi/3),self.cy+r*math.sin((math.pi)-2*math.pi/3))
        port2=(self.cx+ r*math.cos((math.pi)-4*math.pi/3),self.cy+r*math.sin((math.pi)-4*math.pi/3))
        port3=(self.cx+ r*math.cos((math.pi)-2*math.pi),self.cy+r*math.sin((math.pi)-2*math.pi))
        canvas.create_line(lineStart,lineEnd)
        canvas.create_line(lineStart[0],lineStart[1]+r//3,port2)
        canvas.create_line(lineEnd[0],lineEnd[1]-r//3,port1)
        canvas.create_line(lineStart[0],lineStart[1]+r//2,port3)
        
class OpAmp(component):
    def draw(self,canvas):
        size=80
        inputOffset,terminalOffset=10,7.5
        x1,y1=self.cx+size//2,self.cy
        x2,y2=x1-size,y1-size//2
        x3,y3=x2,y2+size
        canvas.create_polygon(x1,y1,x2,y2,x3,y3,fill="white",outline="black")
        input1=(x2,y2+size//4)
        input2=(x3,y3-size//4)
        output=(x1,y1)
        canvas.create_line(input1[0]+size//10,input1[1],input1[0]+terminalOffset+size//10,input1[1])
        canvas.create_line(input1[0]+size//10+terminalOffset//2,input1[1]-terminalOffset//2,input1[0]+size//10+terminalOffset//2,input1[1]-terminalOffset//2+terminalOffset)
        canvas.create_line(input2[0]+size//10,input2[1],input2[0]+terminalOffset+size//10,input2[1])
        
class Ground(component):
    def draw(self,canvas):
        size=30
        x1,y1=self.cx,self.cy+size//4
        x2,y2=x1+size//2,y1-(2*size/4)
        x3,y3=x2-size,y2
        canvas.create_polygon(x1,y1,x2,y2,x3,y3,fill="white",outline="black")
        
class Vcc(component):
    def draw(self,canvas):
        sizeX,smallR=15,2.5
        start=(self.cx-sizeX,self.cy)
        end=(self.cx+sizeX,self.cy)
        startCircle=(start[0]-smallR,start[1])
        endCircle=(end[0]+smallR,end[1])
        canvas.create_line(start,end)
        canvas.create_oval(startCircle[0]-smallR,startCircle[1]-smallR,startCircle[0]+smallR,startCircle[1]+smallR)
        canvas.create_oval(endCircle[0]-smallR,endCircle[1]-smallR,endCircle[0]+smallR,endCircle[1]+smallR)
        
class LED(component):
    def draw(self,canvas):
        size,smallS=20,7
        photoOffset,photoLength,photoWidth=4,9,3
        x1,y1=self.cx+size//2,self.cy
        x2,y2=x1-size,y1-size//2
        x3,y3=x2,y2+size
        canvas.create_polygon(x1,y1,x2,y2,x3,y3)
        bottom1=(self.cx,(y2+y1)/2-photoOffset)
        bottom2=(self.cx+size//5,(y2+y1)/2-photoOffset)
        top1=(bottom1[0]+photoWidth,bottom1[1]-photoLength)
        top2=(bottom2[0]+photoWidth,bottom2[1]-photoLength)
        canvas.create_line(bottom1,top1)
        #canvas.create_line(bottom2,top2)
        canvas.create_line(x1,y1-size//2,x1,y1+size//2, width="2")
        light1=(top1[0],top1[1]+smallS/2)
        light2=(light1[0]-smallS/2,light1[1]-smallS)
        light3=(light2[0]+smallS,light2[1])
        
        #light4=(top2[0],top2[1]+smallS/2)
        #light5=(light4[0]-smallS/2,light4[1]-smallS)
        #light6=(light5[0]+smallS,light5[1])
        canvas.create_polygon(light1,light3,light2)
        #canvas.create_polygon(light4,light6,light5)

# Basic Animation Framework

from tkinter import *

####################################
# customize these functions
####################################

def init(data):
    data.resistors=[resistor(60,60),resistor(80,80)] 
    data.diodes=[diode(200,200),diode(350,270)]
    data.transistors=[transistor(150,90),transistor(240,130)]
    data.opAmps=[OpAmp(240,300),OpAmp(250,80)]
    data.ground=[Ground(130,320),Ground(45,350)]
    data.vcc=[Vcc(320,140),Vcc(260,170)]
    data.LED=[LED(300,290),LED(20,100)]

def mousePressed(event, data):
    # use event.x and event.y
    pass

def keyPressed(event, data):
    # use event.char and event.keysym
    pass

def redrawAll(canvas, data):
    for i in data.resistors:
        i.draw(canvas)
        
    for i in data.diodes:
        i.draw(canvas)
    for i in data.transistors:
        i.draw(canvas)
    for i in data.opAmps:
        i.draw(canvas)
    for i in data.ground:
        i.draw(canvas)
    for i in data.vcc:
        i.draw(canvas)
    for i in data.LED:
        i.draw(canvas)    
####################################
# use the run function as-is
####################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    redrawAll(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(600, 600)

            