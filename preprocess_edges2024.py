import shapefile  # Import the pyshp library
import pickle
import json

edges=pickle.load(open("edges.pickle","rb"))

def degrees(nodes):
    degrees={}
    for key in nodes:
        connections=nodes[key]
        if len(connections) not in degrees:
            degrees[len(connections)]=0
        degrees[len(connections)]+=1
    return degrees

def remove_nonintersections(nodes):
    to_remove=[]
    for key in nodes:
        connections=nodes[key]
        if len(connections)==2:
            to_remove.append(key)
            left,right=connections
            nodes[left].remove(key)
            nodes[left].append(right)
            nodes[right].remove(key)
            nodes[right].append(left)
    for key in to_remove:
        del nodes[key]

def trim_deadend(nodes):
    deadends=[]
    for key in nodes:
        connections=nodes[key]
        if len(connections)==1:
            deadends.append(key)
    for deadend in deadends:
        # ~ print("deadend",deadend)
        # ~ print(nodes[deadend])
        if len(nodes[deadend])==0:
            del nodes[deadend]
            continue
        connection=nodes[deadend][0]
        # ~ print(nodes[connection])
        # ~ input()
        del nodes[deadend]
        nodes[connection].remove(deadend)
    remove_empties(nodes)

def remove_empties(nodes):
    empties=[]
    for key in nodes:
        connections=nodes[key]
        if len(connections)==0:
            empties.append(key)
    for key in empties:
        del nodes[key]


nodes={} #ADJACENCY LIST

for p1,p2 in edges:
    p1=tuple(p1)
    p2=tuple(p2)
    if p1 not in nodes:
        nodes[p1]=[]
    if p2 not in nodes:
        nodes[p2]=[]
    nodes[p1].append(p2)
    nodes[p2].append(p1)
# ~ print(nodes)
for i in range(25):
    print(degrees(nodes))
    trim_deadend(nodes)
remove_nonintersections(nodes)
print(degrees(nodes))

json_nodes={str(key):[list(point) for point in nodes[key]] for key in nodes}

# Writing to sample.json
pickle.dump(nodes,open("roads_processed.pickle","wb"))

with open("roads_processed.json","w") as outfile:
	outfile.write(json.dumps(json_nodes,indent=4))
