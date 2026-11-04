import math

worldwidth = 128
worldheight = 128
seed = 1337  # change this for a different world
WORLD_SEED = seed
spawnradius = 8


def _hash01(ix, iy, seed_value):
    n = (ix * 374761393 + iy * 668265263 + seed_value * 1442695041) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    n = n ^ (n >> 16)
    return (n & 0xFFFFFFFF) / 4294967295.0


def _value_noise(x, y, seed_value):
    x0 = math.floor(x)
    y0 = math.floor(y)
    fx = x - x0
    fy = y - y0
    sx = fx * fx * (3.0 - 2.0 * fx)
    sy = fy * fy * (3.0 - 2.0 * fy)

    n00 = _hash01(x0, y0, seed_value)
    n10 = _hash01(x0 + 1, y0, seed_value)
    n01 = _hash01(x0, y0 + 1, seed_value)
    n11 = _hash01(x0 + 1, y0 + 1, seed_value)

    nx0 = n00 + (n10 - n00) * sx
    nx1 = n01 + (n11 - n01) * sx
    return nx0 + (nx1 - nx0) * sy


def _fbm(x, y, seed_value, octaves=4, lacunarity=2.0, persistence=0.5):
    total = 0.0
    amplitude = 1.0
    frequency = 1.0
    maximum = 0.0

    for _ in range(octaves):
        total += _value_noise(x * frequency, y * frequency, seed_value) * amplitude
        maximum += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return total / maximum


def _percentile(values, fraction):
    ordered = sorted(values)
    index = int(fraction * (len(ordered) - 1))
    return ordered[max(0, min(index, len(ordered) - 1))]


def clear_spawn_area(rows, radius=spawnradius):
    """Make a rounded grass clearing with a sand edge."""
    centerx = len(rows[0]) // 2
    centery = len(rows) // 2

    for y in range(centery - radius - 2, centery + radius + 2):
        if not 0 <= y < len(rows):
            continue

        row = list(rows[y])
        for x in range(centerx - radius - 2, centerx + radius + 2):
            if not 0 <= x < len(row):
                continue

            distance = math.hypot(x - centerx, y - centery)
            if distance <= radius:
                row[x] = "G"
            elif distance <= radius + 1.2 and row[x] == "W":
                row[x] = "S"

        rows[y] = "".join(row)


def _neighbour_has_water(rows, x, y):
    neighbours = (
        (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
        (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1),
    )
    for nx, ny in neighbours:
        if 0 <= nx < len(rows[0]) and 0 <= ny < len(rows):
            if rows[ny][nx] == "W":
                return True
    return False


def _carve_river(rows, seed_value):
    width = len(rows[0])
    height = len(rows)
    river_base = width * 0.22
    sand_offsets = (-3, -2, 2, 3)
    water_offsets = (-1, 0, 1)

    for y in range(height):
        meander = (
            math.sin(y * 0.055) * 6.0
            + (_fbm(0.0, y * 0.06, seed_value + 71, 3) - 0.5) * 10.0
        )
        river_x = int(river_base + meander)

        for dx in sand_offsets:
            x = river_x + dx
            if 0 <= x < width and rows[y][x] not in ("W", "R"):
                rows[y][x] = "S"

        for dx in water_offsets:
            x = river_x + dx
            if 0 <= x < width:
                rows[y][x] = "W"


def generate_world(seed=None, width=None, height=None):
    chosen_seed = WORLD_SEED if seed is None else seed
    width = worldwidth if width is None else width
    height = worldheight if height is None else height

    elevation_grid = []
    moisture_grid = []
    rockiness_grid = []
    clearing_grid = []

    for y in range(height):
        elevation_row = []
        moisture_row = []
        rockiness_row = []
        clearing_row = []

        for x in range(width):
            continent = _fbm(x * 0.018, y * 0.018, chosen_seed + 11, 3)
            hills = _fbm(x * 0.055, y * 0.055, chosen_seed + 17, 4)
            detail = _fbm(x * 0.140, y * 0.140, chosen_seed + 23, 2)
            elevation = continent * 0.55 + hills * 0.32 + detail * 0.13

            moisture = (
                _fbm(x * 0.040, y * 0.040, chosen_seed + 31, 4) * 0.70
                + _fbm(x * 0.120, y * 0.120, chosen_seed + 37, 2) * 0.30
            )
            rockiness = _fbm(x * 0.060, y * 0.060, chosen_seed + 41, 3)
            clearings = _fbm(x * 0.080, y * 0.080, chosen_seed + 83, 3)

            elevation_row.append(elevation)
            moisture_row.append(moisture)
            rockiness_row.append(rockiness)
            clearing_row.append(clearings)

        elevation_grid.append(elevation_row)
        moisture_grid.append(moisture_row)
        rockiness_grid.append(rockiness_row)
        clearing_grid.append(clearing_row)

    elevation_values = [value for row in elevation_grid for value in row]
    moisture_values = [value for row in moisture_grid for value in row]
    rockiness_values = [value for row in rockiness_grid for value in row]
    clearing_values = [value for row in clearing_grid for value in row]

    water_level = _percentile(elevation_values, 0.12)
    sand_level = _percentile(elevation_values, 0.16)
    high_ground = _percentile(elevation_values, 0.70)
    rock_level = _percentile(elevation_values, 0.94)
    rocky_patch = _percentile(rockiness_values, 0.90)

    tree_level = _percentile(moisture_values, 0.74)
    bush_level = _percentile(moisture_values, 0.64)
    flower_level = _percentile(moisture_values, 0.54)
    dry_level = _percentile(moisture_values, 0.10)

    clearing_level = _percentile(clearing_values, 0.70)

    rows = []
    for y in range(height):
        row = ""
        for x in range(width):
            elevation = elevation_grid[y][x]
            moisture = moisture_grid[y][x]
            rockiness = rockiness_grid[y][x]
            clearings = clearing_grid[y][x]

            if elevation < water_level:
                char = "W"
            elif elevation > rock_level or (
                elevation > high_ground and rockiness > rocky_patch
            ):
                char = "R"
            elif elevation < sand_level:
                char = "S"
            elif moisture > tree_level:
                char = "T"
            elif moisture > bush_level:
                char = "B"
            elif moisture > flower_level:
                char = "F"
            elif moisture < dry_level:
                char = "D"
            else:
                char = "G"

            if char in ("T", "B") and clearings > clearing_level:
                char = "F" if moisture > flower_level else "G"

            row += char
        rows.append(row)

    rows = [list(row) for row in rows]
    _carve_river(rows, chosen_seed)

    # Add a small beach wherever land touches water.
    for y in range(height):
        for x in range(width):
            if rows[y][x] not in ("W", "R", "S") and _neighbour_has_water(rows, x, y):
                rows[y][x] = "S"

    clear_spawn_area(rows)
    return ["".join(row) for row in rows]


WORLD = generate_world()


if __name__ == "__main__":
    print(f"World seed: {WORLD_SEED}")
    print(f"World size: {worldwidth}x{worldheight}")
    print("\n".join(WORLD))