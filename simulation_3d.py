import sys
import pygame
import numpy
import equations

simulation = equations.BlackHoleData()
initial_distance = simulation.calculate_separation_over_time(0)
t = 0
orbital_phase = 0.0