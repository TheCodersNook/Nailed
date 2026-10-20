
import pygame
from pygame3d import Surface3D
from panda3d.core import (
    CardMaker,
    PointLight,
    AmbientLight,
    Vec4,
)

from camera import Camera


class GameObject:
    """A manageable 3D object in the scene."""

    def __init__(
        self,
        model,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=1.0,
        physics=None,
    ):
        self.model = model
        self.physics = physics

        self.position = position
        self.rotation = rotation
        self.scale = scale

    @property
    def position(self):
        return self.model.position

    @position.setter
    def position(self, value):
        self.model.position = value

    @property
    def rotation(self):
        return self.model.rotation

    @rotation.setter
    def rotation(self, value):
        self.model.rotation = value

    @property
    def scale(self):
        return self.model.scale

    @scale.setter
    def scale(self, value):
        self.model.scale = value

    def set_position(self, position):
        self.position = position

    def set_rotation(self, rotation):
        self.rotation = rotation

    def set_scale(self, scale):
        self.scale = scale

    def update(self, dt):
        if self.physics:
            self.physics.update(self, dt)


class Scene:
    """Stores and manages objects, the floor, and lighting."""

    def __init__(self, surface):
        self.surface = surface
        self.root = surface._root_node

        self.objects = []
        self.environments = []

    def add_object(
        self,
        path,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=1.0,
        physics=None,
    ):
        """Load a 3D model and add it to the scene."""

        model = self.surface.load_mesh(path)

        obj = GameObject(
            model=model,
            position=position,
            rotation=rotation,
            scale=scale,
            physics=physics,
        )

        self.objects.append(obj)
        return obj

    def remove_object(self, obj):
        """Remove an object from the scene."""

        if obj in self.objects:
            self.objects.remove(obj)

            # Remove the underlying Panda3D node if available.
            core = getattr(obj.model, "core", None)
            if core is not None and hasattr(core, "removeNode"):
                core.removeNode()

    def add_floor(
        self,
        position=(0, 0, -3),
        size=50,
        color=(0.35, 0.35, 0.35, 1),
    ):
        """Create a large horizontal floor."""

        floor_maker = CardMaker("floor")
        floor_maker.setFrame(-size, size, -size, size)

        floor = self.root.attachNewNode(
            floor_maker.generate()
        )

        # CardMaker creates an XY plane.
        floor.setPos(*position)
        floor.setColor(*color)
        floor.setTwoSided(True)

        self.environments.append(floor)
        return floor

    def add_lighting(self):
        """Add ambient and point lighting."""

        point_light = PointLight("point_light")
        point_light.setColor(Vec4(1, 1, 1, 1))

        point_node = self.root.attachNewNode(point_light)
        point_node.setPos(5, -5, 10)
        self.root.setLight(point_node)

        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor(Vec4(0.4, 0.4, 0.4, 1))

        ambient_node = self.root.attachNewNode(ambient_light)
        self.root.setLight(ambient_node)

        self.environments.extend(
            [point_node, ambient_node]
        )

    def remove_environment(self, item):
        """Remove a floor or lighting node."""

        if item in self.environments:
            self.environments.remove(item)
            item.removeNode()

    def update(self, dt):
        """Update every object in the scene."""

        for obj in self.objects:
            obj.update(dt)


class Renderer:
    """Initializes the window, camera, and game loop."""

    def __init__(self, width=800, height=600):
        pygame.init()

        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode(
            (width, height)
        )
        pygame.display.set_caption("Nailed")

        self.surface = Surface3D((width, height))
        self.surface.fill((135, 206, 235))

        self.clock = pygame.time.Clock()
        self.running = False

        self.scene = Scene(self.surface)

        self.camera = Camera(
            self.surface,
            position=(0, 0, 2),
        )

    def run(self):
        """Run the main game loop."""

        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.camera.handle_event(event)

            dt = self.clock.tick(60) / 1000.0

            self.camera.move(dt)
            self.scene.update(dt)

            self.surface.render()

            self.screen.blit(self.surface, (0, 0))
            pygame.display.flip()

        pygame.quit()
