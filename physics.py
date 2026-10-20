
class Physics:
    def __init__(self, gravity=-9.81, groundz=-3):
        self.gravity = gravity
        self.groundz = groundz
        self.velocity = 0.0

    def update(self, model, dt):
        x, y, z = model.position

        if z > self.groundz:
            self.velocity += self.gravity * dt
            z += self.velocity * dt

        if z <= self.groundz:
            z = self.groundz
            self.velocity = 0.0

        model.position = (x, y, z)
