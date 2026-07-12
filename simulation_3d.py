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

    # points = numpy.asarray([[1, 1, 1, 1, 1], [4, 2, 0, 1, 1], [1, 0.5, 3, 1, 1]])
    # triangles = numpy.asarray([[0, 1, 2]])

    base_directory = Path(__file__).resolve().parent
    mesh_path = base_directory / "meshes" / "cube.obj"
    points, triangles = read_obj(mesh_path)
    camera = numpy.asarray([13, 0.5, 2, 3.3, 0]) # the 4th and 5th entry are horizontal and vertical rotation
    rotation_angle = 0.0

    while running:
        surface.fill([0, 0, 0])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        rotation_angle += 0.01
        rotated_points = rotate_vertices_y(points, rotation_angle)
        project_points(rotated_points, camera)

        for index in range(len(triangles)):
            triangle = [rotated_points[triangles[index][0]][3:], rotated_points[triangles[index][1]][3:], rotated_points[triangles[index][2]][3:]]
            color = (255, 255 ,255)
            pygame.draw.polygon(surface, color, triangle)

        screen.blit(surface, (0, 0))
        pygame.display.update()
        camera = camera + numpy.asarray([0, 0, 0, 0, 0])
        clock.tick(120)

def project_points(points, camera):
    for point in points:
        h_angle_camera_point = numpy.arctan((point[2] - camera[2]) / (point[0] - camera[0] + 1e-16))
        if abs(camera[0] + numpy.cos(h_angle_camera_point) - point[0]) > abs(camera[0] - point[0]):
            h_angle_camera_point = (h_angle_camera_point - numpy.pi) % (2 * numpy.pi)
        h_angle = (h_angle_camera_point - camera[3]) % (2 * numpy.pi)
        if h_angle > numpy.pi: h_angle = h_angle - 2 * numpy.pi
        point[3] = SCREEN_WIDTH * h_angle / FOV_HORIZONTAL + SCREEN_WIDTH / 2
        distance = numpy.sqrt((point[0] - camera[0])**2 + (point[1] - camera[1]) ** 2 + (point[2] - camera[2]) ** 2)
        v_angle_camera_point = numpy.arcsin((camera[1] - point[1]) / distance)
        v_angle = (v_angle_camera_point - camera[4]) % (2 * numpy.pi)
        if v_angle > numpy.pi: v_angle = v_angle - 2 * numpy.pi
        point[4] = SCREEN_HEIGHT * v_angle / FOV_VERTICAL + SCREEN_HEIGHT / 2


def rotate_vertices_y(points, angle):
    rotated_points = points.copy()

    center_x = numpy.mean(points[:, 0])
    center_y = numpy.mean(points[:, 1])
    center_z = numpy.mean(points[:, 2])

    cos_a = numpy.cos(angle)
    sin_a = numpy.sin(angle)

    for point in rotated_points:
        # translate point back to origin (relative to its center)
        x = point[0] - center_x
        z = point[2] - center_z

        # apply y-axis rotation matrix math
        new_x = x * cos_a - z * sin_a
        new_z = x * sin_a + z * cos_a

        # translate back to original world position
        point[0] = new_x + center_x
        point[2] = new_z + center_z

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