# MGen: Gazebo Maze Generator

A Python CLI tool for generating solvable mazes in Gazebo SDF format for robot navigation testing.

## Features

- **Guaranteed Solvable**: Uses recursive backtracking algorithm to ensure all mazes have a solution
- **Customizable Size**: Generate mazes from small (5x5) to large (20x20+)
- **Reproducible**: Use seeds to generate the same maze repeatedly
- **Gazebo Ready**: Outputs valid SDF world files compatible with Gazebo Sim
- **Configurable**: Adjust cell size and wall dimensions

## Installation

No installation required! Just Python 3.6+.

```bash
# Clone the repository
git clone <your-repo-url>
cd maze_generator

# Make the script executable (optional)
chmod +x maze_cli.py
```

## Quick Start

### Using the Launch Script (Recommended)
```bash
./launch_mgen.sh
# Select from preset configurations or use advanced mode
```

## Usage

### Basic Usage

Generate a simple 8x8 maze:
```bash
python3 maze_cli.py 8
```

This creates `maze_generator/generated_mazes/maze_8x8.world`

### Custom Output Name

```bash
python3 maze_cli.py 10 -o my_custom_maze.world
```

### Advanced Configuration

```bash
# Generate with custom corridor width
python3 maze_cli.py 8 --cell-size 2.5

# Generate with all custom parameters
python3 maze_cli.py 10 \
  --cell-size 2.0 \
  --wall-height 0.5 \
  --wall-thickness 0.1 \
  --wall-density 0.8 \
  --complexity 1.0 \
  --seed 100
```

## Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `size` | Required | Maze size (creates size×size maze) |
| `--cell-size` | 2.0 | Corridor width in meters (distance between parallel walls) |
| `--wall-height` | 0.5 | Wall height in meters |
| `--wall-thickness` | 0.1 | Wall thickness in meters |
| `--wall-density` | 1.0 | Wall density 0.0-1.0 (1.0=all walls, 0.5=50% removed) |
| `--complexity` | 1.0 | Maze complexity 0.0-1.0 (affects branching) |
| `--seed` | Random | Random seed for reproducibility |
| `-o, --output` | Auto | Output filename |
| `--dir` | generated_mazes | Output directory |

**📖 See `CONFIGURATION.md` for detailed parameter documentation, examples, and presets.**

### Reproducible Mazes

Use a seed to generate the same maze every time:
```bash
python3 maze_cli.py 12 --seed 42
```

### Adjust Cell Size

Change the size of each maze cell (default is 2.0 meters):
```bash
python3 maze_cli.py 6 --cell-size 1.5
```

### Custom Output Directory

```bash
python3 maze_cli.py 8 --dir /path/to/output
```

## Command Line Options

```
positional arguments:
  size                  Maze size (creates size x size maze)

optional arguments:
  -h, --help            Show help message
  -o, --output          Output filename (default: maze_<size>x<size>.world)
  --seed                Random seed for reproducible mazes
  --cell-size           Cell size in meters (default: 2.0)
  --dir                 Output directory (default: maze_generator/generated_mazes)
```

## Testing in Gazebo

After generating a maze, launch it in Gazebo:

```bash
# Launch the maze world
gz sim -r -v2 maze_generator/generated_mazes/maze_8x8.world
```

Then spawn your robot using your preferred method (ROS2 launch file, manual spawn, etc.)

## Examples

### Small Test Maze (5x5)
```bash
python3 maze_cli.py 5 --seed 100
```
Perfect for quick testing and debugging.

### Medium Challenge (10x10)
```bash
python3 maze_cli.py 10 --seed 200
```
Good balance between complexity and navigation time.

### Large Complex Maze (15x15)
```bash
python3 maze_cli.py 15 --seed 300
```
Challenging maze for advanced navigation algorithms.

### Compact Maze (smaller cells)
```bash
python3 maze_cli.py 8 --cell-size 1.5
```
Tighter corridors for testing precision navigation.

## Algorithm

The maze generator uses the **Recursive Backtracking** algorithm:

1. Start at cell (0, 0)
2. Mark current cell as visited
3. While there are unvisited cells:
   - If current cell has unvisited neighbors:
     - Choose random unvisited neighbor
     - Remove wall between current and chosen cell
     - Make chosen cell the current cell
   - Else backtrack to previous cell
4. Convert maze structure to Gazebo SDF format

This guarantees:
- Every cell is reachable from every other cell
- There is exactly one path between any two cells
- No isolated sections or unreachable areas

## Output Format

Generated files are valid Gazebo SDF 1.8 world files containing:
- Physics configuration
- Required Gazebo plugins (physics, sensors, scene broadcaster)
- Directional lighting
- Ground plane
- Wall models with collision and visual geometry

Walls are:
- Height: 0.5m (visible but allows overhead camera view)
- Thickness: 0.1m
- Material: Gray static geometry

## File Structure

```
maze_generator/
├── maze_cli.py              # Main CLI tool
├── generated_mazes/         # Output directory for generated mazes
│   └── *.world             # Generated SDF world files
└── README.md               # This file
```

## Integration with ROS2/TurtleBot3

Example launch script integration:

```bash
#!/bin/bash
# Launch generated maze
gz sim -r -v2 maze_generator/generated_mazes/maze_10x10.world &
sleep 5

# Spawn TurtleBot3
ros2 run ros_gz_sim create -topic /world/generated_maze_10x10/create \
  -file /path/to/turtlebot3.sdf \
  -x 1.0 -y -1.0 -z 0.01
```

## Tips

- **Start Small**: Test your navigation algorithm on 5x5 or 6x6 mazes first
- **Use Seeds**: When debugging, use the same seed to get consistent maze layouts
- **Cell Size**: Default 2.0m works well for TurtleBot3; adjust based on your robot size
- **Performance**: Larger mazes (20x20+) may impact Gazebo performance on slower systems

## Troubleshooting

**Maze doesn't load in Gazebo**
- Verify the output file exists in the specified directory
- Check Gazebo version compatibility (tested with Gazebo Sim 8)

**Robot gets stuck**
- Try increasing cell size with `--cell-size 2.5` or larger
- Ensure your robot's navigation algorithm handles tight corners

**Want different maze each time**
- Don't specify a seed, or use `--seed $(date +%s)` for time-based seeds

## License

MIT License - Feel free to use and modify for your projects.

## Contributing

Contributions welcome! Potential improvements:
- Add different maze generation algorithms (Prim's, Kruskal's)
- Support for rectangular (non-square) mazes
- Configurable wall heights and materials
- Start/goal position markers
- Maze difficulty ratings

## Author

Created for robot navigation testing and simulation environments.
