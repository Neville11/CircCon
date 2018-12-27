def readFile(path):
    with open(path, "rt") as f:
        return f.read()
        
commands={"IN","IF","DISP","THEN","ELSE","PRINT","OUT"}
equalityCheck={"==",">","<"}
operators={"+","-","*","/"}
assignment={"="}
variables=set()

def Error(line,errorType):
    return "%s Error on line %d" %(errorType,line)

def Interpreter(filename):
    content=readFile(filename)
    lineByLine=content.splitlines()
    for i in len(lineByLine):
        terms = lineByLine[i].split("")
        if i==0 and terms[0]=="IN":
            for j in terms[1:].split(","):
                variables.add(j)#error check; cannot be overwritten, cannot be int
        elif terms[0] in commands:#error check, only set "in" command once
            if terms[0]=="IF":
                if len(terms)==4:
                    if terms[1] in variables and terms[3] in variables and terms[2] in operators:#syntax IF a<b
                if lineByLine[i+1][0]=="THEN" and lineByLine[i+2][0]=="ELSE"
            elif terms[0]=="THEN":
            elif terms[0]=="ELSE":
                
        elif terms[0] not in commands:
            if terms[0] not in variables:#error check; LHS can't be an existing variable
                if terms[1] in assignment and terms[3] in operators: #assignment x=a*b
                    if terms[2] in variables and terms[4] in variables:#must exist 
                        
            else:
            return Error(i,"Syntax")
        
            