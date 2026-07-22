import pygame
from equations import BlackHoleData, simulation

class SidePanel:
    def __init__(self, simulation:BlackHoleData, clock, width, height, surface):
        self.simulation = simulation
        self.clock = clock
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 30)
        self.surface = surface
        self.elapsed_time = None
        self.current_distance = None
        self.orbital_phase = None
        self.h_cross = None
        self.h_plus = None


    def update(self):
        elapsed_time_text = self.font.render(f"Time elapsed: {self.elapsed_time:.4f}s", True, (255, 255, 255))
        current_distance_text = self.font.render(f"Current distance: {int(self.current_distance)}m", True,
                                                 (255, 255, 255))
        orbital_phase_text = self.font.render(f"Orbital phase: {self.orbital_phase:.4f} radians", True,
                                              (255, 255, 255))
        h_cross_text = self.font.render(f"H cross: {self.h_cross:e}", True, (255, 255, 255))
        h_plus_text = self.font.render(f"H plus: {self.h_plus:e}", True, (255, 255, 255))

        panel_rect_outline = pygame.rect.Rect(0, 0, 325, 150)
        pygame.draw.rect(self.surface, (255, 255, 255), panel_rect_outline, border_bottom_right_radius=10)
        panel_rect = pygame.rect.Rect(0, 0, 320, 145)
        pygame.draw.rect(self.surface, (0, 0, 0), panel_rect, border_bottom_right_radius=10)


        self.surface.blit(current_distance_text, (0, 0))
        self.surface.blit(elapsed_time_text, (0, 30))
        self.surface.blit(orbital_phase_text, (0, 60))
        self.surface.blit(h_cross_text, (0, 90))
        self.surface.blit(h_plus_text, (0, 120))