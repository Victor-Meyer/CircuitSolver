from sys import argv, exit
import numpy as np
import math
import cmath

CIRCUIT = '.circuit'
END = '.end'
AC = '.ac'

resistors = []
capacitors = []
inductors = []
vsources = []
isource = []

Nodes = ["GND"]

class four_element_component():
    def __init__(self,name,node1,node2,value):
        self.name = name
        self.n1 = node1
        self.n2 = node2
        self.value = value
        
        if(name[0] == 'R'):
            self.value = value
        
        elif(name[0] == 'C'):
            
            if(ac_flag):
                self.value = complex(0,-1/(w*value))
               
            else:
                self.value = 1e10
                
        elif(name[0] == 'L'):
            if(ac_flag):
                self.value = complex(0,(w*value))
            else:
                self.value = 1e-10
                
class five_element_component_val():
    def __init__(self,name,node1,node2,amp,phase,val):
        self.name = name
        self.n1 = node1
        self.n2 = node2
        self.amp = amp
        self.phase = phase
        self.value = val

def sign(a):
    if(a>0):
        return 1
    return -1

def parse_val(x):
    y = len(x)
    if(not x[y-1].isalpha()):
        return float(x)
    
    
#function that breaks the line down into components, recognises the component and creates an object for the component
def parse_line(line):
    
    tokens = line
    l = len(tokens)
    if(l==4):
        element = tokens[0]
        n1 = tokens[1]
        n2 = tokens[2]
        value = tokens[3]
        val = parse_val(value)
        
        if not(n1 in Nodes):
            Nodes.append(n1)
        if not(n2 in Nodes):
            Nodes.append(n2)            
        

        if(tokens[0][0] == 'R' or tokens[0][0] == 'C' or tokens[0][0] == 'L'):
            
            x = four_element_component(element,n1,n2,val)

            if(tokens[0][0] == 'R'):
                resistors.append(x)            
            if(tokens[0][0] == 'L'):
                inductors.append(x)
            if(tokens[0][0] == 'C'):
                capacitors.append(x) 
        else:
            print("Syntax Error in netlist File") 
            
    elif (l==5):
        if(ac_flag):
            print("Multiple Frequencies not possible , This program doesnot take AC and DC simultaneously ")
            exit(0)
        else:
            if(tokens[0][0] == 'V' or tokens[0][0] == 'I'):
                element = tokens[0]
                n1 = tokens[1]
                n2 = tokens[2]
                value = tokens[4]
                
                val = parse_val(value)
                
                if not(n1 in Nodes):                
                    Nodes.append(n1)
                if not(n2 in Nodes):
                    Nodes.append(n2)
            
                if not(tokens[3] == "dc"):
                    print("Invalid netlist , DC Voltage and Current Sources must be written as V/I n3 n4 dc 45")
                    exit(0)
                x = four_element_component(element,n1,n2,val)
                if(tokens[0][0] == 'V'):
                    vsources.append(x)            
                if(tokens[0][0] == 'I'):
                    isource.append(x)
                
    elif (l==6):
        
                if(tokens[0][0] == 'V' or tokens[0][0] == 'I'):
                    element = tokens[0]
                    n1 = tokens[1]
                    n2 = tokens[2]
                    amp = tokens[4]
                    
                    amp = parse_val(amp)/2
                    
                    phase = tokens[5]
                    phase = parse_val(phase)
                    val = complex(amp*math.cos(phase),amp*math.sin(phase))
                   
                    if not(n1 in Nodes):
                        Nodes.append(n1)
                    if not(n2 in Nodes):
                        Nodes.append(n2)
                   
                    x = five_element_component_val(element,n1,n2,amp,phase,val)

                    if(tokens[0][0] == 'V'):
                        vsources.append(x)
                    if(tokens[0][0] == 'I'):
                        isource.append(x)
                   
    return 

#function reads file and returns the part between .circuit and .end
def fileread():
    global ac_flag,w
    ########

    """
    It's a good practice to check if the user has given required and only the required inputs
    Otherwise, show them the expected usage.
    """

    if len(argv) == 2 :
        filename = argv[1]
        if (filename[-8:] != ".netlist"):  # Checks extension
            print("Incorrect file type. Expected Filetype is *.netlist")
            exit(0)
    else:
        print("Invalid command. Try in the form : python PythonScript.py NetlistCircuit.netlist")
        exit(0)
    try:
        f = open(filename)   #Try reading from the file , if it isn't possible throw error
        lines = f.readlines()
        f.close()
    except:
        print("No File %s is found" % filename)
        exit(0)

    #f=open("ckt.netlist")
        
    """
    The user might input a wrong file name by mistake.
    In this case, the open function will throw an IOError.
    Make sure you have taken care of it using try-catch
    """

    try:
        
        #lines = f.readlines()
        start = -1; end = -2
        flag1 = -1; flag2 = -1
        for line in lines:              # extracting circuit definition start and end lines
            #print(line)
            if CIRCUIT == line.replace("\t"," ").replace(" ", "")[:len(CIRCUIT)]:
                start = lines.index(line)
                #print(start)
                flag1 = 1
                flag2 = 1
            elif END == line[:len(END)] and flag1 == 1:
                end = lines.index(line)
                flag1 = 0
                #print(end)
            elif flag1 == 0 and flag2 ==1 and AC == line.replace("\t"," ").replace(" ", "")[:len(AC)]:
                ac_flag = 1
                line = line.split()
                if(line[1][0] in ['V','I'] ):
                    w = parse_val(line[2])
                    #print("Frequency :" , w, ac_flag)
                    w = w*math.pi/180
                    break
                else:
                    print("Invalid AC definition")
                    exit(0)
                    

        Token = []

        if flag1 == 0 and flag2 == 1:
            for line in ([(line.split('#')[0].split()) for line in lines[start+1:end]]):
                Token.append(line)
        else:
            print('Invalid circuit definition')
            exit(0)

        return Token

    except IOError:
        print('Invalid file')
        exit(0)
        
def populate_M():
    if(ac_flag==1):
        M = np.zeros((len(Nodes)-1+len(vsources),len(Nodes)-1+len(vsources)),dtype=np.complex)
        G = np.zeros((len(Nodes)-1,len(Nodes)-1),dtype=np.complex)
        B = np.zeros((len(Nodes)-1,len(vsources)),dtype=np.complex)
        C = np.zeros((len(vsources),len(Nodes)-1),dtype=np.complex)
        D = np.zeros((len(vsources),len(vsources)),dtype=np.complex)
        b = np.zeros((len(Nodes)-1+len(vsources)),dtype=np.complex)
        i = np.zeros((len(Nodes)-1),dtype=np.complex)
        e = np.zeros((len(vsources)),dtype=np.complex)
    else:
        M = np.zeros((len(Nodes)-1+len(vsources),len(Nodes)-1+len(vsources)),dtype=np.float)
        G = np.zeros((len(Nodes)-1,len(Nodes)-1),dtype=np.float)
        B = np.zeros((len(Nodes)-1,len(vsources)),dtype=np.float)
        C = np.zeros((len(vsources),len(Nodes)-1),dtype=np.float)
        D = np.zeros((len(vsources),len(vsources)),dtype=np.float)
        b = np.zeros(len(Nodes)-1+len(vsources),dtype=np.float)
        i = np.zeros((len(Nodes)-1),dtype=np.float)
        e = np.zeros((len(vsources)),dtype=np.float)
    
    for r in resistors:
        if (r.n1=="GND"):
                     index = Nodes.index(r.n2)
                     G[index-1][index-1] += 1/float(r.value)
        elif (r.n2=="GND"):
                     index = Nodes.index(r.n1)
                     G[index-1][index-1] += 1/float(r.value)
        else :
                     index1 = Nodes.index(r.n1)
                     index2 = Nodes.index(r.n2)
                     G[index1-1][index2-1] += -1/float(r.value)
                     G[index2-1][index1-1] += -1/float(r.value)
                     G[index1-1][index1-1] += 1/float(r.value)                           
                     G[index2-1][index2-1] += 1/float(r.value)
    for c in capacitors:
        if (c.n1=="GND"):
                     index = Nodes.index(c.n2)
                     G[index-1][index-1] += 1/(c.value)
        elif (c.n2=="GND"):
                     index = Nodes.index(c.n1)
                     G[index-1][index-1] += 1/(c.value)
        else :
                     index1 = Nodes.index(c.n1)
                     index2 = Nodes.index(c.n2)
                     G[index1-1][index2-1] += -1/(c.value)
                     G[index2-1][index1-1] += -1/(c.value)
                     G[index1-1][index1-1] += 1/(c.value)                           
                     G[index2-1][index2-1] += 1/(c.value)
    for l in inductors:
        if (l.n1=="GND"):
                     index = Nodes.index(l.n2)
                     print("inductor index")
                     print(index)
                     G[index-1][index-1] += 1/(l.value)
        elif (l.n2=="GND"):
                     index = Nodes.index(l.n1)
                     G[index-1][index-1] += 1/(l.value)
        else :
                     index1 = Nodes.index(l.n1)
                     index2 = Nodes.index(l.n2)
                     G[index1-1][index2-1] += -1/(l.value)
                     G[index2-1][index1-1] += -1/(l.value)
                     G[index1-1][index1-1] += 1/(l.value)
                     G[index2-1][index2-1] += 1/(l.value)
    for vs in vsources:
        
        e[vsources.index(vs)]=abs(vs.value) 
        
        if (vs.n1=="GND"):
                    
                    xindex = Nodes.index(vs.n2)-1
                    #print(xindex)
                    yindex = vsources.index(vs)
                    #print(yindex)
                    #print(B[0][1])
                    if(ac_flag):
                        B[xindex][yindex]=1
                    else:
                        B[xindex][yindex] = sign(float(vs.value))
                        print(vs.value)
                        print(yindex)
                        print(B[xindex][yindex])
                                                 
        elif (vs.n2=="GND"):
                    
                    xindex = Nodes.index(vs.n1)-1
                    yindex = vsources.index(vs)                     
                    if(ac_flag):
                        B[xindex][yindex]=-1
                    else:
                        B[xindex][yindex] = -sign(float(vs.value))
        else :
                    yindex = vsources.index(vs)

                    xindex1 = Nodes.index(vs.n1)-1
                    xindex2 = Nodes.index(vs.n2)-1
                    if(ac_flag):
                         B[xindex1][yindex]=1
                         B[xindex2][yindex]=-1
                    else:
                        B[xindex1][yindex] = -sign(float(vs.value))
                        B[xindex2][yindex] = sign(float(vs.value))
                    
    for cs in isource:
        
        if (cs.n1=="GND"):
                     index = Nodes.index(cs.n2)
                     i[index-1]+=cs.value
        elif (c.n2=="GND"):
                     index = Nodes.index(cs.n1)
                     i[index-1]-=cs.value
        else:
                     index1 = Nodes.index(cs.n1)
                     index2 = Nodes.index(cs.n2)
                     i[index1-1]-=cs.value
                     i[index2-1]+=cs.value
                    
    
   
    #M = np.concatenate(np.concatenate((G,B.T),axis=0),np.concatenate((B,D),axis=0),axis=1)
    M = np.concatenate((np.concatenate((G,B.transpose()),axis=0),np.concatenate((B,D),axis=0)),axis=1)
    b = np.concatenate((i,e),axis=0)
    
    return M,b   

ac_flag=0
for l in fileread():
    parse_line(l)
M,b = populate_M()
# print(M)
# print(b)
print("If you get any error please check the below instructions")
print("Please ensure netlist has properly written elements")
print("Please Give one frequency only")
print("Please ensure the logic of the netlist is proper to get correct results")
print("DC Eg:\n.circuit\nV1 GND n1 dc 10\nR1 n1 n2 2\nR2 GND n2 3\nR3 n2 n3 5\nR4 n3 GND 1\n.end")
print("AC Eg:\n.circuit\nV1 GND 1 ac 5 0\nC1 1 2 1\nR1 2 3 1e3\nL1 3 GND 1e-6\n.end\n.ac V1 1000",end="\n\n")



try:
    X = np.linalg.solve(M,b)
    print("Solved")
    print("The answers are printed in both a+ib and Amplitude,Phase form if AC circuit is given")
    #print(X)
    if (ac_flag):
        i=0
        for n in Nodes:
            if not(n == "GND"):
                print("Voltage at node "+ n + " is",end='\t')
                print(X[i],end="")
                print("V",end="\t")
                print(abs(X[i]),end="V ")
                print(cmath.phase(X[i])*180/3.14,end=" degrees\n")
                i=i+1
        for v in vsources:
            print("Current through Voltage Source "+ v.name+ " from "+v.n1+" to "+v.n2 + " is",end='\t')
            print(-X[i],end="")
            print("A",end="\t")
            print(abs(X[i]),end="A ")
            print(cmath.phase(-X[i])*180/3.14,end=" degrees\n")
            i=i+1
    else:
        i=0
        for n in Nodes:
            if not(n == "GND"):
                print("Voltage at node "+ n + " is",end='\t')
                print(X[i],end="")
                print("V")
                i=i+1
        for v in vsources:
            print("Current through Voltage Source "+ v.name + " from "+v.n1+" to "+v.n2+" is",end='\t')
            print(-X[i],end="")
            print("A")
            i=i+1
        
    
except:
    for line in lines:
        print(line)
    print("Unsolvable Matrix")
    exit()
    


