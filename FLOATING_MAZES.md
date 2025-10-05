# Floating Mazes & Finish Lines Guide

## Overview

This guide explains the two special maze types: **Floating Mazes** (disconnected rooms) and **Finish Lines** (exit openings).

---

## Floating Mazes

### What is a Floating Maze?

A floating maze contains **disconnected rooms** or isolated sections that are not connected by continuous paths. This makes them **unsolvable by simple wall-following algorithms**.

### Why Use Floating Mazes?

**Testing Advanced Algorithms:**
- Frontier-based exploration
- Mapping and localization
- Decision-making when stuck
- Handling of disconnected spaces

**Realistic Scenarios:**
- Buildings with separate rooms
- Multi-floor layouts (simulated as disconnected)
- Areas with locked doors
- Partially explored environments

### How It Works

1. **Generation**: Standard maze is generated first
2. **Disconnection**: Random walls are added back to create 3-5 isolated regions
3. **Result**: Rooms that cannot be reached from each other

### Creating Floating Mazes

**Command Line:**
```bash
python3 maze_cli.py 10 --floating --seed 42
```

**Launch Script:**
```bash
./launch_mgen.sh
# Select option 6: Floating maze
```

**Advanced:**
```bash
python3 maze_cli.py 12 \
  --floating \
  --cell-size 2.5 \
  --wall-density 0.7 \
  --seed 100
```

### Navigation Challenges

#### What Doesn't Work:
- ❌ Simple wall-following (gets stuck in one room)
- ❌ Right-hand rule (only explores one section)
- ❌ Basic obstacle avoidance (can't find other rooms)

#### What's Required:
- ✅ Mapping system to track explored areas
- ✅ Frontier detection to find boundaries
- ✅ Path planning between frontiers
- ✅ Decision logic for when area is fully explored
- ✅ Backtracking to try different areas

### Algorithm Requirements

**Minimum Requirements:**
```cpp
class FloatingMazeNavigator {
    MazeMap map_;                    // Track explored areas
    FrontierDetector frontier_;      // Find unexplored boundaries
    PathPlanner planner_;            // Navigate to frontiers
    
    void explore() {
        while (!allFrontiersExplored()) {
            Frontier next = selectNextFrontier();
            navigateToFrontier(next);
            exploreArea();
        }
    }
};
```

**Key Components:**
1. **Mapping**: Build a grid map of explored/unexplored cells
2. **Frontier Detection**: Identify boundaries between known/unknown
3. **Frontier Selection**: Choose which frontier to explore next
4. **Path Planning**: Navigate to selected frontier
5. **Completion Detection**: Know when all reachable areas explored

### Testing Strategy

**Phase 1: Verify Detection**
```bash
# Small floating maze to verify detection
python3 maze_cli.py 5 --floating --seed 100
```
- Robot should detect it's stuck
- Should identify unexplored frontiers
- Should attempt to reach them

**Phase 2: Test Navigation**
```bash
# Medium maze with clear disconnections
python3 maze_cli.py 8 --floating --seed 200
```
- Test frontier selection logic
- Verify path planning works
- Check completion detection

**Phase 3: Full Challenge**
```bash
# Large complex floating maze
python3 maze_cli.py 12 --floating --wall-density 0.7 --seed 300
```
- Multiple disconnected regions
- Complex room layouts
- Full algorithm test

### Expected Behavior

**Standard Wall-Following:**
```
Start → Explore Room 1 → Get stuck → Keep circling Room 1 → Never finish
```

**Frontier-Based Exploration:**
```
Start → Explore Room 1 → Detect frontier → 
Try to reach frontier → Realize unreachable → 
Mark area as fully explored → Report completion
```

### Performance Metrics

**For Floating Mazes:**
- **Coverage**: % of reachable area explored
- **Efficiency**: Path length vs optimal
- **Detection Time**: How quickly stuck is detected
- **Frontier Count**: Number of frontiers identified
- **Completion**: Successfully identifies all reachable areas

---

## Finish Lines

### What is a Finish Line?

A finish line is an **exit opening** created by removing a wall segment at the maze edge. It provides a clear goal/completion point.

### Why Use Finish Lines?

**Goal Detection:**
- Robot can detect when maze is "solved"
- Clear stopping condition
- Visual feedback of completion

**Performance Metrics:**
- Time to reach exit
- Path efficiency
- Success rate

**Timed Challenges:**
- Race against clock
- Compare algorithm speeds
- Benchmark improvements

### How It Works

1. **Location**: Typically at opposite corner from start (0,0)
2. **Position**: Usually at (width-1, height-1)
3. **Opening**: East wall is removed to create exit
4. **Detection**: Robot's LiDAR sees opening (no wall on one side)

### Creating Finish Lines

**Command Line:**
```bash
python3 maze_cli.py 8 --finish-line --seed 42
```

**Launch Script:**
```bash
./launch_mgen.sh
# Select option 7: Maze with finish line
```

**Advanced:**
```bash
python3 maze_cli.py 10 \
  --finish-line \
  --cell-size 2.0 \
  --wall-density 1.0 \
  --seed 100
```

### Detection Methods

#### Method 1: LiDAR Detection
```cpp
bool isAtFinishLine(const SensorData& data) {
    // Finish line has opening on one side
    // Check for unusually large distance on one side
    const double opening_threshold = 5.0;  // meters
    
    return (data.right_distance > opening_threshold ||
            data.left_distance > opening_threshold);
}
```

#### Method 2: Position-Based
```cpp
bool isAtFinishLine(const RobotPose& pose) {
    // Finish line is at opposite corner
    const double finish_x = maze_width - 1;
    const double finish_y = maze_height - 1;
    const double threshold = 0.5;  // meters
    
    double distance = sqrt(
        pow(pose.x - finish_x, 2) + 
        pow(pose.y - finish_y, 2)
    );
    
    return distance < threshold;
}
```

#### Method 3: Combined
```cpp
bool isAtFinishLine(const SensorData& data, const RobotPose& pose) {
    return isAtFinishLine(data) && isAtFinishLine(pose);
}
```

### Use Cases

**1. Timed Challenges**
```bash
# Generate maze with finish line
python3 maze_cli.py 8 --finish-line --seed 100

# Measure time to completion
start_time = now()
navigate_maze()
if (isAtFinishLine()) {
    completion_time = now() - start_time
    print(f"Completed in {completion_time} seconds!")
}
```

**2. Algorithm Comparison**
```bash
# Same maze, different algorithms
for algorithm in [wall_following, astar, flood_fill]:
    time = test_algorithm(algorithm, seed=100)
    print(f"{algorithm}: {time}s")
```

**3. Success Rate Testing**
```bash
# Test multiple mazes
success_count = 0
for seed in range(100, 200):
    if test_maze(seed):
        success_count += 1
print(f"Success rate: {success_count}/100")
```

---

## Combined: Floating Maze with Finish Line

### Ultimate Challenge

Combine both features for the most challenging scenario:

```bash
python3 maze_cli.py 12 \
  --floating \
  --finish-line \
  --cell-size 2.5 \
  --wall-density 0.7 \
  --complexity 1.0 \
  --seed 42
```

### Requirements

**Must Have:**
- Frontier-based exploration
- Mapping system
- Goal detection
- Path planning
- Completion logic

**Algorithm Flow:**
```
1. Start exploration
2. Build map of reachable areas
3. Detect frontiers
4. Try to reach all frontiers
5. Detect finish line opening
6. Navigate to finish line
7. Report completion
```

### Success Criteria

**For Floating Maze with Finish:**
- ✅ Explores all reachable rooms
- ✅ Detects finish line opening
- ✅ Navigates to finish line
- ✅ Reports successful completion
- ✅ Handles unreachable areas gracefully

---

## Testing Progression

### Level 1: Standard Maze
```bash
python3 maze_cli.py 8 --seed 100
```
- Test basic wall-following
- Verify navigation works

### Level 2: Maze with Finish
```bash
python3 maze_cli.py 8 --finish-line --seed 100
```
- Add goal detection
- Test completion logic

### Level 3: Floating Maze
```bash
python3 maze_cli.py 10 --floating --seed 200
```
- Add frontier detection
- Test exploration logic

### Level 4: Combined Challenge
```bash
python3 maze_cli.py 12 --floating --finish-line --seed 300
```
- Full algorithm test
- All features required

---

## Troubleshooting

### Floating Maze Issues

**Robot keeps circling same room:**
- ✅ Add frontier detection
- ✅ Implement mapping
- ✅ Add stuck detection

**Can't find other rooms:**
- ✅ Rooms are disconnected (by design)
- ✅ Mark area as fully explored
- ✅ Report completion

**Algorithm crashes:**
- ✅ Handle case where no path exists
- ✅ Add timeout for stuck detection
- ✅ Implement graceful failure

### Finish Line Issues

**Robot doesn't detect finish:**
- ✅ Check LiDAR threshold (try 5.0m)
- ✅ Verify position calculation
- ✅ Add debug logging

**False positives:**
- ✅ Combine LiDAR + position checks
- ✅ Require both conditions
- ✅ Add confirmation delay

**Robot passes finish without stopping:**
- ✅ Check detection frequency (100Hz)
- ✅ Add stopping logic
- ✅ Reduce speed near goal

---

## Examples

### Example 1: Simple Floating Test
```bash
./launch_mgen.sh
# Select option 6
# Enter size: 6
# Enter seed: 42
```

### Example 2: Timed Challenge
```bash
./launch_mgen.sh
# Select option 7
# Enter size: 8
# Enter seed: 100
```

### Example 3: Ultimate Challenge
```bash
./launch_mgen.sh
# Select option 8 (Advanced)
# Size: 12
# Seed: 200
# Floating: y
# Finish line: y
```

---

**Version:** 1.0  
**Last Updated:** October 5, 2025  
**See Also:** `CONFIGURATION.md` for full parameter documentation
