
class Physics:
    def __init__(self, gravity=-20.0, terminalvelocity=-50.0):
        self.gravity = gravity
        self.terminalvelocity =  terminalvelocity
        self.velocity = 0.0

    def update(self, model, dt):
        x, y, z = model.position
        self.velocity += self.gravity * dt
        self.velocity = max(self.velocity, self.terminalvelocity)
        z += self.velocity * dt
        model.position[2] = z