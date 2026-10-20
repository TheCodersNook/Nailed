
import math
import pygame


class Camera:
    def __init__(self, surface, position=(0, 0, 2), sensitivity=0.15):
        self.core = surface.camera.core
        self.position = list(position)

        self.yaw = 0.0
        self.pitch = 0.0
        self.sensitivity = sensitivity
        self.speed = 8.0
        self.mouse_captured = True

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.update()

    def update(self):
        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)

        dx = math.sin(yaw) * math.cos(pitch)
        dy = math.cos(yaw) * math.cos(pitch)
        dz = math.sin(pitch)

        x, y, z = self.position

        self.core.setPos(x, y, z)
        self.core.lookAt(x + dx, y + dy, z + dz)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.mouse_captured = not self.mouse_captured
                pygame.event.set_grab(self.mouse_captured)
                pygame.mouse.set_visible(not self.mouse_captured)

        elif event.type == pygame.MOUSEMOTION and self.mouse_captured:
            dx, dy = event.rel

            self.yaw -= dx * self.sensitivity
            self.pitch -= dy * self.sensitivity
            self.pitch = max(-89, min(89, self.pitch))

            self.update()

    def move(self, dt):
        if not self.mouse_captured:
            return

        keys = pygame.key.get_pressed()

        yaw = math.radians(self.yaw)

        forward_x = math.sin(yaw)
        forward_y = math.cos(yaw)

        right_x = math.cos(yaw)
        right_y = -math.sin(yaw)

        speed = self.speed * dt

        if keys[pygame.K_w]:
            self.position[0] += forward_x * speed
            self.position[1] += forward_y * speed

        if keys[pygame.K_s]:
            self.position[0] -= forward_x * speed
            self.position[1] -= forward_y * speed

        if keys[pygame.K_d]:
            self.position[0] += right_x * speed
            self.position[1] += right_y * speed

        if keys[pygame.K_a]:
            self.position[0] -= right_x * speed
            self.position[1] -= right_y * speed

        if keys[pygame.K_SPACE]:
            self.position[2] += speed

        if keys[pygame.K_LCTRL]:
            self.position[2] -= speed

        self.update()
