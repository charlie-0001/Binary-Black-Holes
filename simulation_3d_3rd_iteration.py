import numpy
import pygame
import numpy as np
from pathlib import Path

pygame.init()
window = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def read_object(path):
    vertices = []
    edges = []
    with open(path) as file:
        for line in file:
            parsed = line.split() # splits sentences based on white space. e.g. "hello world" turns into "hello" "world"
            if not parsed: continue
            if parsed[0] == "v":
                vertices.append([float(parsed[1]), float(parsed[2]), float(parsed[3])])

            elif parsed[0] == "f":
                ids = []
                for string in parsed[1:]:
                    vertex_index = string.split('/')[0]
                    new_id = int(vertex_index) - 1
                    ids.append(new_id)
                if len(ids) == 3: edges.append(ids)
                if len(ids) == 4:
                    edges.append([ids[0],ids[1],ids[2]])
                    edges.append([ids[0],ids[2],ids[3]])
    return numpy.array(vertices, float), numpy.array(edges, int)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False