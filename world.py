
import random

# World settings
WIDTH = 128
HEIGHT = 128
SEED = 1337
SPAWN_RADIUS = 8

# Backwards-compatible names
width = WIDTH
height = HEIGHT
seed = SEED
spawnradius = SPAWN_RADIUS

WORLD_SEED = SEED


def clear_spawn_area(rows, radius=SPAWN_RADIUS):
    """Clear a square grass area in the center of the map."""

    center_x = len(rows[0]) // 2
    center_y = len(rows) // 2

    for y in range(max(0, center_y - radius),
                   min(len(rows), center_y + radius + 1)):

        row = list(rows[y])

        for x in range(max(0, center_x - radius),
                       min(len(row), center_x + radius + 1)):
            row[x] = "G"

        rows[y] = "".join(row)


def generate_world(world_seed=None):
    """Generate a deterministic world from a seed."""

    if world_seed is None:
        world_seed = WORLD_SEED

    rng = random.Random(world_seed)
    rows = []

    for y in range(HEIGHT):
        row = ""

        for x in range(WIDTH):
            char = rng.choice("GRTFSWBD")
            previous = row[-1] if row else None

            # Terrain rules
            if previous == "W":
                char = "W" if char == "W" else "S"

            elif char == "T" and previous in ("T", "B"):
                char = "T"

            elif char == "B" and previous == "T":
                char = "B"

            elif char == "R" and previous == "R":
                char = "R"

            elif char == "F" and previous == "G":
                char = "F"

            elif char == "D" and previous == "D":
                char = "D"

            row += char

        rows.append(row)

    # Create a clear player spawn area
    clear_spawn_area(rows)

    return rows


# Default generated world
WORLD = generate_world(WORLD_SEED)


if __name__ == "__main__":
    print(f"World seed: {WORLD_SEED}")
    print(f"World size: {WIDTH}x{HEIGHT}")
    print("\n".join(WORLD))
