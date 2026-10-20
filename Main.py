from render import Renderer
game = Renderer()
game.scene.add_floor(position=(0, 0, -3),  size=50)
game.scene.add_lighting()
duck = game.scene.add_object(  "Assests/Testing/ducky.glb",  position=(0, 5, 0), scale=1)
game.run()