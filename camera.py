
import math
import pygame
from panda3d.core import *
from physics import Physics

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
        self.physics = Physics(gravity=-20.0)
        self.jumpforce = 7.0
        self.grounded = False
        self.jump_released = True
        self.maxslopeangle = 45
        self.stepheight = 0.5

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

    def getgroundheight(self, x, y, z):
        ray = CollisionRay()
        ray.setOrigin(x, y, z + 0.5)
        ray.setDirection(0, 0, -1)

        node = CollisionNode("groundray")
        node.addSolid(ray)
        node.setFromCollideMask(BitMask32.allOn())
        node.setIntoCollideMask(BitMask32.allOff())

        raynode = self.root.attachNewNode(node)

        queue = CollisionHandlerQueue()
        traverser = CollisionTraverser()
        traverser.addCollider(raynode, queue)
        traverser.traverse(self.root)

        result = None

        if queue.getNumEntries() > 0:
            queue.sortEntries()
            entry = queue.getEntry(0)

            hitz = entry.getSurfacePoint(self.root).getZ()
            normal = entry.getSurfaceNormal(self.root)

            result = (hitz, normal)

        raynode.removeNode()
        return result

    def move(self, dt):
        if not self.mouse_captured:
            return

        keys = pygame.key.get_pressed()

        yaw = math.radians(self.yaw)

        forward_x = math.sin(yaw)
        forward_y = math.cos(yaw)

        right_x = math.cos(yaw)
        right_y = -math.sin(yaw)

        move_x = 0
        move_y = 0

        if keys[pygame.K_w]:
            move_x += forward_x
            move_y += forward_y

        if keys[pygame.K_s]:
            move_x -= forward_x
            move_y -= forward_y

        if keys[pygame.K_d]:
            move_x += right_x
            move_y += right_y

        if keys[pygame.K_a]:
            move_x -= right_x
            move_y -= right_y

        length = math.sqrt(move_x ** 2 + move_y ** 2)

        if length > 0:
            move_x /= length
            move_y /= length

        self.prepare_collision()

        # Current position
        x, y, z = self.position

        # Ground detection
        ground = self.getgroundheight(x, y, z)

        self.grounded = False

        if ground is not None:
            ground_z, normal = ground

            slopeangle = math.degrees(
                math.acos(max(-1, min(1, normal.getZ())))
            )

            if (
                slopeangle <= self.maxslopeangle
                and self.physics.velocity <= 0
                and z <= ground_z + minheight + 0.5
                and z >= ground_z + minheight - 0.5
            ):
                self.position[2] = ground_z + minheight
                self.physics.velocity = 0
                self.grounded = True

        # Jumping
        if not keys[pygame.K_SPACE]:
            self.jump_released = False

        if keys[pygame.K_SPACE] and self.grounded and self.physics.velocity <=0:
            self.physics.velocity = self.jumpforce
            self.grounded = False

        # Gravity
        if not self.grounded:
            self.physics.update(self, dt)

        new_z = self.position[2]

        # Horizontal movement
        next_x = self.position[0] + move_x * self.speed * dt
        next_y = self.position[1] + move_y * self.speed * dt

        # Check terrain at destination
        next_ground = self.getgroundheight(
            next_x,
            next_y,
            self.position[2]
        )

        if next_ground is not None:
            next_ground_z, next_normal = next_ground

            next_slope = math.degrees(
                math.acos(max(-1, min(1, next_normal.getZ())))
            )

            if next_slope <= self.maxslopeangle:
                target_z = next_ground_z + minheight
                height_difference = target_z - self.position[2]

                if -self.stepheight <= height_difference <= self.stepheight:
                    if not self.collides(next_x, next_y, target_z):
                        self.position[0] = next_x
                        self.position[1] = next_y

                        if self.grounded:
                            self.position[2] = target_z

                elif not self.collides(next_x, next_y, new_z):
                    self.position[0] = next_x
                    self.position[1] = next_y

        else:
            # Allow walking off ledges
            if not self.collides(next_x, next_y, new_z):
                self.position[0] = next_x
                self.position[1] = next_y

        # Vertical collision
        if not self.grounded:
            if not self.collides(
                self.position[0],
                self.position[1],
                new_z
            ):
                self.position[2] = new_z
            else:
                self.physics.velocity = 0

        self.update()
