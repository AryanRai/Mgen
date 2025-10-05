# Maze Generator Configuration Guide

## Overview

The maze generator supports extensive configuration to create mazes with different characteristics for testing your robot's navigation capabilities.

## Parameters

### 1. Maze Size
**Parameter:** `size` (required)  
**Type:** Integer  
**Range:** 5-20 (recommended)  
**Description:** Creates a square maze of size × size cells

**Examples:**
```bash
python3 maze_cli.py 8              # 8x8 maze
python3 maze_cli.py 12             # 12x12 maze
```

**Guidelines:**
- **5x5**: Quick tests, ~1 minute to solve
- **8x8**: Good challenge, ~3 minutes
- **10x10**: Hard, ~5 minutes
- **12x12+**: Very challenging, 10+ minutes

---

### 2. Cell Size (Corridor Width)
**Parameter:** `--cell-size`  
**Type:** Float  
**Default:** 2.0 meters  
**Range:** 1.0-4.0 (recommended)  
**Description:** Distance between parallel walls (corridor width)

**Examples:**
```bash
python3 maze_cli.py 8 --cell-size 1.5    # Narrow corridors
python3 maze_cli.py 8 --cell-size 2.0    # Standard corridors (default)
python3 maze_cli.py 8 --cell-size 3.0    # Wide corridors
```

**Impact on Navigation:**
- **1.0-1.5m**: Narrow - Tests precise wall following
- **2.0-2.5m**: Standard - Good for general testing
- **3.0-4.0m**: Wide - Tests centering mode, easier navigation

**Robot Considerations:**
- TurtleBot3 Burger width: ~0.14m
- Minimum safe corridor: ~0.5m
- Recommended minimum: 1.0m for comfortable navigation

---

### 3. Wall Height
**Parameter:** `--wall-height`  
**Type:** Float  
**Default:** 0.5 meters  
**Range:** 0.2-2.0 (recommended)  
**Description:** Height of maze walls

**Examples:**
```bash
python3 maze_cli.py 8 --wall-height 0.3    # Low walls
python3 maze_cli.py 8 --wall-height 0.5    # Standard walls (default)
python3 maze_cli.py 8 --wall-height 1.0    # Tall walls
```

**Impact:**
- **0.2-0.4m**: Low walls, easier to see over in visualization
- **0.5-0.7m**: Standard, good visibility
- **0.8-2.0m**: Tall walls, more realistic indoor environment

**Note:** Wall height doesn't affect LiDAR-based navigation (LiDAR is horizontal plane)

---

### 4. Wall Thickness
**Parameter:** `--wall-thickness`  
**Type:** Float  
**Default:** 0.1 meters  
**Range:** 0.05-0.3 (recommended)  
**Description:** Thickness of maze walls

**Examples:**
```bash
python3 maze_cli.py 8 --wall-thickness 0.05   # Thin walls
python3 maze_cli.py 8 --wall-thickness 0.1    # Standard walls (default)
python3 maze_cli.py 8 --wall-thickness 0.2    # Thick walls
```

**Impact:**
- **0.05-0.08m**: Thin walls, more space in corridors
- **0.1-0.15m**: Standard, realistic
- **0.2-0.3m**: Thick walls, reduces effective corridor width

**Effective Corridor Width:**
```
Effective Width = Cell Size - Wall Thickness
```

---

### 5. Wall Density
**Parameter:** `--wall-density`  
**Type:** Float  
**Default:** 1.0  
**Range:** 0.0-1.0  
**Description:** Percentage of walls to keep after maze generation

**Examples:**
```bash
python3 maze_cli.py 8 --wall-density 1.0     # All walls (perfect maze)
python3 maze_cli.py 8 --wall-density 0.8     # 80% walls, some removed
python3 maze_cli.py 8 --wall-density 0.5     # 50% walls, very open
python3 maze_cli.py 8 --wall-density 0.2     # 20% walls, mostly open
```

**Impact on Maze:**
- **1.0**: Perfect maze, single solution path, all walls present
- **0.7-0.9**: Multiple paths, some shortcuts
- **0.4-0.6**: Very open, many alternative routes
- **0.0-0.3**: Almost no walls, open space with obstacles

**Use Cases:**
- **1.0**: Test pure wall-following algorithms
- **0.7-0.9**: Test decision-making at intersections
- **0.4-0.6**: Test open-space navigation
- **0.0-0.3**: Test obstacle avoidance in open areas

---

### 6. Complexity
**Parameter:** `--complexity`  
**Type:** Float  
**Default:** 1.0  
**Range:** 0.0-1.0  
**Description:** Affects maze branching and path complexity

**Examples:**
```bash
python3 maze_cli.py 8 --complexity 1.0       # Maximum complexity
python3 maze_cli.py 8 --complexity 0.7       # Moderate complexity
python3 maze_cli.py 8 --complexity 0.3       # Simple paths
```

**Impact:**
- **1.0**: Maximum branching, many dead ends
- **0.5-0.8**: Balanced, some branching
- **0.0-0.4**: Simpler paths, fewer dead ends

**Note:** Currently affects generation algorithm behavior

---

### 7. Random Seed
**Parameter:** `--seed`  
**Type:** Integer  
**Default:** Random  
**Description:** Seed for reproducible maze generation

**Examples:**
```bash
python3 maze_cli.py 8 --seed 42              # Always generates same maze
python3 maze_cli.py 8 --seed 100             # Different but reproducible
python3 maze_cli.py 8                        # Random maze each time
```

**Use Cases:**
- **Testing**: Use same seed to test algorithm improvements
- **Benchmarking**: Compare different navigation strategies
- **Debugging**: Reproduce specific maze configurations
- **Sharing**: Share seed to let others test same maze

---

### 8. Floating Maze
**Parameter:** `--floating`  
**Type:** Flag (boolean)  
**Default:** False  
**Description:** Creates disconnected rooms (unsolvable by wall-following alone)

**Examples:**
```bash
python3 maze_cli.py 10 --floating            # Floating maze
python3 maze_cli.py 10 --floating --seed 42  # Reproducible floating maze
```

**Impact:**
- Creates 3-5 isolated regions within the maze
- Rooms are not connected by continuous paths
- **Unsolvable by simple wall-following algorithms**
- Requires frontier-based exploration or mapping

**Use Cases:**
- **Test advanced algorithms**: Requires exploration + mapping
- **Test frontier detection**: Robot must find unexplored areas
- **Test decision making**: When to give up on current area
- **Realistic scenarios**: Simulates buildings with separate rooms

**Navigation Requirements:**
- Mapping system to track explored areas
- Frontier detection to find boundaries
- Path planning to navigate between frontiers
- Decision logic for when area is fully explored

**Warning:** Standard wall-following will get stuck in one room!

---

### 9. Finish Line
**Parameter:** `--finish-line`  
**Type:** Flag (boolean)  
**Default:** False  
**Description:** Adds an exit opening at the maze edge (goal marker)

**Examples:**
```bash
python3 maze_cli.py 8 --finish-line          # Maze with exit
python3 maze_cli.py 10 --finish-line --seed 100  # Reproducible with exit
```

**Impact:**
- Opens one wall at the opposite corner from start (0,0)
- Creates a clear "exit" point
- Typically at position (width-1, height-1)
- Removes east wall to create opening

**Use Cases:**
- **Goal detection**: Robot can detect when maze is "solved"
- **Performance metrics**: Measure time to reach exit
- **Completion testing**: Verify robot finds the goal
- **Visual feedback**: Clear indication of maze completion

**Detection:**
- Robot can detect opening with LiDAR (no wall on one side)
- Can be used as stopping condition
- Useful for timed challenges

**Note:** Works with both standard and floating mazes

---

## Configuration Presets

### Preset 1: Narrow Challenge
```bash
python3 maze_cli.py 10 \
  --cell-size 1.2 \
  --wall-density 1.0 \
  --complexity 1.0 \
  --seed 100
```
**Purpose:** Test precise wall following in tight spaces

### Preset 2: Wide Open
```bash
python3 maze_cli.py 8 \
  --cell-size 3.5 \
  --wall-density 0.6 \
  --complexity 0.5 \
  --seed 200
```
**Purpose:** Test centering mode and open-space navigation

### Preset 3: Standard Test
```bash
python3 maze_cli.py 8 \
  --cell-size 2.0 \
  --wall-density 1.0 \
  --complexity 1.0 \
  --seed 300
```
**Purpose:** Balanced test for general navigation

### Preset 4: Obstacle Course
```bash
python3 maze_cli.py 12 \
  --cell-size 2.5 \
  --wall-density 0.3 \
  --wall-thickness 0.15 \
  --seed 400
```
**Purpose:** Test obstacle avoidance in open space

### Preset 5: Realistic Indoor
```bash
python3 maze_cli.py 10 \
  --cell-size 2.5 \
  --wall-height 1.0 \
  --wall-thickness 0.15 \
  --wall-density 0.8 \
  --seed 500
```
**Purpose:** Simulate realistic indoor environment

### Preset 6: Floating Rooms Challenge
```bash
python3 maze_cli.py 10 \
  --cell-size 2.0 \
  --wall-density 0.8 \
  --floating \
  --seed 600
```
**Purpose:** Test frontier-based exploration (unsolvable by wall-following)

### Preset 7: Timed Challenge with Exit
```bash
python3 maze_cli.py 8 \
  --cell-size 2.0 \
  --wall-density 1.0 \
  --finish-line \
  --seed 700
```
**Purpose:** Timed maze solving with clear goal

### Preset 8: Complex Floating with Exit
```bash
python3 maze_cli.py 12 \
  --cell-size 2.5 \
  --wall-density 0.7 \
  --complexity 1.0 \
  --floating \
  --finish-line \
  --seed 800
```
**Purpose:** Ultimate challenge - disconnected rooms with goal detection

---

## Using with Launch Script

The `launch_mgen.sh` script provides easy access to these parameters:

### Quick Start (Presets)
```bash
./launch_mgen.sh
# Select option 1-5 for preset configurations
```

### Advanced Configuration
```bash
./launch_mgen.sh
# Select option 6 for custom parameters
# You'll be prompted for each parameter
```

---

## Parameter Combinations

### For Testing Wall Following
```bash
--cell-size 1.5 --wall-density 1.0 --complexity 1.0
```
- Narrow corridors
- All walls present
- Maximum complexity

### For Testing Centering Mode
```bash
--cell-size 3.0 --wall-density 1.0 --complexity 0.7
```
- Wide corridors
- All walls present
- Moderate complexity

### For Testing Decision Making
```bash
--cell-size 2.0 --wall-density 0.7 --complexity 0.8
```
- Standard corridors
- Multiple paths available
- Good branching

### For Performance Testing
```bash
--cell-size 2.5 --wall-density 0.5 --complexity 0.5
```
- Wide corridors
- Many shortcuts
- Moderate complexity
- Faster completion times

---

## Tips and Best Practices

### 1. Start Simple
Begin with default parameters and adjust one at a time to understand impact.

### 2. Match Robot Capabilities
- Narrow corridors (1.0-1.5m) for precise control testing
- Wide corridors (2.5-3.5m) for centering and speed

### 3. Use Seeds for Comparison
Always use the same seed when comparing:
- Different navigation algorithms
- Different parameter tunings
- Before/after code changes

### 4. Consider Computation
Larger mazes (15x15+) with high complexity take longer to:
- Generate
- Render in Gazebo
- Navigate

### 5. Test Edge Cases
- Very narrow: `--cell-size 1.0`
- Very wide: `--cell-size 4.0`
- Very sparse: `--wall-density 0.2`
- Very dense: `--wall-density 1.0`

---

## Troubleshooting

### Maze Too Easy
- Increase size
- Increase complexity
- Increase wall density
- Decrease cell size

### Maze Too Hard
- Decrease size
- Decrease complexity
- Decrease wall density
- Increase cell size

### Robot Gets Stuck
- Increase cell size (wider corridors)
- Decrease wall thickness
- Decrease wall density (more openings)

### Robot Oscillates
- Increase cell size (more room to center)
- Use right wall follow mode instead of centering
- Adjust control gains in code

### Generation Fails
- Check size is reasonable (5-20)
- Ensure cell size > wall thickness
- Verify all parameters are positive numbers

---

## Examples

### Example 1: Quick Test Maze
```bash
python3 maze_cli.py 5 --seed 42
```

### Example 2: Challenging Narrow Maze
```bash
python3 maze_cli.py 12 \
  --cell-size 1.3 \
  --wall-density 1.0 \
  --complexity 1.0 \
  --seed 100
```

### Example 3: Open Training Ground
```bash
python3 maze_cli.py 10 \
  --cell-size 3.0 \
  --wall-density 0.4 \
  --complexity 0.5 \
  --seed 200
```

### Example 4: Realistic Office Layout
```bash
python3 maze_cli.py 8 \
  --cell-size 2.5 \
  --wall-height 1.0 \
  --wall-thickness 0.15 \
  --wall-density 0.7 \
  --complexity 0.6 \
  --seed 300
```

---

## Advanced Usage

### Batch Generation
Create multiple test mazes:
```bash
for seed in 100 200 300 400 500; do
  python3 maze_cli.py 8 --seed $seed -o maze_test_$seed.world
done
```

### Parameter Sweep
Test different corridor widths:
```bash
for size in 1.5 2.0 2.5 3.0; do
  python3 maze_cli.py 8 --cell-size $size --seed 100 -o maze_width_$size.world
done
```

---

**Version:** 1.0  
**Last Updated:** October 5, 2025
