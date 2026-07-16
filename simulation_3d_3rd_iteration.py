from equations import BlackHoleData
import pygame
import numpy
from pathlib import Path

pygame.init()
pygame.display.set_caption("3D Rendering Engine")
window = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

FOV = 400
CAMERA_DISTANCE = 4.0

def get_rotation_matrix(ax, ay, az):
    """creates a combined 3d rotation matrix for x, y and z axes"""

    rx = numpy.array([
        [1, 0, 0],
        [0, numpy.cos(ax), -numpy.sin(ax)],
        [0, numpy.sin(ax), numpy.cos(ax)]
    ])

    ry = numpy.array([
        [numpy.cos(ay), 0, numpy.sin(ay)],
        [0, 1, 0],
        [-numpy.sin(ay), 0, numpy.cos(ay)]
    ])

    rz = numpy.array([
        [numpy.cos(az), -numpy.sin(az), 0],
        [numpy.sin(az), numpy.cos(az), 0],
        [0, 0, 1]
    ])

    return ry @ rx @ rz

def spin_object(vertices, edges, x, y, z, orbital_radius_x, orbital_radius_y, orbital_radius_z, time):
    projected_points = {}
    orbit_x = numpy.cos(time) * orbital_radius_x
    orbit_y = numpy.sin(time) * orbital_radius_y
    orbit_z = numpy.sin(time) * orbital_radius_z
    rot_matrix = get_rotation_matrix(x, y, z)

    for i, vertex in enumerate(vertices):
        rotated = numpy.dot(rot_matrix, vertex)  # dot product of rotation matrix and vertex. prints 3 items in an array.
        z_depth = rotated[2] + CAMERA_DISTANCE + orbit_z  # translate object so it sits in front of camera

        x_proj = int(((rotated[0] + orbit_x) * FOV) / z_depth) + SCREEN_WIDTH // 2
        y_proj = int(((rotated[1] + orbit_y) * FOV) / z_depth) + SCREEN_HEIGHT // 2

        projected_points[i] = (x_proj, y_proj)
        pygame.draw.circle(surface, (255, 255, 255), (x_proj, y_proj), 4)

    for face in edges:
        p1 = projected_points[face[0]]
        p2 = projected_points[face[1]]
        p3 = projected_points[face[2]]

        pygame.draw.polygon(surface, (255, 255, 255), [p1, p3, p2], 3)

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

vertices, edges = read_object(Path(__file__).parent/"meshes"/"icosphere.obj") # read the file
vertices2, edges2 = read_object(Path(__file__).parent/"meshes"/"cube.obj") # read the file

angle_x = 0
angle_y = 0
angle_z = 0

elapsed_time = 0
simulation = BlackHoleData()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    surface.fill((0, 0, 0))



    spin_object(vertices, edges, angle_x, angle_y, angle_z, 3, 3, 0, elapsed_time)

    angle_x += 0
    angle_y += 0
    angle_z += 0
    elapsed_time += 0.01

    pygame.display.flip()
    clock.tick(90)