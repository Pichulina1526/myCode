import random


def generate_moonshire_map(width=1000, height=1000, filename="map.txt"):
    # TILE DICTIONARY:
    # 0 = Green Grass (Default open space)
    # 1 = Pink Tree / Obstacle (Forests)
    # 3 = Blue Water (Lakes)
    # 4 = Brown Dirt Path

    print("1. Laying down the grassy plains...")
    # Start with a massive open world of just grass
    grid = [[0 for _ in range(width)] for _ in range(height)]

    print("2. Digging out the lakes...")
    # Create natural, rounded clusters of water
    num_lakes = (width * height) // 8000
    for _ in range(num_lakes):
        cx, cy = random.randint(0, width - 1), random.randint(0, height - 1)
        radius = random.randint(4, 12)
        for y in range(max(0, cy - radius), min(height, cy + radius)):
            for x in range(max(0, cx - radius), min(width, cx + radius)):
                # Circle formula to make rounded lakes
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                    grid[y][x] = 3

    print("3. Planting the pink tree forests...")
    # Create natural, clustered forests
    num_forests = (width * height) // 4000
    for _ in range(num_forests):
        cx, cy = random.randint(0, width - 1), random.randint(0, height - 1)
        radius = random.randint(5, 15)
        for y in range(max(0, cy - radius), min(height, cy + radius)):
            for x in range(max(0, cx - radius), min(width, cx + radius)):
                # Only plant trees on grass (don't overwrite lakes)
                if grid[y][x] == 0 and (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                    if random.random() < 0.65:  # 65% tree density so it looks natural
                        grid[y][x] = 1

    print("4. Carving the winding dirt paths...")
    # Carve a long, continuous, wide dirt path starting from the center
    x, y = width // 2, height // 2
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for step in range(width * height // 4):
        # Use a "3x3 brush" to make the path nice and wide, just like Moonshire
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    grid[ny][nx] = 4

        # Move the brush
        dx, dy = random.choice(directions)
        x = max(2, min(width - 3, x + dx * 2))
        y = max(2, min(height - 3, y + dy * 2))

    print(f"5. Saving to {filename}...")
    # Write the entire world to your text file
    with open(filename, 'w') as f:
        for row in grid:
            f.write(','.join(map(str, row)) + '\n')

    print("Success! Your Moonshire-style map.txt is ready.")


if __name__ == "__main__":
    generate_moonshire_map()