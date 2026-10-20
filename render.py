import pygame
import pygame3d
from physics import Physics
import sys
import math
from panda3d.core import CardMaker

# Initialize the pygame library
pygame.init()

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Create a 3D surface
surface = pygame3d.Surface3D((800, 600))

# Configure background color
surface.background_color = (145, 216, 255) # Sky blue

# Loading a model
model = surface.load_mesh('Assests/Testing/ducky.glb')
physics = Physics(groundz=-3)
model.position = (0, 20, 10)
# Ground
ground = CardMaker("ground")
ground.setFrame(-50, 50, -50, 50)

ground_node = surface._root_node.attachNewNode(ground.generate())
ground_node.setP(90)
ground_node.setPos(0, 0, -3)
ground_node.setColor(1, 1, 1, 1)
ground_node.setTwoSided(True)
# Add a light
light = surface.add_light('point')
light.position = (20, 20, 20)

light2 = surface.add_light('ambient')
light2.color = (50, 50, 50)
#Mouse
camera = surface.camera
camera_core = camera.core
target = (0, 20, -2)
distance = 27
yaw = 0
pitch = 0
dragging = False
sensitivity = 0.7
#Update Camera
def update_camera():
    yaw_rad = math.radians(yaw)
    pitch_rad = math.radians(pitch)

    x = target[0] + distance * math.cos(pitch_rad) * math.sin(yaw_rad)
    y = target[1] + distance * math.sin(pitch_rad)
    z = target[2] + distance * math.cos(pitch_rad) * math.cos(yaw_rad)

    camera_core.setPos(x, y, z)
    camera_core.lookAt(*target)
# Main game loop
update_camera()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            dragging = True
        if event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        if event.type == pygame.MOUSEMOTION and dragging:
            dx, dy = event.rel
            yaw -= dx * sensitivity
            pitch = max(-80, min(80, pitch + dy * sensitivity))
            update_camera()
    #model.rotation += (1, 0, 0) # Rotate the model
    dt = clock.tick(60) / 1000.0
    physics.update(model, dt)
    surface.render() # Render the surface to display the newest updates
    screen.blit(surface, (0, 0))
    pygame.display.update()
    clock.tick(60) # 60 FPS