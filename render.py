import pygame
import pygame3d
import sys
import math

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
model.position = (0, 20, -2)
# Add a light
light = surface.add_light('point')
light.position = (20, 20, 20)

light2 = surface.add_light('ambient')
light2.color = (50, 50, 50)
#Mouse
camera = surface.camera
camera_core = camera.core
target = (0, 20, -2)
distance = 15
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
            yaw += dx * sensitivity
            pitch = max(-80, min(80, pitch + dy * sensitivity))
            update_camera()
    #model.rotation += (1, 0, 0) # Rotate the model
    surface.render() # Render the surface to display the newest updates
    screen.blit(surface, (0, 0))

    pygame.display.update()
    clock.tick(60) # 60 FPS