from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import multiprocessing
from functools import partial
from collections import defaultdict


class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.is_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            node = node.children[char]
        node.is_word = True

    def search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return node


def build_trie(words):
    trie = Trie()
    for word in words:
        trie.insert(word)
    return trie


def find_words(grid, trie, start_row, start_col, used_positions):
    rows, cols = len(grid), len(grid[0])
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    found_words = []

    def dfs(row, col, node, path, current_word):
        if node.is_word and len(current_word) > 1:
            found_words.append((current_word, path[:]))

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < rows and 0 <= new_col < cols and
                    (new_row, new_col) not in used_positions and
                    (new_row, new_col) not in path):
                char = grid[new_row][new_col]
                if char in node.children:
                    new_path = path + [(new_row, new_col)]
                    dfs(new_row, new_col, node.children[char], new_path, current_word + char)

    start_char = grid[start_row][start_col]
    start_node = trie.search_prefix(start_char)
    if start_node:
        dfs(start_row, start_col, start_node, [(start_row, start_col)], start_char)

    return found_words


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


def find_words_parallel(grid, trie, used_positions):
    rows, cols = len(grid), len(grid[0])
    all_positions = [(r, c) for r in range(rows) for c in range(cols) if (r, c) not in used_positions]
    
    with multiprocessing.Pool() as pool:
        find_words_partial = partial(find_words, grid, trie, used_positions=used_positions)
        results = pool.starmap(find_words_partial, [(r, c) for r, c in all_positions])
    
    return [word for sublist in results for word in sublist]


def can_form_valid_words(grid, trie, used_positions):
    rows, cols = len(grid), len(grid[0])
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in used_positions:
                char = grid[r][c]
                if not trie.search_prefix(char):
                    return False
    return True


def solve(grid, words):
    rows, cols = len(grid), len(grid[0])
    used_positions = set()
    solution = []
    max_solution_length = 0

    trie = build_trie(words)

    plt.ion()
    plt.figure(figsize=(10, 10))

    def backtrack():
        nonlocal max_solution_length
        if len(used_positions) == rows * cols:
            return True

        found_words = find_words_parallel(grid, trie, used_positions)
        found_words.sort(key=lambda x: len(x[1]), reverse=True)  # Prioritize longer words

        for word, path in found_words:
            solution.append((word, path))
            used_positions.update(path)

            if check_isolated_letters(grid, used_positions) and can_form_valid_words(grid, trie, used_positions):
                if len(solution) > max_solution_length:
                    max_solution_length = len(solution)
                    print(f"{max_solution_length} words: {[word for word, _ in solution]}")
                    update_visualization(grid, solution)

                if backtrack():
                    return True

            used_positions.difference_update(path)
            solution.pop()
            update_visualization(grid, solution)
        
        print(f"Backtracking... {len(found_words)} words tried")
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


if __name__ == '__main__':
    multiprocessing.freeze_support()  # This line is necessary for Windows compatibility
    main()