import pygame
import numpy
import equations
from pathlib import Path

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
FOV_VERTICAL = numpy.pi / 4
FOV_HORIZONTAL = FOV_VERTICAL * SCREEN_WIDTH / SCREEN_HEIGHT

simulation = equations.BlackHoleData()
initial_distance = simulation.calculate_separation_over_time(0)
t = 0
orbital_phase = 0.0

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    surface = pygame.surface.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    base_directory = Path(__file__).resolve().parent
    mesh_path = base_directory / "meshes" / "cube.obj"
    points, triangles = read_obj(mesh_path)
    camera = numpy.asarray([0, 0, -20, 0, 0]) # the 4th and 5th entry are horizontal and vertical rotation
    rotation_angle = 0.0
    orbital_angle = 0.0

    while running:
        surface.fill([0, 0, 0])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        rotation_angle += 0.01
        # orbital_angle += 0.01

        rotated_points = rotate_vertices_y(points, rotation_angle, orbital_angle)
        project_points(rotated_points, camera)

        for index in range(len(triangles)):
            triangle = [rotated_points[triangles[index][0]][3:], rotated_points[triangles[index][1]][3:], rotated_points[triangles[index][2]][3:]]
            color = (255, 255 ,255)
            pygame.draw.polygon(surface, color, triangle)

        screen.blit(surface, (0, 0))
        pygame.display.update()
        # camera = camera + numpy.asarray([0, 0, 0, 0, 0])
        clock.tick(120)

def project_points(points, camera):
    """
    camera = [x, y, z, yaw, pitch]
    yaw   = horizontal rotation (radians)
    pitch = vertical rotation (radians)
    """

    aspect = SCREEN_WIDTH / SCREEN_HEIGHT
    f = 1 / numpy.tan(FOV_VERTICAL / 2)

    cos_yaw = numpy.cos(-camera[3])
    sin_yaw = numpy.sin(-camera[3])

    cos_pitch = numpy.cos(-camera[4])
    sin_pitch = numpy.sin(-camera[4])

    for point in points:

        # translate into camera space
        x = point[0] - camera[0]
        y = point[1] - camera[1]
        z = point[2] - camera[2]

        # rotate around Y (yaw)
        x2 = x * cos_yaw - z * sin_yaw
        z2 = x * sin_yaw + z * cos_yaw

        # rotate around X (pitch)
        y2 = y * cos_pitch - z2 * sin_pitch
        z3 = y * sin_pitch + z2 * cos_pitch

        # behind camera?
        if z3 <= 0.01:
            point[3] = -10000
            point[4] = -10000
            continue

        # perspective divide
        ndc_x = (x2 * f / aspect) / z3
        ndc_y = (y2 * f) / z3

        point[3] = (ndc_x + 1) * SCREEN_WIDTH / 2
        point[4] = (1 - ndc_y) * SCREEN_HEIGHT / 2


def rotate_vertices_y(points, spin_angle, orbit_angle):
    rotated_points = points.copy()

    center_x = numpy.mean(points[:, 0])
    center_z = numpy.mean(points[:, 2])

    cos_s, sin_s = numpy.cos(spin_angle), numpy.sin(spin_angle)
    cos_o, sin_o = numpy.cos(orbit_angle), numpy.sin(orbit_angle)

    orbit_radius = 0  # distance from the rotation center

    for point in rotated_points:
        # spin the vertex around the cube's own local center
        x_local = point[0] - center_x
        z_local = point[2] - center_z

        spun_x = x_local * cos_s - z_local * sin_s
        spun_z = x_local * sin_s + z_local * cos_s

        # push the spun cube out to its orbital radius
        x_orbit = spun_x + orbit_radius
        z_orbit = spun_z

        # rotate that entire orbital position around the world origin (0, 0)
        new_x = x_orbit * cos_o - z_orbit * sin_o
        new_z = x_orbit * sin_o + z_orbit * cos_o

        point[0] = new_x
        point[2] = new_z

    return rotated_points

def read_obj(file_name):
    vertices = []
    triangles = []

    with open(file_name, "r") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue

            if parts[0] == "v":
                vertex = [float(parts[1]), float(parts[2]), float(parts[3]), 1, 1]
                vertices.append(vertex)

            elif parts[0] == "f":
                v1 = int(parts[1].split('/')[0]) - 1
                v2 = int(parts[2].split('/')[0]) - 1
                v3 = int(parts[3].split('/')[0]) - 1
                triangles.append([v1, v2, v3])

                if len(parts) > 4:
                    v4 = int(parts[4].split('/')[0]) - 1
                    triangles.append([v1, v3, v4])

    return numpy.asarray(vertices), numpy.asarray(triangles)

if __name__ == '__main__':
    main()
    pygame.quit()