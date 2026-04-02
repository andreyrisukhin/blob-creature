"""Blob creature demo — run with: python -m blob_game.main"""
from __future__ import annotations
import sys
import pygame
from blob_physics import BlobBody, BlobWorld, BlobController
from blob_renderer.renderer import draw_blob, draw_debug

WIDTH, HEIGHT = 800, 600
FPS = 60
PHYSICS_DT = 1.0 / 120.0
SUBSTEPS = 2

# Colors
BG_COLOR = (30, 30, 40)
TERRAIN_COLOR = (100, 100, 120)
TEXT_COLOR = (200, 200, 200)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Blob Creature")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 16)

    # Create world
    world = BlobWorld(gravity=(0, 400), bounds=(WIDTH, HEIGHT))

    # Add terrain: floor + a slope + a platform
    world.add_terrain_segment((0, HEIGHT - 20), (WIDTH, HEIGHT - 20))       # floor
    world.add_terrain_segment((200, HEIGHT - 20), (350, HEIGHT - 120))      # ramp
    world.add_terrain_segment((350, HEIGHT - 120), (500, HEIGHT - 120))     # platform
    world.add_terrain_segment((600, HEIGHT - 80), (750, HEIGHT - 80))       # floating platform

    # Create blob
    blob = BlobBody(
        center=(400, 200),
        radius=40,
        num_points=20,
        mass=1.0,
        spring_k=300.0,
        pressure=60.0,
        surface_tension=0.8,
    )
    world.add_blob(blob)

    controller = BlobController(move_force=250.0, jump_force=1000.0)
    show_debug = False
    gravity_strength = 400.0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    show_debug = not show_debug
                elif event.key == pygame.K_SPACE:
                    controller.apply_intent(blob, "jump")
                elif event.key == pygame.K_UP:
                    gravity_strength = max(0, gravity_strength - 50)
                    world.gravity.y = gravity_strength
                elif event.key == pygame.K_DOWN:
                    gravity_strength += 50
                    world.gravity.y = gravity_strength

        # Continuous input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            controller.apply_intent(blob, "roll_left")
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            controller.apply_intent(blob, "roll_right")

        # Physics
        for _ in range(SUBSTEPS):
            world.step(PHYSICS_DT)

        # Render
        screen.fill(BG_COLOR)

        # Draw terrain
        for seg_a, seg_b in world.terrain:
            pygame.draw.line(screen, TERRAIN_COLOR, (int(seg_a.x), int(seg_a.y)), (int(seg_b.x), int(seg_b.y)), 3)

        # Draw blob
        draw_blob(screen, blob)
        if show_debug:
            draw_debug(screen, blob)

        # HUD
        fps_text = font.render(f"FPS: {clock.get_fps():.0f}", True, TEXT_COLOR)
        grav_text = font.render(f"Gravity: {gravity_strength:.0f} (Up/Down)", True, TEXT_COLOR)
        area_text = font.render(f"Area: {blob.area():.0f} / {blob.target_area:.0f}", True, TEXT_COLOR)
        ctrl_text = font.render("A/D: move  Space: jump  Tab: debug  Up/Down: gravity", True, TEXT_COLOR)
        screen.blit(fps_text, (10, 10))
        screen.blit(grav_text, (10, 30))
        screen.blit(area_text, (10, 50))
        screen.blit(ctrl_text, (10, HEIGHT - 25))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
