
from render import Renderer
from tile import TileWorld

game = Renderer()

game.scene.add_lighting()

# Generate and load the world
world = TileWorld(
    game,
    seed=1337,
    chunksize=16,
    viewdistance=3,
)

# Load initial chunks around the spawn point
world.update((0, 0))

# Test object
duck = game.scene.add_object(
    "Assests/Testing/ducky.glb",
    position=(0, 5, 0),
    scale=1,
)

game.run()
