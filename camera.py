
import math
import pygame
from panda3d.core import *

cameraradius = 0.35
minheight = 1.25
class Camera:
    def __init__(self, surface, position=(0, -5, 2), sensitivity=0.15):
        self.core = surface.camera.core
        self.position = list(position)

        self.yaw = 0.0
        self.pitch = 0.0
        self.sensitivity = sensitivity
        self.speed = 8.0
        self.mouse_captured = True

        self.root = self.core.getParent()
        self.traverser = CollisionTraverser()
        self.queue = CollisionHandlerQueue()
        collider = CollisionNode("playerone")
        collider.setFromCollideMask(BitMask32.allOn())
        collider.setIntoCollideMask(BitMask32.allOff())
        collider.addSolid(CollisionSphere(0, 0, 0, cameraradius))
        self.collider = self.root.attachNewNode(collider)
        self.traverser.addCollider(self.collider, self.queue)

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.update()

    def prepare_collision(self):
        for node in self.root.findAllMatches("**/+GeomNode"):
            if self.core.isAncestorOf(node):
                continue
            if node.getCollideMask().isZero():
                node.setCollideMask(BitMask32.allOn())
    def collides(self, x, y, z):
        self.collider.setPos(x, y, z)
        self.queue.clearEntries()
        self.traverser.traverse(self.root)
        return self.queue.getNumEntries() > 0
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

            self.yaw += dx * self.sensitivity
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
        right_y = math.sin(yaw)
        speed = self.speed*dt
        self.prepare_collision()
        new_x, new_y, new_z = self.position

        if keys[pygame.K_w]:
            new_x += forward_x * speed
            new_y += forward_y * speed
        if keys[pygame.K_s]:
            new_x -= forward_x * speed
            new_y -= forward_y * speed
        if keys[pygame.K_d]:
            new_x += right_x * speed
            new_y += right_y * speed
        if keys[pygame.K_a]:
            new_x -= right_x * speed
            new_y -= right_y * speed
        if keys[pygame.K_SPACE]:
            new_z += speed
        if keys[pygame.K_LCTRL]:
            new_z -= speed

        new_z = max(new_z, minheight)
        x, y, z = self.position

        if not self.collides(new_x, y, new_z):
            self.position[0] = new_x
        if not self.collides(self.position[0], new_y, new_z):
            self.position[1] = new_y
        if not self.collides(self.position[0], self.position[1], new_z):
            self.position[2] = new_z
        self.update()