import pickle
import json
import turtle
import math
import cv2
import numpy as np
import heapq

class PriorityQueue:
    def __init__(self):
        self.q = []
        self.lookup = {}
        self.i = 0

    def add(self, cost, elem):
        if elem in self.lookup:
            if self.lookup[elem][0] > cost:
                self.remove(elem)
            else:
                return
        entry = [cost, -self.i, elem]
        self.i += 1
        heapq.heappush(self.q, entry)
        self.lookup[elem] = entry

    def pop(self):
        elem = False
        while not elem:
            cost, _, elem = heapq.heappop(self.q)
        self.lookup.pop(elem)
        return elem

    def remove(self, elem):
        entry = self.lookup.pop(elem)
        entry[-1] = False

    def __len__(self):
        return len(self.lookup)

def heuristic(x, y):
    return math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)



width=270*2
length=240*2

def find_closest(point,nodes):
    x1,y1=point
    dist=100000000
    closest=None
    for x2,y2 in nodes:
        d=math.hypot(x1-x2,y1-y2)
        if d<dist:
            dist=d
            closest=(x2,y2)
    return closest

nodes=pickle.load(open("roads_processed.pickle","rb"))

maxx=-10000000000
maxy=-10000000000
minx=10000000000
miny=10000000000
for x,y in nodes:
    if x<minx:
        minx=x
    if x>maxx:
        maxx=x
    if y<miny:
        miny=y
    if y>maxy:
        maxy=y
print(minx,maxx,miny,maxy)

def scale_point(point):
    x,y=point
    x=(x-minx)/(maxx-minx)*width
    y=length-(y-miny)/(maxy-miny)*length
    return x,y

import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the canvas
canvas_size = (width, length)
screen = pygame.display.set_mode(canvas_size)
pygame.display.set_caption("Draw Lines")


def draw_line(point1,point2,color=(0,0,0),width=1):
    scaled_point1=scale_point(point1)
    scaled_point2=scale_point(point2)
    pygame.draw.line(screen, color, scaled_point1, scaled_point2, width)

# Set up colors
white = (255, 255, 255)
screen.fill(white)
for point1 in nodes:
    for point2 in nodes[point1]:
        draw_line(point1,point2)
        
pygame.display.flip()

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = 30
video_writer = cv2.VideoWriter('output.mp4', fourcc, fps, canvas_size)


start=(-9305798,3451807)
start=find_closest(start,nodes)

end = (-9251404, 3508924)
# (longitude, lattitude)
end = find_closest(end,nodes)

# Draw the end point
scaled_end = scale_point(end)
end_point_color = (255, 0, 0)
point_radius = 5
pygame.draw.circle(screen, end_point_color, scaled_end, point_radius)
pygame.display.flip()

explored=set()
queue=[start]
queue = PriorityQueue()
queue.add(0, start)
running=True
i=0
j=0
parents = {}
costs = {}
costs[start] = 0
while queue and running:
    point=queue.pop()
    if point == end:
        break
    j+=1
    cost = costs[point]
    explored.add(point)
    for point2 in nodes[point]:
        if point2 not in explored:
            point2_cost = cost + 1
            if point2 not in costs or point2_cost < costs[point2]:
                # print(f"point{point2}")
                costs[point2] = point2_cost
                parents[point2] = point
                queue.add(point2_cost + heuristic(point2, end), point2)
                draw_line(point,point2,(0,0,255),3)
                i+=1
            if i%1==0:
                pygame.display.flip()
                frame = pygame.surfarray.array3d(screen)
                frame = np.swapaxes(frame, 0, 1)
                video_writer.write(frame)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Set up the color and width for the traceback path
traceback_color = (0, 255, 0)  # Green color
traceback_width = 3

# Trace back from the end to the start
import math

def haversine(coord1, coord2):
    # Radius of the Earth in km
    R = 6371.0
    
    # Coordinates in decimal degrees (e.g. (-9251404, 3508924))
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    lon1 = lon1/100000
    lat1 = lat1/100000
    lon2 = lon2/100000
    lat2 = lat2/100000
    
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    
    # Difference in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

distance = 0

current_point = end
while current_point != start:
    predecessor = parents[current_point]
    distance += haversine(current_point, predecessor)
    draw_line(current_point, predecessor, traceback_color, traceback_width)
    current_point = predecessor
    pygame.display.flip()
    frame = pygame.surfarray.array3d(screen)
    frame = np.swapaxes(frame, 0, 1)
    video_writer.write(frame)

for i in range(150):
    video_writer.write(frame)

print(f"Total distance: {distance:.2f} km")
video_writer.release()

pixels = pygame.surfarray.array3d(screen)
pixels = pixels.transpose([1, 0, 2])
pixels = cv2.cvtColor(pixels, cv2.COLOR_RGB2BGR)
cv2.imwrite('output.png', pixels)

pygame.quit()
sys.exit()