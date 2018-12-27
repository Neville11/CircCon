from tkinter import *
from image_util import *
import copy
import math
import string

# NOTE: Pricing was done on a standard of 10,000 units per part being purchased

####################################
# CLASSES
####################################

class Part(object):
    def __init__(self, rx, ry, portPoints, price):
        self.rx = rx
        self.ry = ry
        self.portPoints = portPoints
        self.price = price

class Wire(object):
    def __init__(self, part1, port1, part2, port2):
        self.part1 = part1
        self.port1 = port1
        self.part2 = part2
        self.port2 = port2
    
    def draw(self, canvas):
        # get connection points
        x1, y1 = self.part1.portPoints[self.port1]
        x1 += self.part1.rx
        y1 += self.part1.ry
        x2, y2 = self.part2.portPoints[self.port2]
        x2 += self.part2.rx
        y2 += self.part2.ry
        # connect the points
        if isinstance(self.part1, Node) and isinstance(self.part2, OpAmp) and x2 > x1 and x2 - x1 < 200:
            midX = x1 + 30
            canvas.create_line(x1, y1, midX, y1)
            canvas.create_line(midX, y1, midX, y2)
            canvas.create_line(midX, y2, x2, y2)
        elif isinstance(self.part2, Node) and isinstance(self.part1, OpAmp) and x1 > x2 and x1 - x2 < 200:
            midX = x2 + 30
            canvas.create_line(x1, y1, midX, y1)
            canvas.create_line(midX, y1, midX, y2)
            canvas.create_line(midX, y2, x2, y2)
        elif x1 == x2 or y1 == y2:
            canvas.create_line(x1, y1, x2, y2)
        elif isinstance(self.part1, Transistor) and self.port1 > 0:
            canvas.create_line(x1, y1, x1, y2)
            canvas.create_line(x1, y2, x2, y2)
        elif isinstance(self.part2, Transistor) and self.port2 > 0:
            canvas.create_line(x2, y2, x2, y1)
            canvas.create_line(x2, y1, x1, y1)
        elif isinstance(self.part1, Node) and self.part1.tag == "TransOut" and x2 > x1:
            midX = x1 + 30
            canvas.create_line(x1, y1, midX, y1)
            canvas.create_line(midX, y1, midX, y2)
            canvas.create_line(midX, y2, x2, y2)
        elif isinstance(self.part2, Node) and self.part2.tag == "TransOut" and x1 > x2:
            midX = x2 + 30
            canvas.create_line(x1, y1, midX, y1)
            canvas.create_line(midX, y1, midX, y2)
            canvas.create_line(midX, y2, x2, y2)
        elif isinstance(self.part1, Node) and self.part1.tag == "AmpOut" and x2 > x1:
            midX = x1 + 30
            canvas.create_line(x1, y1, midX, y1)
            canvas.create_line(midX, y1, midX, y2)
            canvas.create_line(midX, y2, x2, y2)
        elif isinstance(self.part2, Node) and self.part2.tag == "AmpOut" and x1 > x2:
            midX = x2 + 30
            canvas.create_line(x1, y1, midX, y1)
            canvas.create_line(midX, y1, midX, y2)
            canvas.create_line(midX, y2, x2, y2)
        elif (isinstance(self.part1, Node) and not self.part1.isOpen) or isinstance(self.part1, Ground):
            canvas.create_line(x1, y1, x1, y2)
            canvas.create_line(x1, y2, x2, y2)
        elif (isinstance(self.part2, Node) and not self.part2.isOpen) or isinstance(self.part2, Ground):
            canvas.create_line(x2, y2, x2, y1)
            canvas.create_line(x2, y1, x1, y1)
        else:
            if isinstance(self.part1, OpAmp) and self.port1 == 1:
                midX = x2 - 60
            elif isinstance(self.part2, OpAmp) and self.port2 == 1:
                midX = x2 - 60
            elif isinstance(self.part1, Resistor) and self.part1.tag=="SubIn" and self.port1 == 0:
                midX = x2 - 56
            elif isinstance(self.part2, Resistor) and self.part2.tag=="SubIn" and self.port2 == 0:
                midX = x2 - 56
            else:
                midX = x2 - 30
            canvas.create_line(x1, y1, midX, y1)
            canvas.create_line(midX, y1, midX, y2)
            canvas.create_line(midX, y2, x2, y2)

class Resistor(Part):
    # based on 311-1KMTR-ND from DigiKey
    def __init__(self, rx, ry, resistance, tag="", price=0.5):
        portPoints = [(-27, 0), (27, 0)]
        super().__init__(rx, ry, portPoints, price)
        self.resistance = resistance
        self.tag = tag
        
    def numStr(self, num):
        if(num < 1000):
            out = str(num);
        if(num >= 1000):
            out = str(int((num/100)/10)) + "K";
        if(num >= 1000000):
            out = str(int((num/100000)/10)) + "M";
        if(num >= 1000000000):
            out = str(int((num/100000000)/10)) + "B";
        return out
    
    def draw(self, canvas):
        start=(self.rx - 27, self.ry)
        numPoints = 9
        dx, dy = 6, 20
        for i in range(0, numPoints):
            if i==0 or i==8: end=(start[0] + dx,start[1] + dy//2)
            elif i%2==1: end=(start[0] + dx, start[1] - dy)
            else:
                end=(start[0] + dx, start[1] + dy)
            canvas.create_line(start, end)
            start = end
        canvas.create_text(self.rx, self.ry-12, text=self.numStr(self.resistance) + " ohms", font="Times 15 italic", anchor=S)

class Transistor(Part):
    # based on BC846BLT1GOSTR-ND from DigiKey
    def __init__(self, rx, ry, pType, price=1.8):
        r=15
        port1=(r*math.cos((math.pi)-2*math.pi/3), r*math.sin((math.pi)-2*math.pi/3))
        port2=(r*math.cos((math.pi)-4*math.pi/3), r*math.sin((math.pi)-4*math.pi/3))
        port3=(r*math.cos((math.pi)-2*math.pi), r*math.sin((math.pi)-2*math.pi))
        portPoints = [port3, port2, port1]
        super().__init__(rx, ry, portPoints, price)
        self.pType = pType
        self.Vce = 0.3
        self.Ib = 0.005
    
    def draw(self, canvas):
        r=15
        canvas.create_oval(self.rx-r,self.ry-r,self.rx+r,self.ry+r,fill="white",outline="black")
        lineStart=(self.rx-r//2,self.ry-r//2)
        lineEnd=(lineStart[0],lineStart[1]+r)
        port1=(self.rx + r*math.cos((math.pi)-2*math.pi/3), self.ry + r*math.sin((math.pi)-2*math.pi/3))
        port2=(self.rx + r*math.cos((math.pi)-4*math.pi/3), self.ry + r*math.sin((math.pi)-4*math.pi/3))
        port3=(self.rx + r*math.cos((math.pi)-2*math.pi), self.ry + r*math.sin((math.pi)-2*math.pi))
        canvas.create_line(lineStart,lineEnd)
        canvas.create_line(lineStart[0],lineStart[1]+r//3,port2)
        canvas.create_line(lineEnd[0],lineEnd[1]-r//3,port1)
        canvas.create_line(lineStart[0],lineStart[1]+r//2,port3)

class Diode(Part):
    # based on 1N4148FSTR-ND from DigiKey
    def __init__(self, rx, ry, forwardVoltage=1, color="black", width="2", price=1):
        portPoints = [(-10, 0), (10, 0)]
        super().__init__(rx, ry, portPoints, price)
        self.forwardVoltage = forwardVoltage
        self.color = color
        self.width = width
    
    def draw(self, canvas):
        size=20
        x1,y1=self.rx+size//2,self.ry
        x2,y2=x1-size,y1-size//2
        x3,y3=x2,y2+size
        canvas.create_polygon(x1,y1,x2,y2,x3,y3, fill=self.color, outline="black")
        canvas.create_line(x1,y1-size//2,x1,y1+size//2, width=self.width)

class LED(Diode):
    # based on SML-D12U1WT86TR-ND from DigiKey
    def __init__(self, rx, ry, forwardVoltage=2.2, currentDraw=0.020, color="white", width="1", price=2.9):
        super().__init__(rx, ry, forwardVoltage, color, width, price)
        self.currentDraw = currentDraw
    
    def draw(self, canvas):
        super().draw(canvas)
        radius = 20
        canvas.create_oval(self.rx - radius, self.ry - radius, self.rx + radius, self.ry + radius, fill="")

class OpAmp(Part):
    # based on 497-1591-2-ND from DigiKey
    def __init__(self, rx, ry, price=9.2):
        size=80
        x1,y1=rx+size//2,ry
        x2,y2=x1-size,y1-size//2
        x3,y3=x2,y2+size
        input1=(x2 - rx,y2+size//4 - ry)
        input2=(x3 - rx,y3-size//4 - ry)
        output=(x1 - rx,y1 - ry)
        portPoints = [input1, input2, output]
        super().__init__(rx, ry, portPoints, price)
    
    def draw(self, canvas):
        size=80
        inputOffset,terminalOffset=10,8
        x1,y1=self.rx+size//2,self.ry
        x2,y2=x1-size,y1-size//2
        x3,y3=x2,y2+size
        canvas.create_polygon(x1,y1,x2,y2,x3,y3,fill="white",outline="black")
        input1=(x2,y2+size//4)
        input2=(x3,y3-size//4)
        output=(x1,y1)
        canvas.create_line(input2[0]+size//10,input2[1],input2[0]+terminalOffset+size//10,input2[1])
        canvas.create_line(input2[0]+size//10+terminalOffset//2,input2[1]-      terminalOffset//2,input2[0]+size//10+terminalOffset//2,input2[1]-terminalOffset//2+terminalOffset)
        canvas.create_line(input1[0]+size//10,input1[1],input1[0]+terminalOffset+size//10,input1[1])

class Comparator(Part):
    # based on 497-1593-2-ND from DigiKey
    def __init__(self, rx, ry, price=10):
        size=80
        x1,y1=rx+size//2,ry
        x2,y2=x1-size,y1-size//2
        x3,y3=x2,y2+size
        input1=(x2 - rx,y2+size//4 - ry)
        input2=(x3 - rx,y3-size//4 - ry)
        output=(x1 - rx,y1 - ry)
        portPoints = [input1, input2, output, (0, 0), (0, 0)]
        super().__init__(rx, ry, portPoints, price)
    
    def draw(self, canvas):
        size=80
        inputOffset,terminalOffset=10,8
        x1,y1=self.rx+size//2,self.ry
        x2,y2=x1-size,y1-size//2
        x3,y3=x2,y2+size
        canvas.create_polygon(x1,y1,x2,y2,x3,y3,fill="white",outline="black")
        input1=(x2,y2+size//4)
        input2=(x3,y3-size//4)
        output=(x1,y1)
        canvas.create_line(input2[0]+size//10,input2[1],input2[0]+terminalOffset+size//10,input2[1])
        canvas.create_line(input2[0]+size//10+terminalOffset//2,input2[1]-      terminalOffset//2,input2[0]+size//10+terminalOffset//2,input2[1]-terminalOffset//2+terminalOffset)
        canvas.create_line(input1[0]+size//10,input1[1],input1[0]+terminalOffset+size//10,input1[1])

class Buffer(Part):
    # based on NC7SZ125P5XTR-ND from DigiKey
    def __init__(self, rx, ry, price=5.5):
        size=80
        x1,y1=rx+size//2,ry
        x2,y2=x1-size,y1-size//2
        x3,y3=x2,y2+size
        input1=(x2 - rx,y2+size//4 - ry)
        input2=(x3 - rx,y3-size//4 - ry)
        output=(x1 - rx,y1 - ry)
        portPoints = [(input1[0], 0), output]
        super().__init__(rx, ry, portPoints, price)
    
    def draw(self, canvas):
        size=80
        inputOffset,terminalOffset=10,8
        x1,y1=self.rx+size//2,self.ry
        x2,y2=x1-size,y1-size//2
        x3,y3=x2,y2+size
        canvas.create_polygon(x1,y1,x2,y2,x3,y3,fill="white",outline="black")

class Ground(Part):
    def __init__(self, rx, ry, price=0):
        portPoints = [(0, 0)]
        super().__init__(rx, ry, portPoints, price)
    
    def draw(self, canvas):
        size=30
        x1,y1=self.rx,self.ry+size//4
        x2,y2=x1+size//2,y1-(2*size/4)
        x3,y3=x2-size,y2
        canvas.create_polygon(x1,y1,x2,y2,x3,y3,fill="white",outline="black")

class Node(Part):
    def __init__(self, rx, ry, isOpen, tag="", price=0):
        portPoints = [(0, 0)]
        super().__init__(rx, ry, portPoints, price)
        self.isOpen = isOpen
        self.tag = tag
    
    def draw(self, canvas):
        if self.isOpen:
            nodeRadius = 5
            color = "white"
            tag = self.tag
        else:
            nodeRadius = 3
            color = "black"
            tag = ""
        x1 = self.rx - nodeRadius
        y1 = self.ry - nodeRadius
        x2 = self.rx + nodeRadius
        y2 = self.ry + nodeRadius
        canvas.create_oval(x1, y1, x2, y2, fill=color)
        canvas.create_text(self.rx - 4, self.ry - 4, text=tag, font="Times 20 italic", anchor=SE)

class Source(Node):
    def __init__(self, rx, ry, price=0):
        super().__init__(rx, ry, True, "Vcc", price)
        
####################################
# METHODS
####################################

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def addPart(data, part):
    data.parts.append(part)
    data.totalPrice += part.price

def connectParts(data, part1, port1, part2, port2):
    data.connections.append(Wire(data.parts[part1], port1, data.parts[part2], port2))

def drawParts(data, canvas):
    for part in data.parts:
        part.draw(canvas)

def drawConnections(data, canvas):
    for connection in data.connections:
        connection.draw(canvas)

def defineCircuit(data, parts, connections):
    for part in parts:
        if isinstance(part, Part):
            addPart(data, part)
        else:
            add(data, part[0], part[1], part[2], part[3:])
    for wire in connections:
        connectParts(data, wire[0], wire[1], wire[2], wire[3])

def add(data, addFunction, cx, cy, values):
    addFunction(data, cx, cy, values)

####################################
# COMPOSITE COMPONENTS
####################################

def LEDDisplay(data, cx, cy, values):
    Vin = values[0]
    Rled = LED(0, 0).forwardVoltage/LED(0, 0).currentDraw
    r1 = (Vin*Rled)/LED(0, 0).forwardVoltage - Rled
    addPart(data, Resistor(cx - 50, cy, round(r1)))
    addPart(data, LED(cx + 20, cy))
    addPart(data, Ground(cx + 60, cy + 50))
    connectParts(data, -3, 1, -2, 0)
    connectParts(data, -2, 1, -1, 0)

def VoltageDivider(data, cx, cy, values):
    factor = values[0]
    r2 = 1000
    r1 = r2 * (factor - 1)
    addPart(data, Resistor(cx - 50, cy, round(r1)))
    addPart(data, Node(cx, cy, False))
    addPart(data, Resistor(cx + 60, cy + 50, round(r2)))
    addPart(data, Ground(cx + 120, cy + 80))
    addPart(data, Buffer(cx + 70, cy - 50))
    connectParts(data, -5, 1, -4, 0)
    connectParts(data, -3, 0, -4, 0)
    connectParts(data, -1, 0, -4, 0)
    connectParts(data, -3, 1, -2, 0)

def InvertingAmplifier(data, cx, cy, values):
    gain = -values[0]
    r1 = 1000
    r2 = r1 * gain
    addPart(data, Resistor(cx - 50, cy, round(r1)))
    addPart(data, Node(cx, cy, False))
    addPart(data, Resistor(cx + 60, cy - 50, round(r2)))
    yOffset = data.yOffset
    addPart(data, Node(cx + 120, cy - yOffset, False, "AmpOut"))
    addPart(data, Ground(cx - 50, cy + 80))
    addPart(data, OpAmp(cx + 62, cy - yOffset))
    connectParts(data, -2, 0, -1, 1)
    connectParts(data, -1, 0, -5, 0)
    connectParts(data, -6, 1, -5, 0)
    connectParts(data, -4, 0, -5, 0)
    connectParts(data, -4, 1, -3, 0)
    connectParts(data, -1, 2, -3, 0)

def NonInvertingAmplifier(data, cx, cy, values):
    gain = values[0] - 1
    r1 = 1000
    r2 = r1 * gain
    addPart(data, Resistor(cx - 50, cy, round(r1)))
    addPart(data, Node(cx, cy, False))
    addPart(data, Resistor(cx + 60, cy - 50, round(r2)))
    yOffset = data.yOffset
    addPart(data, Node(cx + 120, cy - yOffset, False, "AmpOut"))
    addPart(data, Ground(cx - 100, cy + 80))
    addPart(data, OpAmp(cx + 62, cy - yOffset))
    connectParts(data, -2, 0, -6, 0)
    connectParts(data, -1, 0, -5, 0)
    connectParts(data, -6, 1, -5, 0)
    connectParts(data, -4, 0, -5, 0)
    connectParts(data, -4, 1, -3, 0)
    connectParts(data, -1, 2, -3, 0)

def TransistorSwitch(data, cx, cy, values):
    Vin = values[0]
    Vce = Transistor(0, 0, True).Vce
    Ib = Transistor(0, 0, True).Ib
    r1 = (Vin-Vce)/Ib
    xOffset = Transistor(0, 0, True).portPoints[1][0]
    addPart(data, Resistor(cx - 30, cy, round(r1)))
    addPart(data, Resistor(cx - 30, cy - 80, 330))
    addPart(data, Transistor(cx + 25, cy, True))
    addPart(data, Node(cx + 25 + xOffset, cy - 40, False, "TransOut"))
    connectParts(data, -4, 1, -2, 0)
    connectParts(data, -1, 0, -2, 1)
    connectParts(data, -3, 1, -1, 0)

def SummingAmplifier(data, cx, cy, values):
    gain = values[0]
    r1 = 1000
    r2 = r1 * gain
    addPart(data, Resistor(cx - 70, cy - 40, round(r1)))
    addPart(data, Resistor(cx - 70, cy + 40, round(r1)))
    addPart(data, Node(cx - 20, cy, False))
    addPart(data, Node(cx, cy, False))
    addPart(data, Resistor(cx + 60, cy - 50, round(r2)))
    yOffset = data.yOffset
    addPart(data, Node(cx + 120, cy - yOffset, False, "AmpOut"))
    addPart(data, Ground(cx, cy + 80))
    addPart(data, OpAmp(cx + 62, cy - yOffset))
    connectParts(data, -8, 1, -6, 0)
    connectParts(data, -7, 1, -6, 0)
    connectParts(data, -5, 0, -6, 0)
    connectParts(data, -2, 0, -1, 1)
    connectParts(data, -1, 0, -5, 0)
    connectParts(data, -4, 0, -5, 0)
    connectParts(data, -4, 1, -3, 0)
    connectParts(data, -1, 2, -3, 0)

def DifferentialAmplifier(data, cx, cy, values):
    gain = values[0]
    r1 = 1000
    r2 = r1 * gain
    VoltageDivider(data, cx - 50, cy + 40, (2,))
    data.parts.pop()
    data.connections.pop(-2)
    data.totalPrice -= 5.5 # the price of a buffer
    addPart(data, Resistor(cx - 100, cy - 10, round(r1), "SubIn"))
    addPart(data, Node(cx, cy - 10, False))
    addPart(data, Resistor(cx + 60, cy - 50, round(r2)))
    yOffset = data.yOffset
    addPart(data, Node(cx + 120, cy - yOffset, False, "AmpOut"))
    addPart(data, OpAmp(cx + 62, cy - yOffset))
    connectParts(data, -1, 0, -4, 0)
    connectParts(data, -5, 1, -4, 0)
    connectParts(data, -3, 0, -4, 0)
    connectParts(data, -3, 1, -2, 0)
    connectParts(data, -1, 2, -2, 0)
    connectParts(data, -8, 0, -1, 1)

####################################
# MODEL
####################################

def init(data):
    data.microchipPrice = 331 # based on ATmega32u4-MU from ATmel
    data.totalPrice = 0
    data.parts = []
    data.connections = []
    data.yOffset = OpAmp(0,0).portPoints[0][1]
    data.filename = "circuit.txt"
    data.Vcc = 5
    
    # defining the circuit...
    partList = []
    wireList = []
    numParts = 0
    
    # by compiling the code:
    commands={"IN","IF","DISP","THEN","ELSE","PRINT","OUT"}
    equalityCheck={">":0, "<":1}
    operators={"+","-","*","/"}
    assignment={"="}
    variables=dict()
    inY=dict()

    content=readFile(data.filename)
    lineByLine=content.splitlines()
    drawPoint = [50, 200]
    
    for i in range(len(lineByLine)):
        terms = lineByLine[i].split(" ")
        if terms[0]=="IN":
            for j in range(len(terms[1:])):
                variables[terms[1 + j]] = (j,0)#error check; cannot be overwritten, cannot be int
                numParts += 1
                inY[terms[1 + j]] = drawPoint[1] + j * 200
                partList.append(Node(drawPoint[0], drawPoint[1] + j * 200, True, "V" + terms[1 + j]))
            drawPoint[0] += 150
        elif terms[0]=="OUT":
            for j in range(len(terms[1:])):
                if terms[1 + j] in inY:
                    drawPoint[1] = inY[terms[1 + j]]
                drawPoint[1] += 100
                if terms[1 + j] in variables:
                    partList.append(Node(drawPoint[0], drawPoint[1] + j * 200, True, "V" + terms[1 + j]))
                    numParts += 1
                    print(terms[1 + j], variables[terms[1 + j]], numParts)
                    wireList.append((variables[terms[1 + j]][0], variables[terms[1 + j]][1], numParts-1, 0))
                    variables[terms[1 + j]] = (numParts - 1, 0)
            drawPoint[0] += 150
        elif terms[0]=="DISP":
            for j in range(len(terms[1:])):
                if terms[1 + j] in inY:
                    drawPoint[1] = inY[terms[1 + j]]
                drawPoint[1] += 360
                if terms[1 + j] in variables:
                    partList.append((LEDDisplay, drawPoint[0], drawPoint[1] + j * 200, data.Vcc))
                    numParts += 3
                    print(terms[1 + j], variables[terms[1 + j]], numParts)
                    wireList.append((variables[terms[1 + j]][0], variables[terms[1 + j]][1], numParts-3, 0))
                drawPoint[1] -= 360
        elif terms[0]=="VCC":
            data.Vcc = float(terms[1])
        elif terms[0] in commands:#error check, only set "in" command once
            if terms[0]=="IF":
                if len(terms)==4:
                    if terms[1] in variables and terms[3] in variables and terms[2] in equalityCheck:#syntax IF a<b
                        if terms[1] in inY:
                            drawPoint[1] = inY[terms[1]]
                        if lineByLine[i+1][:4]=="THEN" and lineByLine[i+2][:4]=="ELSE":
                            terms2 = lineByLine[i+2][5:].split(" ")
                            terms2[0] += "1"
                            termsOrig = terms
                            terms = terms2
                            drawPoint[0] += 250
                            drawPoint[1] += 200
                            if terms[0] not in variables:#error check; LHS can't be an existing variable
                                if terms[1] in assignment and terms[3] in operators: #assignment x=a*b
                                    if terms[2] in variables and terms[4] in variables and terms[3] == "+":#must exist 
                                        if inY[terms[2]] > inY[terms[4]]:
                                            terms[2], terms[4] = terms[4], terms[2]
                                        partList.append((SummingAmplifier, drawPoint[0], drawPoint[1], 1))
                                        numParts += 8
                                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-8, 0))
                                        wireList.append((variables[terms[4]][0], variables[terms[4]][1], numParts-7, 0))
                                        variables[terms[0]] = (numParts-3, 0)
                                        print(terms[0], variables[terms[0]], numParts)
                                        drawPoint[0] += 300
                                        partList.append((InvertingAmplifier, drawPoint[0], drawPoint[1], -1))
                                        numParts += 6
                                        wireList.append((variables[terms[0]][0], variables[terms[0]][1], numParts-6, 0))
                                        variables[terms[0]] = (numParts-3, 0)
                                        print(terms[0], variables[terms[0]], numParts)
                                    elif terms[2] in variables and terms[4] in variables and terms[3] == "-":#must exist 
                                        partList.append((DifferentialAmplifier, drawPoint[0], drawPoint[1], 1))
                                        numParts += 9
                                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-9, 0))
                                        wireList.append((variables[terms[4]][0], variables[terms[4]][1], numParts-5, 0))
                                        variables[terms[0]] = (numParts-2, 0)
                                        print(terms[0], variables[terms[0]], numParts)
                                    elif terms[2] in variables and terms[4][0] in string.digits and terms[3] == "/":#must exist 
                                        partList.append((VoltageDivider, drawPoint[0], drawPoint[1], float(terms[4])))
                                        numParts += 5
                                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-5, 0))
                                        variables[terms[0]] = (numParts-1, 1)
                                        print(terms[0], variables[terms[0]], numParts)
                                    elif terms[2] in variables and terms[4][0] in string.digits and terms[3] == "*":#must exist 
                                        partList.append((NonInvertingAmplifier, drawPoint[0], drawPoint[1], float(terms[4])))
                                        numParts += 6
                                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-1, 1))
                                        variables[terms[0]] = (numParts-3, 0)
                                        print(terms[0], variables[terms[0]], numParts)
                            else:
                                pass # error!
                            terms = termsOrig
                            drawPoint[0] -= 250
                            drawPoint[1] -= 200
                            ###
                            terms3 = lineByLine[i+1][5:].split(" ")
                            terms3[0] += "2"
                            termsOrig = terms
                            terms = terms3
                            drawPoint[0] += 200
                            drawPoint[1] += 600
                            if terms[0] not in variables:#error check; LHS can't be an existing variable
                                if terms[1] in assignment and terms[3] in operators: #assignment x=a*b
                                    if terms[2] in variables and terms[4] in variables and terms[3] == "+":#must exist 
                                        if inY[terms[2]] > inY[terms[4]]:
                                            terms[2], terms[4] = terms[4], terms[2]
                                        partList.append((SummingAmplifier, drawPoint[0], drawPoint[1], 1))
                                        numParts += 8
                                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-8, 0))
                                        wireList.append((variables[terms[4]][0], variables[terms[4]][1], numParts-7, 0))
                                        variables[terms[0]] = (numParts-3, 0)
                                        print(terms[0], variables[terms[0]], numParts)
                                        drawPoint[0] += 300
                                        partList.append((InvertingAmplifier, drawPoint[0], drawPoint[1], -1))
                                        numParts += 6
                                        wireList.append((variables[terms[0]][0], variables[terms[0]][1], numParts-6, 0))
                                        variables[terms[0]] = (numParts-3, 0)
                                        print(terms[0], variables[terms[0]], numParts)
                                    elif terms[2] in variables and terms[4] in variables and terms[3] == "-":#must exist 
                                        partList.append((DifferentialAmplifier, drawPoint[0], drawPoint[1], 1))
                                        numParts += 9
                                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-9, 0))
                                        wireList.append((variables[terms[4]][0], variables[terms[4]][1], numParts-5, 0))
                                        variables[terms[0]] = (numParts-2, 0)
                                        print(terms[0], variables[terms[0]], numParts)
                                    elif terms[2] in variables and terms[4][0] in string.digits and terms[3] == "/":#must exist 
                                        partList.append((VoltageDivider, drawPoint[0], drawPoint[1], float(terms[4])))
                                        numParts += 5
                                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-5, 0))
                                        variables[terms[0]] = (numParts-1, 1)
                                        print(terms[0], variables[terms[0]], numParts)
                                    elif terms[2] in variables and terms[4][0] in string.digits and terms[3] == "*":#must exist 
                                        partList.append((NonInvertingAmplifier, drawPoint[0], drawPoint[1], float(terms[4])))
                                        numParts += 6
                                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-1, 1))
                                        variables[terms[0]] = (numParts-3, 0)
                                        print(terms[0], variables[terms[0]], numParts)
                            else:
                                pass # error!
                            terms = termsOrig
                            drawPoint[0] -= 200
                            drawPoint[1] -= 200
                            ###
                            if terms2[3] == "+" or terms3[3] == "+":
                                someValue = -100
                            else:
                                someValue = +100
                            drawPoint[0] += someValue
                            partList.append(OpAmp(drawPoint[0], drawPoint[1]))
                            drawPoint[0] -= someValue
                            numParts += 1
                            wireList.append((variables[terms[1]][0], variables[terms[1]][1], numParts-1, (0 + equalityCheck[terms[2]])%2))
                            wireList.append((variables[terms[3]][0], variables[terms[3]][1], numParts-1, (1 + equalityCheck[terms[2]])%2))
                            variables[terms2[0][:1] + "3"] = (numParts-1, 2)
                            print(terms2[0][:1] + "3", variables[terms2[0][:1] + "3"], numParts)
                            drawPoint[0] += 480
                            ###
                            letter = terms2[0][:1]
                            var1 = letter + "1"
                            var2 = letter + "2"
                            var3 = letter + "3"
                            partList.append((TransistorSwitch, drawPoint[0], drawPoint[1], data.Vcc))
                            inY[letter] = drawPoint[1]
                            numParts += 4
                            wireList.append((variables[var1][0], variables[var1][1], numParts-3, 0))
                            wireList.append((variables[var3][0], variables[var3][1], numParts-4, 0))
                            wireList.append((variables[var2][0], variables[var2][1], numParts-2, 2))
                            variables[letter] = (numParts-1, 0)
                            print(letter, variables[letter], numParts)
                            drawPoint[0] += 300
                            drawPoint[1] -= 400
        elif terms[0] not in commands:
            if terms[0] not in variables:#error check; LHS can't be an existing variable
                if terms[1] in assignment and terms[3] in operators: #assignment x=a*b
                    if terms[2] in inY:
                        drawPoint[1] = inY[terms[2]]
                    if terms[2] in variables and terms[4] in variables and terms[3] == "+":#must exist
                        if inY[terms[2]] > inY[terms[4]]:
                            terms[2], terms[4] = terms[4], terms[2]
                        partList.append((SummingAmplifier, drawPoint[0], drawPoint[1], 1))
                        numParts += 8
                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-8, 0))
                        wireList.append((variables[terms[4]][0], variables[terms[4]][1], numParts-7, 0))
                        variables[terms[0]] = (numParts-3, 0)
                        drawPoint[0] += 300
                        print(terms[0], variables[terms[0]], numParts)
                        partList.append((InvertingAmplifier, drawPoint[0], drawPoint[1], -1))
                        numParts += 6
                        wireList.append((variables[terms[0]][0], variables[terms[0]][1], numParts-6, 0))
                        variables[terms[0]] = (numParts-3, 0)
                        drawPoint[0] += 300
                        print(terms[0], variables[terms[0]], numParts)
                    elif terms[2] in variables and terms[4] in variables and terms[3] == "-":#must exist 
                        partList.append((DifferentialAmplifier, drawPoint[0], drawPoint[1], 1))
                        numParts += 9
                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-9, 0))
                        wireList.append((variables[terms[4]][0], variables[terms[4]][1], numParts-5, 0))
                        variables[terms[0]] = (numParts-2, 0)
                        drawPoint[0] += 300
                        print(terms[0], variables[terms[0]], numParts)
                    elif terms[2] in variables and terms[4][0] in string.digits and terms[3] == "/":#must exist 
                        partList.append((VoltageDivider, drawPoint[0], drawPoint[1], float(terms[4])))
                        numParts += 5
                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-5, 0))
                        variables[terms[0]] = (numParts-1, 1)
                        drawPoint[0] += 300
                        print(terms[0], variables[terms[0]], numParts)
                    elif terms[2] in variables and terms[4][0] in string.digits and terms[3] == "*":#must exist 
                        partList.append((NonInvertingAmplifier, drawPoint[0], drawPoint[1], float(terms[4])))
                        numParts += 6
                        wireList.append((variables[terms[2]][0], variables[terms[2]][1], numParts-1, 1))
                        variables[terms[0]] = (numParts-3, 0)
                        drawPoint[0] += 300
                        print(terms[0], variables[terms[0]], numParts)
                inY[terms[0]] = drawPoint[1]
            else:
                pass # error!
    
    defineCircuit(data, partList, wireList)
    print(partList)
    print(wireList)
    
####################################
# CONTROL
####################################

def mousePressed(event, data):
    pass

def keyPressed(event, data):
    if event.keysym == "Right":
        for part in data.parts:
            part.rx -= 50
    elif event.keysym == "Left":
        for part in data.parts:
            part.rx += 50
    elif event.keysym == "Up":
        for part in data.parts:
            part.ry += 50
    elif event.keysym == "Down":
        for part in data.parts:
            part.ry -= 50

def timerFired(data):
    pass

####################################
# VIEW
####################################

def redrawAll(canvas, data):
    drawConnections(data, canvas)
    drawParts(data, canvas)
    price1 = str(round(data.totalPrice)/100)
    price1 += "0" * (4-len(price1))
    canvas.create_text(10, 5, text="Total Price (per Board): $" + price1, font="Times 20", anchor=NW)
    canvas.create_text(350, 5, text="Total Price (per Batch of 10,000): $" + str(round(data.totalPrice*10000)/100) + "0", font="Times 20", anchor=NW)
    price2 = str(round(data.microchipPrice - data.totalPrice)/100)
    price2 += "0" * (4-len(price2))
    canvas.create_text(10, 30, text="Money Saved (per Board): $" + price2, font="Times 20", anchor=NW)
    canvas.create_text(350, 30, text="Money Saved (per Batch of 10,000): $" + str(round(data.microchipPrice*10000 - data.totalPrice*10000)/100) + "0", font="Times 20", anchor=NW)

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

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 1000 # milliseconds
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
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(850, 800)