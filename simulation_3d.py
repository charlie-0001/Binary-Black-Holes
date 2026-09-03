from equations import BlackHoleData
from side_panel import SidePanel
import pygame
import numpy
from pathlib import Path

pygame.init()
pygame.display.set_caption("3D Binary Black Hole Merger")
clock = pygame.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = 1350, 1000
surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
ring_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
game_font = pygame.font.Font(None, 30)

my_image = pygame.image.load("images/cosmos.png").convert()

PANEL_OFFSET = SCREEN_WIDTH - 1000
FOV = 400
camera_distance = 4.0
camera_pitch = 0.0
camera_x = 0.0
camera_y = 0.0
mouse_x, mouse_y = pygame.mouse.get_pos()

LIGHT_DIR = numpy.array([0.577, -0.577, 0.577]) * 3


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


def transform_and_collect_faces(all_faces, vertices, edges, x, y, z, orbital_radius_x, orbital_radius_y, orbital_radius_z, phase, alpha = 0):
    """transforms vertices and pushes processed faces to a render list."""
    orbit_x = numpy.cos(phase) * orbital_radius_x
    orbit_y = numpy.sin(phase) * orbital_radius_y
    orbit_z = numpy.sin(phase) * orbital_radius_z

    rot_matrix = get_rotation_matrix(x, y, z)
    cos_pitch = numpy.cos(camera_pitch)
    sin_pitch = numpy.sin(camera_pitch)

    world_points = {}
    projected_points = {}

    for i, vertex in enumerate(vertices):
        rotated = numpy.dot(rot_matrix, vertex)

        world_x = rotated[0] + orbit_x
        world_y = rotated[1] + orbit_y
        world_z = rotated[2] + orbit_z

        pitched_x = world_x
        pitched_y = world_y * cos_pitch - world_z * sin_pitch
        pitched_z = world_y * sin_pitch + world_z * cos_pitch

        world_points[i] = numpy.array([pitched_x, pitched_y, pitched_z])

        z_depth = pitched_z + camera_distance
        if z_depth <= 0.1: z_depth = 0.1

        x_proj = int(((pitched_x - camera_x) * FOV) / z_depth) + SCREEN_WIDTH // 2 + PANEL_OFFSET
        y_proj = int(((pitched_y - camera_y) * FOV) / z_depth) + SCREEN_HEIGHT // 2

        projected_points[i] = (x_proj, y_proj)

    for face, face_color in edges:
        p1_w, p2_w, p3_w = world_points[face[0]], world_points[face[1]], world_points[face[2]]
        avg_z = (p1_w[2] + p2_w[2] + p3_w[2]) / 3.0

        p1 = projected_points[face[0]]
        p2 = projected_points[face[1]]
        p3 = projected_points[face[2]]

        # skip faces outside the screen bounding box
        if (max(p1[0], p2[0], p3[0]) < 0 or min(p1[0], p2[0], p3[0]) > SCREEN_WIDTH or
                max(p1[1], p2[1], p3[1]) < 0 or min(p1[1], p2[1], p3[1]) > SCREEN_HEIGHT):
            continue

        v1 = p2_w - p1_w
        v2 = p3_w - p1_w
        normal = numpy.cross(v1, v2)
        norm_length = numpy.linalg.norm(normal)

        if norm_length > 0:
            normal = normal / norm_length

        intensity = numpy.dot(normal, LIGHT_DIR)
        intensity = max(0.2, min(1.0, intensity + 0.2))

        shaded_color = (
            int(face_color[0] * intensity),
            int(face_color[1] * intensity),
            int(face_color[2] * intensity),
            alpha
        )

        all_faces.append((avg_z, p1, p2, p3, shaded_color, alpha))


def render_scene(black_hole_faces, ring_faces):
    # render background
    surface.fill((0, 0, 0))
    surface.blit(my_image, (0, 0))

    # render black holes first
    black_hole_faces.sort(key=lambda item: item[0], reverse=True)

    for _, p1, p2, p3, shaded_color, alpha in black_hole_faces:
        pygame.draw.polygon(
            surface,
            (shaded_color[0], shaded_color[1], shaded_color[2]),
            [p1, p3, p2]
        )

    # clear ring surface
    ring_surface.fill((0, 0, 0, 0))

    # render rings on transparent surface
    ring_faces.sort(key=lambda item: item[0], reverse=True)

    for _, p1, p2, p3, shaded_color, alpha in ring_faces:
        pygame.draw.polygon(
            ring_surface,
            shaded_color,
            [p1, p3, p2]
        )

    # put transparent rings above black holes
    surface.blit(ring_surface, (0, 0))


def read_object(obj, mtl):
    vertices = []
    edges = []
    materials = {}
    current_color = (200, 200, 200)

    current_mtl = None
    with open(mtl) as file:
        for line in file:
            parsed = line.split()
            if not parsed: continue
            if parsed[0] == "newmtl":
                current_mtl = parsed[1]
            elif parsed[0] == "Kd" and current_mtl:
                r = int(float(parsed[1]) * 255)
                g = int(float(parsed[2]) * 255)
                b = int(float(parsed[3]) * 255)
                materials[current_mtl] = (r, g, b)

    with open(obj) as file:
        for line in file:
            parsed = line.split()
            if not parsed: continue

            if parsed[0] == "usemtl":
                mtl_name = parsed[1]
                current_color = materials.get(mtl_name, (200, 200, 200))

            elif parsed[0] == "v":
                vertices.append([float(parsed[1]), float(parsed[2]), float(parsed[3])])

            elif parsed[0] == "f":
                ids = []
                for string in parsed[1:]:
                    vertex_index = string.split('/')[0]
                    new_id = int(vertex_index) - 1
                    ids.append(new_id)

                if len(ids) == 3:
                    edges.append((ids, current_color))
                elif len(ids) == 4:
                    edges.append(([ids[0], ids[1], ids[2]], current_color))
                    edges.append(([ids[0], ids[2], ids[3]], current_color))

    return numpy.array(vertices, float), edges


vertices, edges = read_object(Path(__file__).parent / "meshes" / "black_hole.obj", Path(__file__).parent / "meshes" / "black_hole.mtl")
ring_vertices, ring_edges = read_object(Path(__file__).parent / "meshes" / "ring.obj", Path(__file__).parent / "meshes" / "ring.mtl")

simulation = BlackHoleData()
side_panel = SidePanel(simulation, clock, 350, 500, surface)

VISUAL_SCALE = 3.0 / (simulation.initial_distance / 2)

angle_x, angle_y, angle_z = 0, 0, 0
elapsed_time = 0.0
orbital_phase = 0.0

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

    current_distance = simulation.calculate_separation_over_time(elapsed_time)

    if current_distance <= 0:
        print(f"t={elapsed_time:.4f}s: Black holes have merged!")
        running = False
        continue

    angular_frequency = simulation.get_angular_frequency(current_distance)
    orbital_phase += angular_frequency * dt

    physics_radius = current_distance / 2
    visual_radius = physics_radius * VISUAL_SCALE

    # collect faces separately so rings can always be rendered above black holes
    black_hole_faces = []
    ring_faces = []

    transform_and_collect_faces(
        black_hole_faces, vertices, edges,
        angle_x, angle_y, angle_z,
        visual_radius, visual_radius, 0,
        orbital_phase,
        255
    )

    transform_and_collect_faces(
        black_hole_faces, vertices, edges,
        angle_x, angle_y, angle_z,
        visual_radius, visual_radius, 0,
        orbital_phase + numpy.pi,
        255
    )

    transform_and_collect_faces(
        ring_faces, ring_vertices, ring_edges,
        angle_x, angle_y, angle_z,
        visual_radius, visual_radius, 0,
        orbital_phase,
        50
    )

    transform_and_collect_faces(
        ring_faces, ring_vertices, ring_edges,
        angle_x, angle_y, angle_z,
        visual_radius, visual_radius, 0,
        orbital_phase + numpy.pi,
        50
    )

    h_cross = simulation.waveform_over_time_cross(elapsed_time, orbital_phase)
    h_plus = simulation.waveform_over_time_plus(elapsed_time, orbital_phase)
    v_newton, v_rel, v_diff = simulation.calculate_velocity_difference(current_distance)

    side_panel.h_plus = h_plus
    side_panel.h_cross = h_cross
    side_panel.current_distance = current_distance
    side_panel.elapsed_time = elapsed_time
    side_panel.orbital_phase = orbital_phase
    side_panel.angular_frequency = angular_frequency
    side_panel.newtonian_velocity = v_newton
    side_panel.relativistic_velocity = v_rel
    side_panel.difference = v_diff

    render_scene(black_hole_faces, ring_faces)
    side_panel.update()

    angle_x += 0.025
    angle_y += 0.01
    angle_z += 0.02
    elapsed_time += dt

    pygame.display.flip()
    clock.tick(90)