#!/bin/bash
# Launch generated mazes with TurtleBot3

echo "=========================================="
echo "Maze Generator & Launcher"
echo "=========================================="
echo ""
echo "Select maze type:"
echo ""
echo "  1) Small Maze 5x5 (Quick test - ~1 min)"
echo "  2) Medium Maze 8x8 (Good challenge - ~3 min)"
echo "  3) Large Maze 10x10 (Hard - ~5 min)"
echo "  4) Extra Large 12x12 (Very hard - ~10 min)"
echo "  5) Custom size"
echo "  6) Floating maze (disconnected rooms - unsolvable)"
echo "  7) Maze with finish line (exit opening)"
echo "  8) Advanced configuration"
echo ""
read -p "Select option (1-8): " choice

case $choice in
    1)
        SIZE=5
        SEED=100
        CELL_SIZE=2.0
        WALL_HEIGHT=0.5
        WALL_THICKNESS=0.1
        WALL_DENSITY=1.0
        COMPLEXITY=1.0
        echo "🔨 Generating Small 5x5 Maze..."
        ;;
    2)
        SIZE=8
        SEED=200
        CELL_SIZE=2.0
        WALL_HEIGHT=0.5
        WALL_THICKNESS=0.1
        WALL_DENSITY=1.0
        COMPLEXITY=1.0
        echo "🔨 Generating Medium 8x8 Maze..."
        ;;
    3)
        SIZE=10
        SEED=300
        CELL_SIZE=2.0
        WALL_HEIGHT=0.5
        WALL_THICKNESS=0.1
        WALL_DENSITY=1.0
        COMPLEXITY=1.0
        echo "🔨 Generating Large 10x10 Maze..."
        ;;
    4)
        SIZE=12
        SEED=400
        CELL_SIZE=2.0
        WALL_HEIGHT=0.5
        WALL_THICKNESS=0.1
        WALL_DENSITY=1.0
        COMPLEXITY=1.0
        echo "🔨 Generating Extra Large 12x12 Maze..."
        ;;
    5)
        read -p "Enter maze size (5-20): " SIZE
        read -p "Enter seed (or press Enter for random): " SEED
        if [ -z "$SEED" ]; then
            SEED=$(date +%s)
        fi
        CELL_SIZE=2.0
        WALL_HEIGHT=0.5
        WALL_THICKNESS=0.1
        WALL_DENSITY=1.0
        COMPLEXITY=1.0
        echo "🔨 Generating Custom ${SIZE}x${SIZE} Maze..."
        ;;
    6)
        read -p "Enter maze size (5-20): " SIZE
        read -p "Enter seed (or press Enter for random): " SEED
        if [ -z "$SEED" ]; then
            SEED=$(date +%s)
        fi
        CELL_SIZE=2.0
        WALL_HEIGHT=0.5
        WALL_THICKNESS=0.1
        WALL_DENSITY=0.7
        COMPLEXITY=1.0
        FLOATING="--floating"
        FINISH_LINE=""
        echo "🔨 Generating Floating ${SIZE}x${SIZE} Maze (disconnected rooms)..."
        ;;
    7)
        read -p "Enter maze size (5-20): " SIZE
        read -p "Enter seed (or press Enter for random): " SEED
        if [ -z "$SEED" ]; then
            SEED=$(date +%s)
        fi
        CELL_SIZE=2.0
        WALL_HEIGHT=0.5
        WALL_THICKNESS=0.1
        WALL_DENSITY=1.0
        COMPLEXITY=1.0
        FLOATING=""
        FINISH_LINE="--finish-line"
        echo "🔨 Generating ${SIZE}x${SIZE} Maze with finish line..."
        ;;
    8)
        echo ""
        echo "Advanced Configuration"
        echo "======================"
        read -p "Maze size (5-20): " SIZE
        read -p "Seed (or press Enter for random): " SEED
        if [ -z "$SEED" ]; then
            SEED=$(date +%s)
        fi
        read -p "Cell size/corridor width in meters (default 2.0): " CELL_SIZE
        CELL_SIZE=${CELL_SIZE:-2.0}
        read -p "Wall height in meters (default 0.5): " WALL_HEIGHT
        WALL_HEIGHT=${WALL_HEIGHT:-0.5}
        read -p "Wall thickness in meters (default 0.1): " WALL_THICKNESS
        WALL_THICKNESS=${WALL_THICKNESS:-0.1}
        read -p "Wall density 0.0-1.0 (1.0=all walls, 0.5=50% removed, default 1.0): " WALL_DENSITY
        WALL_DENSITY=${WALL_DENSITY:-1.0}
        read -p "Complexity 0.0-1.0 (default 1.0): " COMPLEXITY
        COMPLEXITY=${COMPLEXITY:-1.0}
        read -p "Floating maze? (y/n, default n): " FLOATING_INPUT
        if [ "$FLOATING_INPUT" = "y" ] || [ "$FLOATING_INPUT" = "Y" ]; then
            FLOATING="--floating"
        else
            FLOATING=""
        fi
        read -p "Add finish line? (y/n, default n): " FINISH_INPUT
        if [ "$FINISH_INPUT" = "y" ] || [ "$FINISH_INPUT" = "Y" ]; then
            FINISH_LINE="--finish-line"
        else
            FINISH_LINE=""
        fi
        echo "🔨 Generating Custom ${SIZE}x${SIZE} Maze with advanced settings..."
        ;;
    *)
        echo "❌ Invalid choice. Exiting..."
        exit 1
        ;;
esac

# Initialize flags for options 1-5 if not set
FLOATING=${FLOATING:-""}
FINISH_LINE=${FINISH_LINE:-""}

# Build the command with all parameters
CMD="python3 maze_generator/maze_cli.py $SIZE --seed $SEED -o current_test_maze.world"
CMD="$CMD --cell-size $CELL_SIZE"
CMD="$CMD --wall-height $WALL_HEIGHT"
CMD="$CMD --wall-thickness $WALL_THICKNESS"
CMD="$CMD --wall-density $WALL_DENSITY"
CMD="$CMD --complexity $COMPLEXITY"
CMD="$CMD $FLOATING"
CMD="$CMD $FINISH_LINE"

# Generate the maze
$CMD

if [ $? -ne 0 ]; then
    echo "❌ Failed to generate maze!"
    exit 1
fi

WORLD_FILE="maze_generator/generated_mazes/current_test_maze.world"

# Set up environment for Gazebo to find TurtleBot3 models
export TURTLEBOT3_MODEL=burger
cd turtlebot3_ws
source install/setup.bash

# Add TurtleBot3 models to Gazebo resource path
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:$(pwd)/install/turtlebot3_gazebo/share/turtlebot3_gazebo/models

cd ..

echo ""
echo "🚀 Launching Gazebo with generated maze..."
echo ""

# Launch Gazebo with the maze
gz sim -r -v2 "$WORLD_FILE" &
GZ_PID=$!

echo "⏳ Waiting for Gazebo to initialize..."
sleep 6

# Check if Gazebo is still running
if ! ps -p $GZ_PID > /dev/null; then
    echo "❌ Gazebo failed to start!"
    exit 1
fi

# Spawn TurtleBot3 using launch file
cd turtlebot3_ws

echo "🤖 Spawning TurtleBot3 at start position..."
ros2 launch turtlebot3_gazebo spawn_turtlebot3.launch.py x_pose:=1.0 y_pose:=-1.0 &
SPAWN_PID=$!

# Wait for spawn to complete
sleep 3

# Check if spawn was successful
if ps -p $SPAWN_PID > /dev/null 2>&1; then
    # Process still running, wait a bit more
    sleep 2
fi

echo ""
echo "✅ Maze launched successfully!"
echo ""
echo "📊 Maze Info:"
echo "   Size: ${SIZE}x${SIZE}"
echo "   Seed: ${SEED}"
echo "   Corridor width: ${CELL_SIZE}m"
echo "   Wall height: ${WALL_HEIGHT}m"
echo "   Wall thickness: ${WALL_THICKNESS}m"
echo "   Wall density: ${WALL_DENSITY}"
echo "   Complexity: ${COMPLEXITY}"
if [ -n "$FLOATING" ]; then
    echo "   ⚠️  Type: FLOATING (disconnected rooms)"
fi
if [ -n "$FINISH_LINE" ]; then
    echo "   🏁 Finish line: YES (exit opening added)"
fi
echo "   File: ../${WORLD_FILE}"
echo ""
echo "🎮 Next Steps:"
echo "   1. Open a new terminal"
echo "   2. Run: ./run_drive.sh"
echo "   3. Watch your robot navigate!"
echo ""
echo "💡 Tip: Use the same seed to get the same maze again"
echo ""
echo "Press Ctrl+C to stop (will keep Gazebo and robot running)"
echo "Or run ./kill_all.sh to stop everything"

# Keep script running so spawn process doesn't terminate
wait
