
import math
import random
from pathlib import Path
from panda3d.core import NodePath, PandaNode
import os
import world as world_module

ASSEST = Path(__file__).resolve().parent / "Assests"
tilesize = 4.0
chunksize = 16
viewdistance = 3


def _assests(*paths):
    return [str(ASSEST / path) for path in paths]


GROUND_TILES = {
    "G": _assests(
        "terrain/grass/grass_01.glb",
        "terrain/grass/grass_02.glb",
        "terrain/grass/grass_03.glb",
        "terrain/grass/grass_04.glb",
    ),
    "D": _assests(
        "terrain/dirt/dirt_01.glb",
        "terrain/dirt/dirt_02.glb",
        "terrain/dirt/dirt_03.glb",
        "terrain/dirt/dirt_04.glb",
    ),
    "S": _assests(
        "terrain/sand/sand_01.glb",
        "terrain/sand/sand_02.glb",
        "terrain/sand/sand_03.glb",
    ),
    "W": _assests(
        "terrain/water/water_01.glb",
        "terrain/water/water_02.glb",
        "terrain/water/water_03.glb",
    ),
    "R": _assests(
        "terrain/rock/rock_ground_01.glb",
        "terrain/rock/rock_ground_02.glb",
        "terrain/rock/rock_ground_03.glb",
    ),
    "T": _assests(
        "terrain/grass/grass_01.glb",
        "terrain/grass/grass_02.glb",
        "terrain/grass/grass_03.glb",
        "terrain/grass/grass_04.glb",
    ),
    "B": _assests(
        "terrain/grass/grass_01.glb",
        "terrain/grass/grass_02.glb",
        "terrain/grass/grass_03.glb",
        "terrain/grass/grass_04.glb",
    ),
    "F": _assests(
        "terrain/grass/grass_01.glb",
        "terrain/grass/grass_02.glb",
        "terrain/grass/grass_03.glb",
        "terrain/grass/grass_04.glb",
    ),
}


PROP_TILES = {
    "T": _assests(
        "vegetation/trees/tree_oak_01.glb",
        "vegetation/trees/tree_oak_02.glb",
        "vegetation/trees/tree_oak_03.glb",
        "vegetation/trees/tree_pine_01.glb",
        "vegetation/trees/tree_pine_02.glb",
        "vegetation/trees/tree_pine_03.glb",
    ),
    "B": _assests(
        "vegetation/bushes/bush_01.glb",
        "vegetation/bushes/bush_02.glb",
        "vegetation/bushes/bush_03.glb",
        "vegetation/bushes/bush_04.glb",
    ),
    "F": _assests(
        "vegetation/flowers/flower_01.glb",
        "vegetation/flowers/flower_02.glb",
        "vegetation/flowers/flower_03.glb",
        "vegetation/flowers/flower_04.glb",
        "vegetation/flowers/grass_tuft_01.glb",
        "vegetation/flowers/grass_tuft_02.glb",
        "vegetation/flowers/grass_tuft_03.glb",
    ),
    "R": _assests(
        "rocks/rock_medium_01.glb",
        "rocks/rock_medium_02.glb",
        "rocks/rock_medium_03.glb",
        "rocks/rock_small_01.glb",
        "rocks/rock_small_02.glb",
        "rocks/rock_small_03.glb",
        "rocks/rock_small_04.glb",
    ),
    "G": _assests(
        "vegetation/flowers/grass_tuft_01.glb",
        "vegetation/flowers/grass_tuft_02.glb",
        "vegetation/flowers/grass_tuft_03.glb",
    ),
}


PROP_CHANCE = {
    "T": 1.0,
    "B": 1.0,
    "F": 1.0,
    "R": 0.35,
    "G": 0.08,
}


class TileWorld:

    def __init__(
        self,
        game,
        seed=None,
        chunksize=chunksize,
        viewdistance=viewdistance,
    ):
        self.game = game
        self.scene = game.scene
        self.surface = game.surface

        if seed is None:
            self.seed = world_module.WORLD_SEED
            self.world = world_module.WORLD
        else:
            self.seed = seed
            self.world = world_module.generate_world(self.seed)

        self.width = len(self.world[0])
        self.height = len(self.world)

        self.chunksize = chunksize
        self.viewdistance = viewdistance

        self._templates = {}
        self._chunks = {}

    def _template(self, path):
        template = self._templates.get(path)

        if template is None:
            loaded = self.surface.load_mesh(path)

            template = NodePath(PandaNode(Path(path).stem))

            for child in list(loaded.core.getChildren()):
                child.reparentTo(template)

            loaded.core.removeNode()
            template.detachNode()

            self._templates[path] = template

        return template

    def _rng(self, *key):
        return random.Random(
            ":".join(str(part) for part in (self.seed, *key))
        )

    def _pick(self, options, *key):
        valid_options = [
            path for path in options
            if os.path.isfile(path)
        ]

        if not valid_options:
            raise FileNotFoundError(
                f"No valid models found. Checked: {options}"
            )

        return self._rng(*key).choice(valid_options)

    def _add(
        self,
        parent,
        path,
        x,
        y,
        z=0.0,
        heading=0.0,
        scale=1.0,
    ):
        node = self._template(path).copyTo(parent)

        node.setPos(x, y, z)
        node.setScale(scale)
        node.setHpr(heading, 0, 0)

        return node

    def _tile_to_world(self, tile_x, tile_y):
        return (
            (tile_x - self.width / 2) * tilesize,
            (tile_y - self.height / 2) * tilesize,
        )

    def world_to_tile(self, x, y):
        return (
            int(math.floor(x / tilesize + self.width / 2)),
            int(math.floor(y / tilesize + self.height / 2)),
        )

    def tile_at_world(self, x, y):
        tile_x, tile_y = self.world_to_tile(x, y)

        if (
            0 <= tile_x < self.width
            and 0 <= tile_y < self.height
        ):
            return self.world[tile_y][tile_x]

        return None

    def _build_tile(self, parent, tile_x, tile_y):
        char = self.world[tile_y][tile_x]

        x, y = self._tile_to_world(tile_x, tile_y)

        ground = self._pick(
            GROUND_TILES[char],
            "ground",
            tile_x,
            tile_y,
        )

        heading = self._rng(
            "ground_rotation",
            tile_x,
            tile_y,
        ).choice((0, 90, 180, 270))

        self._add(
            parent,
            ground,
            x,
            y,
            heading=heading,
            scale=tilesize,
        )

        props = PROP_TILES.get(char)

        if not props:
            return

        rng = self._rng("prop", tile_x, tile_y)

        if rng.random() > PROP_CHANCE.get(char, 0.0):
            return

        path = rng.choice(props)
        heading = rng.choice((0, 90, 180, 270))
        scale = tilesize * rng.uniform(0.85, 1.15)

        offset_x = rng.uniform(-0.18, 0.18) * tilesize
        offset_y = rng.uniform(-0.18, 0.18) * tilesize

        self._add(
            parent,
            path,
            x + offset_x,
            y + offset_y,
            heading=heading,
            scale=scale,
        )

    def _build_chunk(self, chunk_x, chunk_y):
        key = (chunk_x, chunk_y)

        if key in self._chunks:
            return self._chunks[key]

        chunk = self.scene.root.attachNewNode(
            f"tiles_{chunk_x}_{chunk_y}"
        )

        start_x = chunk_x * self.chunksize
        start_y = chunk_y * self.chunksize

        end_x = min(start_x + self.chunksize, self.width)
        end_y = min(start_y + self.chunksize, self.height)

        for tile_y in range(start_y, end_y):
            for tile_x in range(start_x, end_x):
                self._build_tile(
                    chunk,
                    tile_x,
                    tile_y,
                )

        chunk.flattenStrong()

        self._chunks[key] = chunk

        return chunk

    def _unload_chunk(self, key):
        chunk = self._chunks.pop(key, None)

        if chunk is not None:
            chunk.removeNode()

    def build_all(self):
        chunks_x = math.ceil(self.width / self.chunksize)
        chunks_y = math.ceil(self.height / self.chunksize)

        for chunk_y in range(chunks_y):
            for chunk_x in range(chunks_x):
                self._build_chunk(chunk_x, chunk_y)

    def update(self, player_position):
        tile_x, tile_y = self.world_to_tile(
            player_position[0],
            player_position[1],
        )

        center_x = tile_x // self.chunksize
        center_y = tile_y // self.chunksize

        wanted = set()
        radius = self.viewdistance

        for chunk_y in range(
            center_y - radius,
            center_y + radius + 1,
        ):
            for chunk_x in range(
                center_x - radius,
                center_x + radius + 1,
            ):
                if (
                    0 <= chunk_x * self.chunksize < self.width
                    and 0 <= chunk_y * self.chunksize < self.height
                ):
                    wanted.add((chunk_x, chunk_y))

        for key in list(self._chunks):
            if key not in wanted:
                self._unload_chunk(key)

        for chunk_x, chunk_y in wanted:
            self._build_chunk(chunk_x, chunk_y)
