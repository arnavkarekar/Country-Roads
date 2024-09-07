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
print(start)
start=find_closest(start,nodes)
print(start)

end = (-9251404, 3508924)
end = find_closest(end,nodes)

# Draw the end point
scaled_end = scale_point(end)
end_point_color = (255, 0, 0)
point_radius = 3
pygame.draw.circle(screen, end_point_color, scaled_end, point_radius)
pygame.display.flip()

explored=set()
queue=[start]
running=True
i=0
predecessors = {}
while queue and running:
    point=queue.pop(0)
    explored.add(point)
    for point2 in nodes[point]:
        if point2 not in explored:
            queue.append(point2)
            predecessors[point2] = point
            if point2==end:
                print("Found")
                running=False
                break
            draw_line(point,point2,(0,0,255),3)
            i+=1
            if i%100000==0:
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
current_point = end
while current_point != start:
    predecessor = predecessors[current_point]
    draw_line(current_point, predecessor, traceback_color, traceback_width)
    current_point = predecessor

# Update the display to show the traceback path
pygame.display.flip()

# Optionally, save the frame that includes the traceback path
frame = pygame.surfarray.array3d(screen)
frame = np.swapaxes(frame, 0, 1)
video_writer.write(frame)

# Continue with releasing the video writer and quitting Pygame...

video_writer.release()

# Save the final picture to a file
#pygame.image.save(screen, "output.png")

# Quit Pygame
pygame.quit()
sys.exit()