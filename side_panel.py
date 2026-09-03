import pygame
from equations import BlackHoleData

class SidePanel:
    def __init__(self, simulation:BlackHoleData, clock, width, height, surface):
        self.simulation = simulation
        self.clock = clock
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 25)
        self.surface = surface
        self.title_text = self.font.render("DATA PANEL:", True, (255, 255, 255))
        self.elapsed_time = None
        self.current_distance = None
        self.orbital_phase = None
        self.angular_frequency = None
        self.h_cross = None
        self.h_plus = None
        self.newtonian_velocity = None
        self.relativistic_velocity = None
        self.difference = None


    def update(self):
        text = []

        text.append(self.title_text)
        text.append(self.font.render(f"Time elapsed: {self.elapsed_time:.4f}s", True, (255, 255, 255)))
        text.append(self.font.render(f"Current distance: {int(self.current_distance)}m", True,(255, 255, 255)))
        text.append(self.font.render(f"Orbital phase: {self.orbital_phase:.4f} radians", True,(255, 255, 255)))
        text.append(self.font.render(f"Angular frequency: {self.angular_frequency:.4f} radians", True,(255, 255, 255)))
        text.append(self.font.render(f"H cross: {self.h_cross:e}", True, (255, 255, 255)))
        text.append(self.font.render(f"H plus: {self.h_plus:e}", True, (255, 255, 255)))
        text.append(self.font.render(f"Newtonian velocity: {int(self.newtonian_velocity)} m/s", True, (255, 255, 255)))
        text.append(self.font.render(f"Relativistic velocity: {int(self.relativistic_velocity)} m/s", True, (255, 255, 255)))
        text.append(self.font.render(f"Velocity difference: {int(self.difference)} m/s", True, (255, 255, 255)))

        panel_rect_outline = pygame.rect.Rect(0, 0, 325, 1000)
        pygame.draw.rect(self.surface, (255, 255, 255), panel_rect_outline)
        panel_rect = pygame.rect.Rect(0, 0, 320, 1000)
        pygame.draw.rect(self.surface, (0, 0, 0), panel_rect)

        pos = 5
        for item in text:
            self.surface.blit(item, (5, pos))
            pos += 30
