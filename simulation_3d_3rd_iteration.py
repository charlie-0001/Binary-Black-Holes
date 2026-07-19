from equations import BlackHoleData
import pygame
import numpy
from pathlib import Path

pygame.init()
pygame.display.set_caption("3D Binary Black Hole Merger")
window = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

FOV = 400
camera_distance = 4.0
camera_pitch = 0.0
camera_x = 0.0
camera_y = 0.0
mouse_x, mouse_y = pygame.mouse.get_pos()

def get_rotation_matrix(ax, ay, az):
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


def spin_object(vertices, edges, x, y, z, orbital_radius_x, orbital_radius_y, orbital_radius_z, phase):
    projected_points = {}

    # X and Z create a horizontal flat orbit in 3D space
    orbit_x = numpy.cos(phase) * orbital_radius_x
    orbit_y = numpy.sin(phase) * orbital_radius_y
    orbit_z = numpy.sin(phase) * orbital_radius_z

    rot_matrix = get_rotation_matrix(x, y, z)

    cos_pitch = numpy.cos(camera_pitch)
    sin_pitch = numpy.sin(camera_pitch)

    for i, vertex in enumerate(vertices):
        rotated = numpy.dot(rot_matrix, vertex)

        world_x = rotated[0] + orbit_x
        world_y = rotated[1] + orbit_y
        world_z = rotated[2] + orbit_z

        pitched_x = world_x
        pitched_y = world_y * cos_pitch - world_z * sin_pitch
        pitched_z = world_z * sin_pitch + world_z * cos_pitch

        z_depth = pitched_z + camera_distance
        if z_depth <= 0.1: z_depth = 0.1

        x_proj = int(((pitched_x - camera_x) * FOV) / z_depth) + SCREEN_WIDTH // 2
        y_proj = int(((pitched_y - camera_y) * FOV) / z_depth) + SCREEN_HEIGHT // 2

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
            parsed = line.split()
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
                    edges.append([ids[0], ids[1], ids[2]])
                    edges.append([ids[0], ids[2], ids[3]])
    return numpy.array(vertices, float), numpy.array(edges, int)


vertices, edges = read_object(Path(__file__).parent / "meshes" / "icosphere.obj")

simulation = BlackHoleData()

# map the massive starting distance down to a visual radius of 3.0 on screen
initial_radius_actual = simulation.initial_distance / 2
VISUAL_SCALE = 3.0 / initial_radius_actual

angle_x, angle_y, angle_z = 0, 0, 0
elapsed_time = 0.0
orbital_phase = 0.0

# small dt to ensure math doesnt blow up
# while updating 90 times a second
dt = 0.0001

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        current_mouse_x, current_mouse_y = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        change_x = current_mouse_x - mouse_x
        change_y = current_mouse_y - mouse_y

        if mouse_buttons[0]:
            camera_distance += change_y / 50.0
            if camera_distance < 1.0: camera_distance = 1.0
            if camera_distance > 20.0: camera_distance = 20.0
        elif mouse_buttons[1]:
            camera_x -= change_x / 150.0
            camera_y -= change_y / 150.0
        elif mouse_buttons[2]:
            camera_pitch -= change_y / 150.0

        mouse_x, mouse_y = current_mouse_x, current_mouse_y

    surface.fill((0, 0, 0))

    current_distance = simulation.calculate_separation_over_time(elapsed_time)

    if current_distance <= 0:
        print(f"t={elapsed_time:.4f}s: Black holes have merged!")
        running = False
        continue

    omega_current = numpy.sqrt(
        (simulation.gravitational_constant * (simulation.bh1_mass + simulation.bh2_mass))
        / (current_distance ** 3)
    )

    orbital_phase += omega_current * dt

    physics_radius = current_distance / 2
    visual_radius = physics_radius * VISUAL_SCALE

    spin_object(
        vertices, edges,
        angle_x, angle_y, angle_z,
        visual_radius, visual_radius, 0,
        orbital_phase
    )

    spin_object(
        vertices, edges,
        angle_x, angle_y, angle_z,
        visual_radius, visual_radius, 0,
        orbital_phase + numpy.pi  # add 180 degrees so it's on the other side
    )

    angle_x += 0.01
    angle_y += 0.01
    elapsed_time += dt

    # print(current_distance)

    pygame.display.flip()
    clock.tick(90)