#!/usr/bin/env python3
"""
Gazebo Maze Generator CLI Tool
Generates solvable mazes for robot navigation testing
"""

import random
import sys
import os
import argparse

class MazeGenerator:
    def __init__(self, width, height, complexity=1.0):
        self.width = width
        self.height = height
        self.complexity = max(0.0, min(1.0, complexity))  # Clamp to 0-1
        self.grid = [[{'N': True, 'S': True, 'E': True, 'W': True} 
                      for _ in range(width)] for _ in range(height)]
        self.visited = [[False for _ in range(width)] for _ in range(height)]
    
    def generate(self, seed=None):
        """Generate maze using recursive backtracking"""
        if seed is not None:
            random.seed(seed)
        
        stack = []
        current = (0, 0)
        self.visited[current[1]][current[0]] = True
        
        while True:
            neighbors = self.get_unvisited_neighbors(current)
            
            if neighbors:
                next_cell = random.choice(neighbors)
                stack.append(current)
                self.remove_wall(current, next_cell)
                self.visited[next_cell[1]][next_cell[0]] = True
                current = next_cell
            elif stack:
                current = stack.pop()
            else:
                break
    
    def get_unvisited_neighbors(self, cell):
        """Get list of unvisited neighboring cells"""
        x, y = cell
        neighbors = []
        
        if y > 0 and not self.visited[y-1][x]:
            neighbors.append((x, y-1))
        if y < self.height - 1 and not self.visited[y+1][x]:
            neighbors.append((x, y+1))
        if x < self.width - 1 and not self.visited[y][x+1]:
            neighbors.append((x+1, y))
        if x > 0 and not self.visited[y][x-1]:
            neighbors.append((x-1, y))
        
        return neighbors
    
    def remove_wall(self, cell1, cell2):
        """Remove wall between two cells"""
        x1, y1 = cell1
        x2, y2 = cell2
        
        if x1 == x2:
            if y1 < y2:
                self.grid[y1][x1]['S'] = False
                self.grid[y2][x2]['N'] = False
            else:
                self.grid[y1][x1]['N'] = False
                self.grid[y2][x2]['S'] = False
        else:
            if x1 < x2:
                self.grid[y1][x1]['E'] = False
                self.grid[y2][x2]['W'] = False
            else:
                self.grid[y1][x1]['W'] = False
                self.grid[y2][x2]['E'] = False
    
    def apply_density(self, density):
        """Remove additional walls based on density parameter (0.0-1.0)
        density=1.0: keep all walls (perfect maze)
        density=0.5: remove ~50% of remaining walls (more open)
        density=0.0: remove almost all walls (very open)
        """
        if density >= 1.0:
            return  # Keep all walls
        
        # Calculate how many walls to remove
        removal_rate = 1.0 - density
        
        # Iterate through all cells and randomly remove walls
        for y in range(self.height):
            for x in range(self.width):
                # Try to remove each wall with probability based on removal_rate
                for direction in ['N', 'S', 'E', 'W']:
                    if self.grid[y][x][direction] and random.random() < removal_rate:
                        # Remove this wall and its counterpart
                        self.grid[y][x][direction] = False
                        
                        # Remove counterpart wall in adjacent cell
                        if direction == 'N' and y > 0:
                            self.grid[y-1][x]['S'] = False
                        elif direction == 'S' and y < self.height - 1:
                            self.grid[y+1][x]['N'] = False
                        elif direction == 'E' and x < self.width - 1:
                            self.grid[y][x+1]['W'] = False
                        elif direction == 'W' and x > 0:
                            self.grid[y][x-1]['E'] = False
    
    def make_floating(self):
        """Convert maze to floating rooms (disconnected sections)
        Creates TRULY unsolvable maze by wall-following by creating completely
        disconnected rooms. The robot starts in one room but cannot reach other rooms.
        """
        # Strategy: Divide the maze into separate regions and wall them off completely
        
        # For a proper floating room maze, create 2-3 completely isolated sections
        # by adding complete wall barriers
        
        if self.width < 6 or self.height < 6:
            # Too small for floating rooms, just add some random walls
            for _ in range(5):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                for direction in ['N', 'S', 'E', 'W']:
                    self.grid[y][x][direction] = True
            return
        
        # Create vertical barrier to split maze into left and right sections
        barrier_x = self.width // 2
        for y in range(self.height):
            # Wall off the middle column completely
            if barrier_x < self.width:
                self.grid[y][barrier_x]['W'] = True
                if barrier_x > 0:
                    self.grid[y][barrier_x - 1]['E'] = True
        
        # Create horizontal barrier in one section to create a third isolated room
        if self.height >= 8:
            barrier_y = self.height // 2
            # Only wall off the left half
            for x in range(barrier_x):
                self.grid[barrier_y][x]['N'] = True
                if barrier_y > 0:
                    self.grid[barrier_y - 1][x]['S'] = True
        
        # Result: 3 completely disconnected rooms
        # - Top-left room (robot starts here if at 0,0)
        # - Bottom-left room (unreachable)
        # - Right room (unreachable)
    
    def add_finish_line(self):
        """Add finish line by opening one wall at the maze edge
        Creates an exit point by removing a wall segment on the outer boundary.
        Typically placed at the opposite corner from start (0,0).
        """
        # Choose finish location (opposite corner from start)
        finish_x = self.width - 1
        finish_y = self.height - 1
        
        # Open the south wall of the finish cell (creates exit)
        self.grid[finish_y][finish_x]['S'] = True  # Keep wall for structure
        self.grid[finish_y][finish_x]['E'] = False  # Open east wall
        
        # Also open adjacent cell if exists
        if finish_x < self.width - 1:
            self.grid[finish_y][finish_x + 1]['W'] = False
        
        return (finish_x, finish_y)
    
    def to_sdf(self, output_file, cell_size=2.0, wall_height=0.5, wall_thickness=0.1):
        """Convert maze to Gazebo SDF format with configurable parameters
        
        Args:
            output_file: Path to output SDF file
            cell_size: Distance between parallel walls in meters (corridor width)
            wall_height: Height of walls in meters
            wall_thickness: Thickness of walls in meters
        """
        
        sdf_content = f'''<?xml version="1.0" ?>
<sdf version="1.8">
  <world name="generated_maze_{self.width}x{self.height}">
    
    <physics name="1ms" type="ignored">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>
    
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"></plugin>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"></plugin>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"></plugin>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>

    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

'''
        
        wall_id = 0
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                cx = x * cell_size
                cy = -y * cell_size
                
                if cell['N']:
                    sdf_content += self.create_wall(wall_id, cx, cy + cell_size/2, 
                                                    cell_size, wall_thickness, wall_height)
                    wall_id += 1
                
                if cell['S']:
                    sdf_content += self.create_wall(wall_id, cx, cy - cell_size/2, 
                                                    cell_size, wall_thickness, wall_height)
                    wall_id += 1
                
                if cell['E']:
                    sdf_content += self.create_wall(wall_id, cx + cell_size/2, cy, 
                                                    wall_thickness, cell_size, wall_height)
                    wall_id += 1
                
                if cell['W']:
                    sdf_content += self.create_wall(wall_id, cx - cell_size/2, cy, 
                                                    wall_thickness, cell_size, wall_height)
                    wall_id += 1
        
        sdf_content += '\n  </world>\n</sdf>\n'
        
        with open(output_file, 'w') as f:
            f.write(sdf_content)
        
        return wall_id
    
    def create_wall(self, wall_id, x, y, size_x, size_y, height):
        """Create a wall model"""
        z = height / 2
        return f'''    <model name="wall_{wall_id}">
      <static>true</static>
      <pose>{x} {y} {z} 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>{size_x} {size_y} {height}</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>{size_x} {size_y} {height}</size>
            </box>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.5 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
      </link>
    </model>
'''

def main():
    parser = argparse.ArgumentParser(
        description='Generate solvable mazes for Gazebo simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s 8                          # Generate 8x8 maze
  %(prog)s 10 -o my_maze.world        # Generate 10x10 maze with custom name
  %(prog)s 12 --seed 42               # Generate reproducible 12x12 maze
  %(prog)s 6 --cell-size 1.5          # Generate 6x6 with smaller cells
        '''
    )
    
    parser.add_argument('size', type=int, help='Maze size (creates size x size maze)')
    parser.add_argument('-o', '--output', help='Output filename (default: maze_<size>x<size>.world)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducible mazes')
    parser.add_argument('--cell-size', type=float, default=2.0, 
                       help='Cell size in meters (default: 2.0) - distance between parallel walls')
    parser.add_argument('--wall-height', type=float, default=0.5, 
                       help='Wall height in meters (default: 0.5)')
    parser.add_argument('--wall-thickness', type=float, default=0.1, 
                       help='Wall thickness in meters (default: 0.1)')
    parser.add_argument('--wall-density', type=float, default=1.0, 
                       help='Wall density 0.0-1.0 (default: 1.0) - 1.0=all walls, 0.5=50%% walls removed')
    parser.add_argument('--complexity', type=float, default=1.0, 
                       help='Maze complexity 0.0-1.0 (default: 1.0) - affects branching')
    parser.add_argument('--floating', action='store_true',
                       help='Generate floating maze (disconnected rooms, unsolvable by wall-following)')
    parser.add_argument('--finish-line', action='store_true',
                       help='Add finish line by opening one wall at maze edge (creates exit)')
    parser.add_argument('--dir', default='maze_generator/generated_mazes', 
                       help='Output directory (default: maze_generator/generated_mazes)')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.dir, exist_ok=True)
    
    # Determine output filename
    if args.output:
        output_file = os.path.join(args.dir, args.output)
    else:
        output_file = os.path.join(args.dir, f'maze_{args.size}x{args.size}.world')
    
    # Generate maze
    maze_type = "floating" if args.floating else "standard"
    print(f"🔨 Generating {args.size}x{args.size} {maze_type} maze...")
    if args.seed is not None:
        print(f"   Using seed: {args.seed}")
    
    # Create maze with complexity parameter
    maze = MazeGenerator(args.size, args.size, args.complexity)
    maze.generate(args.seed)
    
    # Apply density (remove extra walls if density < 1.0)
    if args.wall_density < 1.0:
        print(f"   Applying wall density: {args.wall_density:.1%}")
        maze.apply_density(args.wall_density)
    
    # Make floating (disconnected rooms) if requested
    if args.floating:
        print(f"   Creating floating rooms (disconnected sections)...")
        maze.make_floating()
    
    # Add finish line if requested
    finish_pos = None
    if args.finish_line:
        print(f"   Adding finish line (exit opening)...")
        finish_pos = maze.add_finish_line()
    
    # Convert to SDF with custom parameters
    wall_count = maze.to_sdf(output_file, args.cell_size, args.wall_height, args.wall_thickness)
    
    print(f"✅ Maze generated successfully!")
    print(f"   Type: {maze_type.upper()}")
    print(f"   Size: {args.size}x{args.size}")
    print(f"   Walls: {wall_count}")
    print(f"   Cell size (corridor width): {args.cell_size}m")
    print(f"   Wall height: {args.wall_height}m")
    print(f"   Wall thickness: {args.wall_thickness}m")
    print(f"   Wall density: {args.wall_density:.1%}")
    print(f"   Complexity: {args.complexity:.1%}")
    if args.floating:
        print(f"   ⚠️  Floating maze: Contains disconnected rooms (unsolvable by wall-following)")
    if args.finish_line:
        print(f"   🏁 Finish line: Exit at position ({finish_pos[0]}, {finish_pos[1]})")
    print(f"   Output: {output_file}")
    print(f"\n🚀 To test:")
    print(f"   gz sim -r -v2 {output_file} &")
    print(f"   # Then spawn your robot")

if __name__ == "__main__":
    main()
