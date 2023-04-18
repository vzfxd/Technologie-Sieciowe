#c - funkcja przepustowości (maksymalna liczba bitów, którą można wprowadzić do kanału komunikacyjnego w ciągu sekundy)
#a - funckja przepływu (faktyczna liczba pakietów, które wprowadza się do kanału komunikacyjego w ciągu sekundy)

#macierz N - macierz  macierz natężeń strumienia pakietów, 
#gdzie element n(i,j) jest liczbą pakietów przesyłanych (wprowadzanych do sieci) w ciągu sekundy od źródła v(i) do ujścia v(j).

#podpunkt 1
#Zaproponuj topologię grafu G ale tak aby żaden wierzchołek nie był izolowany oraz aby: |V|=20, |E|<30, a, c
#

import networkx as nx
import matplotlib.pyplot as plt
import random
import argparse
import math

_edges = [(1,2),(1,3),(1,4),(2,5),(3,5),(4,6),(4,7),(5,8),(6,9),(6,10),(7,11),(8,12),(9,13),
          (10,13),(11,14),(12,15),(12,16),(13,17),(14,18),(14,19),(15,20),(16,20),(17,18),(17,19),(18,20),(19,20)]

_edges2 = [(1,2),(1,3),(1,4),(2,5),(2,6),(3,6),(3,7),(4,8),(4,9),(5,10),(5,11),(6,12),(7,12),
           (7,13),(8,14),(9,14),(9,15),(10,16),(11,16),(11,17),(12,18),(13,18),(13,19),(14,20),(15,20),(16,19),(17,18),(17,20), (19,20)]

class Edge:
    def __init__(self,v,c):
        self.v = v
        self.c = c              #przepustowość
        self.a = 0              #przepływ
        self.enabled = True

class Network:
    def __init__(self,edges,m=10,pr=0.97,max_packets=10):
        self.edges = [Edge(v,10_000) for v in edges]
        self.m = m
        self.max_packets = max_packets
        self.nodes = []
        self.pr = pr
        for edge in edges:
            for node in edge:
                if(node not in self.nodes):self.nodes.append(node)
        self.matrix = self.gen_matrix(len(self.nodes))
        self.G = sum([sum(row) for row in self.matrix])
        self.T = 0
        self.graph = nx.Graph()
        self.graph.add_edges_from(edges)
        self.failures = 0

    def shortest_path(self,v_sc,v_dst,packets):
        new_graph = nx.Graph()
        #krawedzie dla ktorych ( packets + a(e) )*m < c(e)
        new_edges = [edge.v for edge in self.edges if(edge.enabled and (packets+edge.a)*self.m<edge.c)]
        new_graph.add_nodes_from(self.nodes)
        new_graph.add_edges_from(new_edges)
        return nx.shortest_path(new_graph,v_sc,v_dst)
    
    def gen_matrix(self,n):
        #Macierz natężeń 
        matrix = [[random.randint(1,self.max_packets) if x!=y else 0 for x in range(n)] for y in range(n)]
        return matrix
    
    def find_edge(self,v):
        for edge in self.edges:
            if(edge.v == v or edge.v==(v[1],v[0])):
                return edge
    
    def update_graph(self):
        for edge in self.edges:
            edge.a = 0
            pr = random.random()
            edge.enabled = pr < self.pr
        
        self.graph.clear_edges()
        self.graph.add_edges_from([edge.v for edge in self.edges if edge.enabled])
    
    def gen_a(self):
        self.update_graph()
        if(nx.is_connected(self.graph)==False):
            self.failures += 1
        for i,row in enumerate(self.matrix):
            for idx,packets in enumerate(row):
                try:
                    while(packets>0):
                        path = self.shortest_path(i+1,idx+1,1)
                        path_edges = [self.find_edge((path[x-1],path[x])) for x in range(1,len(path))]
                        packets_sent =  math.ceil(min([(edge.c/self.m)-edge.a for edge in path_edges])-1)
                        if(packets_sent>packets):
                            packets_sent = packets
                        for edge in path_edges:
                            edge.a+=packets_sent
                        packets-=packets_sent
                except nx.NetworkXNoPath as e:
                    pass
        self.T = (1 / self.G) * sum(edge.a / ((edge.c / self.m) - edge.a) for edge in self.edges)
    
    def reliability(self,t_max,rep):
        self.failures = 0
        success = 0
        delay = 0
        for i in range(rep):
            failures = self.failures
            self.gen_a()
            if(self.T<t_max and failures == self.failures):
                success += 1
            if(self.T>=t_max):
                delay += 1
        return [round(success/rep*100,2),round(self.failures/rep*100,2),round(delay/rep*100,2)]
    
    def add_edge(self):
        x = random.randint(1,20)
        y = random.randint(1,20)
        while(self.find_edge((x,y))==True):
            x = random.randint(1,20)
            y = random.randint(1,20)
        self.edges.append(Edge((x,y),10_000))

                        
parser = argparse.ArgumentParser(prog='Symulator Sieci')
parser.add_argument('--podpunkt',help="podpunkt do wyboru")
parser.add_argument('--t_max', help="maksymalne opoznienie")
parser.add_argument('--prawdopodobienstwo',help="prawdopodobieństwo nieuszkodzenia każdej krawędzi")
parser.add_argument('--topologia',help="wybor topologii")
args = parser.parse_args()

try:
    podpunkt = int(args.podpunkt)
except TypeError:
    podpunkt = 1

try:
    pr = float(args.prawdopodobienstwo)
except TypeError:
    pr = 0.95

try:
    t_max = float(args.t_max)
except TypeError:
    t_max = 1/100

try:
    topologia = int(args.topologia)
except TypeError:
    topologia = 1

if(topologia==1):
    edges = _edges
else:
    edges = _edges2
n = Network(edges,pr=pr)

if(podpunkt==1):
    n.gen_a()
    print("=== MACIERZ NATĘŻEŃ ===")
    for row in n.matrix:
        print(row)
    print("=== Funkcja Przepływu === ")
    for edge in n.edges:
        print(str(edge.v)+":"+str(edge.a))
elif(podpunkt==2):
    rel = n.reliability(t_max=t_max,rep=2500)
    print(f"Niezawodnosc sieci: {rel[0]}%")
    print(f"Procent rozspojnien sieci: {rel[1]}%")
    print(f"Procent przekroczenia opóźnienia: {rel[2]}%")
elif(podpunkt==3):
    for i in range(5,21,5):
        print(f"max liczba pakietów w macierzy:{i}")
        n.max_packets = i
        n.matrix = n.gen_matrix(len(n.nodes))
        rel = n.reliability(t_max=t_max,rep=2500)
        print(f"Niezawodnosc sieci: {rel[0]}%")
        print(f"Procent rozspojnien sieci: {rel[1]}%")
        print(f"Procent przekroczenia opóźnienia: {rel[2]}%\n")
elif(podpunkt==4):
    for i in range(5_000,11_000,1_000):
        for edge in n.edges:
            edge.c = i
        rel = n.reliability(t_max=t_max,rep=2500)
        print(f"Maksymalna przepustowość w krawędziach:{i}")
        print(f"Niezawodnosc sieci: {rel[0]}%")
        print(f"Procent rozspojnien sieci: {rel[1]}%")
        print(f"Procent przekroczenia opóźnienia: {rel[2]}%\n")
elif(podpunkt==5):
    print(f"liczba krawedzi:{len(n.edges)}")
    rel = n.reliability(t_max=t_max,rep=2500)
    print(f"Niezawodnosc sieci: {rel[0]}%")
    print(f"Procent rozspojnien sieci: {rel[1]}%")
    print(f"Procent przekroczenia opóźnienia: {rel[2]}%\n")
    for i in range(4):
        n.add_edge()
        n.add_edge()
        print(f"liczba krawedzi:{len(n.edges)}")
        rel = n.reliability(t_max=t_max,rep=2500)
        print(f"Niezawodnosc sieci: {rel[0]}%")
        print(f"Procent rozspojnien sieci: {rel[1]}%")
        print(f"Procent przekroczenia opóźnienia: {rel[2]}%\n")