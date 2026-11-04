
import os

from render import Renderer
from tile import TileWorld
from panda3d.core import *

game = Renderer()

game.scene.add_lighting()

# Generate and load the world
world = TileWorld(
    game,
    seed=1337,
    chunksize=16,
    viewdistance=3,
)

world.update((0, 0))

# Hand and Nail Gun
viewgun = game.surface.load_mesh(
    "Assests/01-player-and-equipment/nail-gun-first-person.obj"
)
viewgun.core.reparentTo(game.camera.core)
viewgun.core.setPos(0.15, 0.9, -0.26)
viewgun.core.setHpr(10, 90, 0)
viewgun.core.setScale(0.4)
viewgun.core.setDepthTest(False)
viewgun.core.setDepthWrite(False)
viewgun.core.setBin("fixed", 100)

game.camera.core.node().getLens().setNear(0.05)


# Skybox
SKY_NAME = "day_fair"
SKY_FACES = ("px", "nx", "py", "ny", "pz", "nz")


def load_skybox(name):
    folder = os.path.join("Assests", "skies", "cubemaps", name)

    settings = [
        ("px", (50, 0, 0), (-90, 0, 0)),
        ("nx", (-50, 0, 0), (90, 0, 0)),
        ("py", (0, 50, 0), (0, 0, 0)),
        ("ny", (0, -50, 0), (180, 0, 0)),
        ("pz", (0, 0, 50), (0, 90, 0)),
        ("nz", (0, 0, -50), (0, -90, 0)),
    ]

    faces = []

    for face, position, rotation in settings:
        path = os.path.abspath(
            os.path.join(folder, face + ".png")
        )

        texture = Texture(face)
        image = PNMImage()
        if not image.read(Filename.from_os_specific(path)):
            raise FileNotFoundError(path)

        texture.load(image)
        texture.setMinfilter(Texture.FT_linear)
        texture.setMagfilter(Texture.FT_linear)

        maker = CardMaker(face)
        maker.setFrame(-50, 50, -50, 50)

        card = game.camera.core.attachNewNode(
            maker.generate()
        )

        card.setPos(*position)
        card.setHpr(*rotation)
        card.setTexture(texture)
        card.setTwoSided(True)
        card.setLightOff()
        card.setDepthTest(False)
        card.setDepthWrite(False)
        card.setBin("background", 0)

        faces.append(card)

    return faces


sky = load_skybox(SKY_NAME)


# Start game
game.run()
