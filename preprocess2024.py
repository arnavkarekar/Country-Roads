import shapefile  # Import the pyshp library
import pickle

# Replace 'your_shapefile.shp' with the path to your actual Shapefile
shape = shapefile.Reader("Trans_RoadSegment.zip")



# ~ # Accessing the shape records
shapes = shape.shapes()

# ~ pickle.dump((shapes,records),open("shape.pickle","wb"))
# ~ shapes,records=pickle.load(open("shape.pickle","rb"))

# Example: Print the first record's attributes and geometry
first_shape = shapes[0]

print("First Geometry (Shape):", first_shape)


edges=[]
maxx=0
minx=10000000000
maxy=0
miny=10000000000
# You can also iterate over all records and associated shapes
for shp in shapes:
    # ~ print("Record:", record)
    # ~ print("Geometry:", shape)
    # ~ if shape.shapeType not in types:
        # ~ types[shape.shapeType]=0
    # ~ types[shape.shapeType]+=1
    for start,end in zip(shp.parts,list(shp.parts[1:])+[len(shp.points)]):
        p1 = [int(t*100000) for t in shp.points[start]]
        p2 = [int(t*100000) for t in shp.points[end-1]]
        x,y=p1
        if x>maxx:
            maxx=x
        if x<minx:
            minx=x
        if y>maxy:
            maxy=y
        if y<miny:
            miny=y
        edges.append((p1,p2))
        # ~ print(p1,p2)
print("x",minx,maxx)
print("y",miny,maxy)
pickle.dump(edges,open("edges.pickle","wb"))
    
