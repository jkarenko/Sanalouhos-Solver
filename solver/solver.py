from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt


def find_word(grid, word, start_row, start_col, used_positions):
    rows, cols = len(grid), len(grid[0])
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dfs(row, col, index, path):
        if index == len(word):
            return path

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < rows and 0 <= new_col < cols and
                    grid[new_row][new_col] == word[index] and
                    (new_row, new_col) not in used_positions and
                    (new_row, new_col) not in path):
                new_path = path + [(new_row, new_col)]
                result = dfs(new_row, new_col, index + 1, new_path)
                if result:
                    return result
        return None

    if grid[start_row][start_col] == word[0]:
        return dfs(start_row, start_col, 1, [(start_row, start_col)])
    return None


def check_isolated_letters(grid, used_positions):
    rows, cols = len(grid), len(grid[0])
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def count_connectable_letters(row, col):
        count = 1
        visited = set([(row, col)])
        stack = [(row, col)]

        while stack:
            r, c = stack.pop()
            for dr, dc in directions:
                new_row, new_col = r + dr, c + dc
                if (0 <= new_row < rows and 0 <= new_col < cols and
                        (new_row, new_col) not in used_positions and
                        (new_row, new_col) not in visited):
                    count += 1
                    visited.add((new_row, new_col))
                    stack.append((new_row, new_col))

        return count

    for r in range(rows):
        for c in range(cols):
            if (r, c) not in used_positions:
                connectable_letters = count_connectable_letters(r, c)
                if 1 <= connectable_letters <= 2:
                    return False

    return True


def create_visualization(grid, solution):
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
    for index, solution_item in enumerate(solution):
        word, path = solution_item
        color = colors[index % len(colors)]
        for i in range(len(path) - 1):
            start = path[i]
            end = path[i + 1]
            start_x = start[1] * cell_size + padding + cell_size // 2
            start_y = start[0] * cell_size + padding + cell_size // 2
            end_x = end[1] * cell_size + padding + cell_size // 2
            end_y = end[0] * cell_size + padding + cell_size // 2
            draw.line([start_x, start_y, end_x, end_y], fill=color, width=3)

    return image


def update_visualization(grid, solution):
    img = create_visualization(grid, solution)
    plt.clf()
    plt.imshow(img)
    plt.title(f"Current solution: {len(solution)} words\nwords: {[word for word, _ in solution]}")
    plt.axis('off')
    plt.draw()
    plt.pause(0.1)


def solve(grid, words):
    rows, cols = len(grid), len(grid[0])
    used_positions = set()
    solution = []
    max_solution_length = 0

    plt.ion()
    plt.figure(figsize=(10, 10))

    def backtrack():
        nonlocal max_solution_length
        if len(used_positions) == rows * cols:
            return True

        for r in range(rows):
            for c in range(cols):
                if (r, c) not in used_positions:
                    tried_words = 0
                    for word in words:
                        tried_words += 1
                        path = find_word(grid, word, r, c, used_positions)
                        if path:
                            solution.append((word, path))
                            used_positions.update(path)

                            if check_isolated_letters(grid, used_positions):
                                if len(solution) > max_solution_length:
                                    max_solution_length = len(solution)
                                    print(f"{max_solution_length} words: {[word for word, _ in solution]}")
                                    update_visualization(grid, solution)

                                if backtrack():
                                    return True

                            used_positions.difference_update(path)
                            solution.pop()
                            update_visualization(grid, solution)
                            print(f"Backtracking... {tried_words} words tried")
        return False

    backtrack()
    plt.ioff()
    plt.show()
    return solution


def read_grid_from_file(file_path):
    with open(file_path, "r", encoding="utf8") as file:
        return [list(line.strip()) for line in file]


def read_words_from_file(file_path):
    with open(file_path, "r", encoding="utf8") as file:
        return [line.strip() for line in file]


def main():
    grid = read_grid_from_file("puzzle.txt")
    words = read_words_from_file("words.txt")

    result = solve(grid, words)

    print("Solution:")
    for word, path in result:
        print(f"Word: {word}, Path: {path}")

    print(f"\nTotal words used: {len(result)}")
    print(f"Total positions covered: {sum(len(path) for _, path in result)}")
