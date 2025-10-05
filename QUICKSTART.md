# Quick Start Guide

Get up and running with the Gazebo Maze Generator in 60 seconds.

## 1. Generate Your First Maze

```bash
python3 maze_cli.py 8
```

Output: `generated_mazes/maze_8x8.world`

## 2. Launch in Gazebo

```bash
gz sim -r -v2 generated_mazes/maze_8x8.world
```

## 3. Spawn Your Robot

In another terminal:
```bash
# Example for TurtleBot3
ros2 run ros_gz_sim create -topic /world/generated_maze_8x8/create \
  -file /path/to/your/robot.sdf \
  -x 1.0 -y -1.0 -z 0.01
```

## Common Commands

```bash
# Small test maze
python3 maze_cli.py 5

# Medium challenge
python3 maze_cli.py 10

# Large complex maze
python3 maze_cli.py 15

# Reproducible maze (same every time)
python3 maze_cli.py 8 --seed 42

# Custom name
python3 maze_cli.py 10 -o challenge_maze.world

# Smaller cells (tighter corridors)
python3 maze_cli.py 8 --cell-size 1.5
```

## Tips

- Start with 5x5 or 6x6 for testing
- Use `--seed` for consistent testing
- Default cell size (2.0m) works well for TurtleBot3
- Larger mazes (15x15+) are more challenging

## Need Help?

See the full [README.md](README.md) for detailed documentation.
