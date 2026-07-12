import sys
import pygame
import numpy
import equations

on = False

if on:
    bh1 = None
    simulation = equations.BlackHoleData()
    initial_distance = simulation.calculate_separation_over_time(0)
    t = 0
    orbital_phase = 0.0

    pygame.init()

    window = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()

    SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 1000
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        surface.fill(color=(0,0,0))

        current_distance = simulation.calculate_separation_over_time(t)

        r_current = current_distance / 2

        bh1_x = 500 - r_current * numpy.cos(orbital_phase) / initial_distance * 500
        bh1_y = 500 - r_current * numpy.sin(orbital_phase) / initial_distance * 500

        bh2_x = 500 + r_current * numpy.cos(orbital_phase) / initial_distance * 500
        bh2_y = 500 + r_current * numpy.sin(orbital_phase) / initial_distance * 500


        dt = 0.00025
        t += dt #time elapsed per frame (tick, currently 120 per second)

        if current_distance != 0:
            omega_current = numpy.sqrt(
                (simulation.gravitational_constant * (simulation.bh1_mass + simulation.bh2_mass))
                / (current_distance ** 3)
            )

            orbital_phase += omega_current * dt
        else:
            print("Black holes have merged!")
            running = False

        bh1 = pygame.draw.circle(surface=surface, color=(255,255,255), center=(bh1_x,bh1_y), radius=50)
        bh2 = pygame.draw.circle(surface=surface, color=(255,255,255), center=(bh2_x,bh2_y), radius=50)

        pygame.display.flip()

        clock.tick(120)

    pygame.quit()
    sys.exit()