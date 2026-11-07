import os
from panda3d.core import CardMaker, Filename, PNMImage, Point3, Texture, Vec3

SKY_FACES = ("px", "nx", "py", "ny", "pz", "nz")
SKY_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "Assests", "skies", "cubemaps"
)


class SkyBox:
    """Cube-mapped sky that follows the camera's position but never its rotation."""

    # face -> (forward, up) in Panda3D space (X right, Y forward, Z up).
    # The image's right edge always points along forward x up.
    ORIENTATION = {
        "px": ((1, 0, 0), (0, 0, 1)),
        "nx": ((-1, 0, 0), (0, 0, 1)),
        "pz": ((0, 1, 0), (0, 0, 1)),
        "nz": ((0, -1, 0), (0, 0, 1)),
        "py": ((0, 0, 1), (0, -1, 0)),
        "ny": ((0, 0, -1), (0, 1, 0)),
    }

    def __init__(self, camera, reference, name="day_fair", size=10):
        self.size = size
        self.name = None
        self.cards = {}

        # Parented to the camera so it follows its position; the compass
        # effect cancels the camera's rotation so the sky stays fixed.
        self.root = camera.attachNewNode("skybox")
        self.root.setCompass(reference)
        self.root.setLightOff()
        self.root.setDepthTest(False)
        self.root.setDepthWrite(False)
        self.root.setBin("background", 0)

        for face in SKY_FACES:
            self.cards[face] = self._make_face(face)

        self.set_sky(name)

    @staticmethod
    def available_skies():
        return sorted(
            d for d in os.listdir(SKY_FOLDER)
            if os.path.isdir(os.path.join(SKY_FOLDER, d))
        )

    def _make_face(self, face):
        forward, up = self.ORIENTATION[face]
        maker = CardMaker(face)
        maker.setFrame(-self.size, self.size, -self.size, self.size)

        card = self.root.attachNewNode(maker.generate())
        card.setPos(*(c * self.size for c in forward))
        card.lookAt(
            Point3(*(c * self.size * 2 for c in forward)),
            Vec3(*up),
        )
        card.setTwoSided(True)
        return card

    def _load_texture(self, folder, face):
        path = os.path.join(folder, face + ".png")

        image = PNMImage()
        if not image.read(Filename.from_os_specific(path)):
            raise FileNotFoundError(path)

        texture = Texture(face)
        texture.load(image)
        texture.setWrapU(Texture.WM_clamp)
        texture.setWrapV(Texture.WM_clamp)
        texture.setMinfilter(Texture.FT_linear)
        texture.setMagfilter(Texture.FT_linear)
        return texture

    def set_sky(self, name):
        """Switch to another cubemap folder, e.g. "night_full_moon"."""
        folder = os.path.join(SKY_FOLDER, name)
        if not os.path.isdir(folder):
            raise ValueError(
                f"Unknown sky '{name}'. Available: {', '.join(self.available_skies())}"
            )

        # Load everything first so a bad file can't leave a half-swapped sky.
        textures = {face: self._load_texture(folder, face) for face in SKY_FACES}
        for face, card in self.cards.items():
            card.setTexture(textures[face], 1)

        self.name = name

    def destroy(self):
        self.root.removeNode()
        self.cards.clear()