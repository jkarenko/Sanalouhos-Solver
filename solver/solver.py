from datetime import datetime

from PIL import Image, ImageDraw, ImageFont


def find_word(grid, word, start_row, start_col, used_positions):
    rows, cols = len(grid), len(grid[0])
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dfs(row, col, index):
        if index == len(word):
            return [(row, col)]

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < rows and 0 <= new_col < cols and
                    grid[new_row][new_col] == word[index] and
                    (new_row, new_col) not in used_positions):
                result = dfs(new_row, new_col, index + 1)
                if result:
                    return [(row, col)] + result
        return None

    if grid[start_row][start_col] == word[0]:
        return dfs(start_row, start_col, 1)
    return None


def solve(grid, word):
    rows, cols = len(grid), len(grid[0])
    used_positions = set()
    solution = []

    def backtrack():
        if len(used_positions) == rows * cols:
            return True

        for r in range(rows):
            for c in range(cols):
                if (r, c) not in used_positions:
                    path = find_word(grid, word, r, c, used_positions)
                    if path:
                        solution.append((word, path))
                        used_positions.update(path)
                        if backtrack():
                            return True
                        used_positions.difference_update(path)
                        solution.pop()
        return False

    backtrack()
    return solution


def visualize_solution(grid, solution):
    cell_size = 100
    padding = 20
    rows, cols = len(grid), len(grid[0])
    img_width = cols * cell_size + 2 * padding
    img_height = rows * cell_size + 2 * padding

    image = Image.new("RGB", (img_width, img_height), color="white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # Draw grid
    for r in range(rows):
        for c in range(cols):
            x = c * cell_size + padding
            y = r * cell_size + padding
            draw.rectangle([x, y, x + cell_size, y + cell_size], outline="black")
            draw.text((x + cell_size // 2, y + cell_size // 2), grid[r][c],
                      fill="black", font=font, anchor="mm")

    # Draw connections
    colors = ["red", "blue", "green", "orange", "purple", "brown", "pink", "cyan", "magenta", "yellow"]
    for index, solution in enumerate(solution):
        word, path = solution
        color = colors[index % len(colors)]
        for i in range(len(path) - 1):
            start = path[i]
            end = path[i + 1]
            start_x = start[1] * cell_size + padding + cell_size // 2
            start_y = start[0] * cell_size + padding + cell_size // 2
            end_x = end[1] * cell_size + padding + cell_size // 2
            end_y = end[0] * cell_size + padding + cell_size // 2
            draw.line([start_x, start_y, end_x, end_y], fill=color, width=3)

    file_name = f"solution_visualization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png"
    image.save(file_name)
    print(f"Visualization saved as {file_name}")



# Example usage
grid = [
    "catca",
    "atcat",
    "tcatc",
    "catca",
    "atcat",
    "tcatc"
]

word = "cat"
result = solve(grid, word)

print("Solution:")
for word, path in result:
    print(f"Word: {word}, Path: {path}")

print(f"\nTotal words used: {len(result)}")
print(f"Total positions covered: {sum(len(path) for _, path in result)}")

visualize_solution(grid, result)