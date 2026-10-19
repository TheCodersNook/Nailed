import math
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

sides = int(input("How many sides? "))

vertices = []

# Create top and bottom polygons
for z in [1, -1]:
    for i in range(sides):
        angle = 2 * math.pi * i / sides
        vertices.append((
            math.cos(angle),
            math.sin(angle),
            z
        ))

edges = []

for i in range(sides):
    next_i = (i + 1) % sides

    # Top and bottom edges
    edges.append((i, next_i))
    edges.append((i + sides, next_i + sides))

    # Vertical edges
    edges.append((i, i + sides))

def drawobject():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        glRotatef(1, 0, 1, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        drawobject()
        pygame.display.flip()
        pygame.time.wait(10)

main()
