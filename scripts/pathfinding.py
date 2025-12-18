"""
Pathfinding and movement range utilities
"""
from collections import deque


def get_reachable_tiles(level, start_x, start_y, movement_range, ignore_enemies=False):
    """
    Returns a set of all tiles reachable within movement_range from start position.
    Uses BFS to explore walkable tiles.

    Args:
        level: The Level instance
        start_x: Starting X grid position
        start_y: Starting Y grid position
        movement_range: Maximum number of tiles that can be moved
        ignore_enemies: If True, tiles with enemies are considered walkable

    Returns:
        Set of tuples (x, y) representing reachable tile positions
    """
    reachable = set()
    visited = {(start_x, start_y): 0}  # Maps position to distance from start
    queue = deque([(start_x, start_y, 0)])  # (x, y, distance)

    while queue:
        x, y, dist = queue.popleft()

        # Add current position to reachable set
        reachable.add((x, y))

        # If we've reached max distance, don't explore further from this tile
        if dist >= movement_range:
            continue

        # Check all 4 cardinal directions
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_x = x + dx
            next_y = y + dy
            next_pos = (next_x, next_y)

            # Skip if already visited with a shorter or equal path
            if next_pos in visited and visited[next_pos] <= dist + 1:
                continue

            # Check if tile is walkable
            if not level.is_walkable(next_x, next_y):
                continue

            # Check for enemies if not ignoring them
            if not ignore_enemies and level.get_enemy_at(next_x, next_y):
                continue

            # Mark as visited and add to queue
            visited[next_pos] = dist + 1
            queue.append((next_x, next_y, dist + 1))

    return reachable


def find_path_bfs(level, start_x, start_y, goal_x, goal_y, max_distance=None):
    """
    Finds the shortest path from start to goal using BFS.

    Args:
        level: The Level instance
        start_x: Starting X position
        start_y: Starting Y position
        goal_x: Goal X position
        goal_y: Goal Y position
        max_distance: Maximum path length (None for unlimited)

    Returns:
        List of (x, y) tuples representing the path, or None if no path found
    """
    if start_x == goal_x and start_y == goal_y:
        return [(start_x, start_y)]

    visited = {(start_x, start_y)}
    queue = deque([[(start_x, start_y)]])  # Queue of paths

    while queue:
        path = queue.popleft()
        x, y = path[-1]

        # Check if we've exceeded max distance
        if max_distance and len(path) > max_distance:
            continue

        # Check all 4 cardinal directions
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_x = x + dx
            next_y = y + dy
            next_pos = (next_x, next_y)

            # Skip if already visited
            if next_pos in visited:
                continue

            # Check if we reached the goal
            if next_x == goal_x and next_y == goal_y:
                return path + [next_pos]

            # Check if tile is walkable
            if not level.is_walkable(next_x, next_y):
                continue

            # Mark as visited and add new path to queue
            visited.add(next_pos)
            queue.append(path + [next_pos])

    return None  # No path found


def get_next_step_towards(level, start_x, start_y, goal_x, goal_y):
    """
    Returns the next tile to move to when pathfinding towards a goal.

    Args:
        level: The Level instance
        start_x: Starting X position
        start_y: Starting Y position
        goal_x: Goal X position
        goal_y: Goal Y position

    Returns:
        Tuple (x, y) of next step, or None if no path exists
    """
    path = find_path_bfs(level, start_x, start_y, goal_x, goal_y)

    if path and len(path) > 1:
        return path[1]  # Return the next step (index 0 is current position)

    return None
