import os
from render import Renderer
from tile import TileWorld
from panda3d.core import *
from sky import SkyBox

game = Renderer()
game.scene.add_lighting()

world = TileWorld(
    game,
    seed=1334,
    chunksize=16,
    viewdistance=3,
)

world.update((0, 0))


viewgun = game.surface.load_mesh(
    "Assests/01-player-and-equipment/nail-gun-first-person.obj"
)
viewgun.core.reparentTo(game.camera.core)
viewgun.core.setPos(0.15, 0.9, -0.26)
viewgun.core.setHpr(10, 90, 0)
viewgun.core.setScale(0.85)
viewgun.core.setDepthTest(False)
viewgun.core.setDepthWrite(False)
viewgun.core.setBin("fixed", 100)
game.camera.core.node().getLens().setNear(0.05)
game.camera.core.node().getLens().setFov(110)
sky = SkyBox(game.camera.core, game.scene.root, "day_fair")
sky.set_sky("night_full_moon")
game.run()
