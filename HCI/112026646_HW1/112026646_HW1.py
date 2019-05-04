import os,sys
import math as m
import random
import string
import time

#Key Width equal to 1 key
keyWidth = 1.0
#Key coordinate for a 6 rows by 5 column keyboard
cord = [[(x + keyWidth/2.0,y+keyWidth/2.0) for x in range(5)] for y in range(6)]

#Get random layout
def get_random_layout():
    # A layout is dictionary of key symbols(a to z) to it's (row,column) matrix
    card_shuffle = [(x,y) for x in range(6) for y in range(5)]
    random.shuffle(card_shuffle)

    layout = {}
    i=0
    for lt in string.ascii_lowercase:
        layout[lt] = card_shuffle[i]
        i+=1

    # Since there are 30 slots for a 6*5 keyboard
    # we use dummy keys to stuff remaining keys
    layout['1'] = card_shuffle[-1]
    layout['2'] = card_shuffle[-2]
    layout['3'] = card_shuffle[-3]
    layout['4'] = card_shuffle[-4]

    return layout

#Construct the diagram table given data_path
def makeDiagramTable(data_path):
    fp = open(data_path)
    content = fp.readlines()
    fp.close()

    words=[]
    frequency=[]

    for line in content:
        w,f=((line.strip().split("\t")))
        words.append(w)
        frequency.append(int(f))

    tbl = {}
    #Assigning frequencies
    for i in range(len(words)):
        l = len(words[i])
        for j in range(l):
            if j+1==l:
                break
            s = ""+ words[i][j]+words[i][j+1]
            tup = (words[i][j],words[i][j+1])
            if tup in tbl:
                tbl[tup]+=frequency[i]
            else:
                tbl[tup] = frequency[i]

    total_frequency = 0
    for v in tbl:
        total_frequency += tbl[v]

    #Evaluating and storing probabilities
    for v in tbl:
        tbl[v]= float(tbl[v]/total_frequency)
    print("digram table:")
    print(tbl)

    return tbl

#Implement the Fitt's law given W and D
def FittsLaw(W,D):
    a = 0.083
    b = 0.127
    return a+(b*m.log(((D/W)+1),2))

#Computer the average movement time
def computeAMT(layout,digram_table):
    MT = 0
    for i in range(26):
        key1 = chr(ord('a')+i)
        for j in range(26):
            if i==j:
                continue
            key2 = chr(ord('a')+j)

            comb = (key1,key2)

            if comb in digram_table:
                a,b = (layout[key1])
                c,d = (layout[key2])
                D = pow(pow((a-c),2)+pow((b-d),2),0.5)
                W = 1
                P = digram_table[comb]
                MT= MT+P*FittsLaw(W,D)
    return MT

# Performing Simulation Annealing given num_iter iterations and random start number
def SA(num_iter,num_random_start,tbl):

    final_result=({},0,0)
    r=0
    optimalCost = sys.maxsize
    optimalLayout = {}
    start_time = time.time()
    while r < num_random_start:
        if time.time()>start_time+560:
            # Condition to terminate program and return layout in case of very large output if it exceeds about 10 minutes deadline.
            # The result will have a very high probability of being optimal as the program iterates upto 2*10^6 times
            # before terminating after 10 minutes. So this can be considered as solution.
            print("Program terminated as time exceeded 10 mintues. It ran for "+str(r-1)+" outer randomized layouts")
            return (optimalLayout,optimalCost)
        starting_state = get_random_layout()
        k = 0
        optimalLayout_iter = starting_state
        cost = computeAMT(starting_state,tbl)
        while k<num_iter:
            randomKey1 = chr(ord('a') + random.randint(0,25))
            randomKey2 = chr(ord('a') + random.randint(0,25))
            while randomKey2==randomKey1:
                randomKey2 = chr(ord('a') + random.randint(0,25))
            temp = starting_state[randomKey1]
            starting_state[randomKey1] = starting_state[randomKey2]
            starting_state[randomKey2] = temp
            cost_iter = computeAMT(starting_state,tbl)
            if cost_iter<cost:
                cost = cost_iter
                optimalLayout_iter = starting_state
            k = k+1
        if cost<optimalCost:
            optimalCost = cost
            optimalLayout = optimalLayout_iter
        r= r+1
        #print(optimalCost,cost)

        #---------- you should return a tuple of (optimal_layout, optimal_MT)-------
    final_result = (optimalLayout,optimalCost)
    return final_result

def printlayout(layout):
    # use this function to print the layout
    keyboard = [[[] for x in range(5)] for y in range(6)]
    for k in layout:
        r = layout[k][0]
        c = layout[k][1]
        keyboard[r][c].append(k)

    for r in range(6):
        row = ''
        for c in range(5):
            row += keyboard[r][c][0]+' '
        print(row)

if __name__ == '__main__':
    if len(sys.argv)!=4:
        print("usage : hw1.py [num_SA_iteration] [num_SA_random_start] [dataset_path]")
        exit(0)
    k = int(sys.argv[1])
    rs = int(sys.argv[2])
    data_path = sys.argv[3]

    #Test Fitt's law
    print(FittsLaw(10,10))
    print(FittsLaw(20,5))
    print(FittsLaw(10.5,1))

    #Construct Digram table
    tbl = makeDiagramTable(data_path)

    #Run SA
    result,cost = SA(k,rs,tbl)
    print("Optimal MT:",cost)
    printlayout(result)