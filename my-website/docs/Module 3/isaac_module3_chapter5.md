# Chapter 5: Nav2 - Navigation for Humanoid and Mobile Robots

## Introduction

Nav2 is the ROS 2 navigation stack providing complete path planning and navigation capabilities. This chapter covers configuring Nav2 for different robot types, from mobile robots to complex humanoid systems, and implementing custom behaviors for task-specific navigation.

## Nav2 Architecture

### Navigation Stack Overview

```
Nav2 Stack:

User Application
      ↓
Navigation Goals/Tasks
      ↓
┌─────────────────────────────────────────┐
│       Behavior Tree Executor            │
├─────────────────────────────────────────┤
│  Manages high-level navigation tasks    │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼────────────────┐   ┌────▼──────────────┐
│  Global Planner    │   │  Local Planner    │
│  - Dijkstra        │   │  - DWA            │
│  - A*              │   │  - TEB            │
│  - Custom          │   │  - Custom         │
└───┬────────────────┘   └────┬──────────────┘
    │                         │
    └────────────┬────────────┘
                 │
        ┌────────▼─────────┐
        │  Motion Control  │
        │  - Vel commands  │
        │  - Footstep cmds │
        └────────┬─────────┘
                 │
           Robot Hardware
```

## Installation and Configuration

### Installation

```bash
#!/bin/bash
# Install Nav2

# Add ROS 2 repository
source /opt/ros/humble/setup.bash

# Install Nav2 packages
sudo apt install -y ros-humble-navigation2
sudo apt install -y ros-humble-nav2-bringup
sudo apt install -y ros-humble-nav2-core
sudo apt install -y ros-humble-nav2-msgs

# Optional: Install development tools
sudo apt install -y ros-humble-nav2-planner-server
sudo apt install -y ros-humble-nav2-controller-server
sudo apt install -y ros-humble-nav2-behaviors-server

# Build workspace
cd ~/nav2_ws
colcon build --symlink-install
```

### Basic Configuration (YAML)

```yaml
# nav2_config.yaml
# Configuration for Nav2

amcl:
  ros__parameters:
    # Particle filter parameters
    alpha1: 0.2
    alpha2: 0.2
    alpha3: 0.2
    alpha4: 0.2
    alpha5: 0.2
    base_frame_id: base_link
    beam_skip_distance: 0.5
    beam_skip_error_threshold: 0.9
    beam_skip_threshold: 0.3
    do_beamskip: false
    global_frame_id: map
    lambda_short: 0.1
    laser_likelihood_max_dist: 2.0
    laser_max_range: 100.0
    laser_min_range: 0.1
    max_beams: 360
    max_particles: 2000
    min_particles: 500
    odom_frame_id: odom
    pf_err: 0.05
    pf_z: 0.99
    recovery_alpha_fast: 0.0
    recovery_alpha_slow: 0.0
    resample_interval: 1
    robot_model_type: differential
    save_pose_rate: 0.5
    sigma_hit: 0.2
    sigma_z: 0.05
    tf_broadcast: true
    transform_tolerance: 1.0
    update_min_a: 0.2
    update_min_d: 0.25
    z_hit: 0.5
    z_max: 0.05
    z_rand: 0.5
    z_short: 0.05

bt_navigator:
  ros__parameters:
    default_bt_xml_filename: navigate_w_replanning_and_recovery.xml
    bt_loop_duration: 10
    default_server_timeout: 20

controller_server:
  ros__parameters:
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    failure_tolerance: 0.3
    progress_checker_plugin: progress_checker
    goal_checker_plugin: goal_checker
    controller_plugins: [FollowPath]

    # Controller plugin configuration
    FollowPath:
      plugin: nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController
      desired_linear_vel: 0.5
      lookahead_dist: 0.6
      min_lookahead_dist: 0.3
      max_lookahead_dist: 0.9
      lookahead_time: 1.5
      rotate_to_heading_angular_vel: 1.8
      transform_tolerance: 0.1
      use_velocity_scaled_lookahead_dist: false
      min_approach_linear_velocity: -0.5
      approach_velocity_scaling_dist: 0.6
      max_allowed_time_error: 1.0
      use_collision_detection: true
      collision_detection_time: -1.0

planner_server:
  ros__parameters:
    planner_plugins: [GridBased]
    use_sim_time: true

    GridBased:
      plugin: nav2_navfn_planner::NavfnPlanner
      tolerance: 0.5
      use_astar: false
      allow_unknown: false
      cost_travel_multiplier: 2.0

recoveries_server:
  ros__parameters:
    recovery_plugins: [spin, backup, wait]
    global_frame: map
    robot_base_frame: base_link
    transform_timeout: 0.1
    use_sim_time: true
    simulate_ahead_time: 2.0

    spin:
      plugin: nav2_behaviors::Spin
      simulate_ahead_time: 2.0
      max_rotations: 1
      max_time: 10

    backup:
      plugin: nav2_behaviors::BackUp
      simulate_ahead_time: 2.0
      required_movement_angle: 0.545
      movement_duration: 2

    wait:
      plugin: nav2_behaviors::Wait
      wait_duration: 2

map_server:
  ros__parameters:
    yaml_filename: map.yaml
    use_sim_time: true
```

## Path Planning

### Global Planning

```python
"""
Global path planning with Nav2
"""

import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path

class Nav2GlobalPlanner(Node):
    """
    Global path planning using Nav2
    """
    
    def __init__(self):
        super().__init__('global_planner')
        
        # Initialize Nav2 navigator
        self.navigator = BasicNavigator()
        
        # Publisher for planned path
        self.path_pub = self.create_publisher(Path, '/global_plan', 10)
    
    def plan_to_goal(self, goal_x: float, goal_y: float, 
                     goal_theta: float = 0.0) -> Path:
        """
        Plan path from current location to goal
        
        Args:
            goal_x, goal_y: Goal coordinates
            goal_theta: Goal orientation (radians)
        
        Returns:
            Path object containing waypoints
        """
        # Create goal pose
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = goal_x
        goal_pose.pose.position.y = goal_y
        
        # Convert angle to quaternion
        from scipy.spatial.transform import Rotation as R
        quat = R.from_euler('z', goal_theta).as_quat()
        goal_pose.pose.orientation.x = quat[0]
        goal_pose.pose.orientation.y = quat[1]
        goal_pose.pose.orientation.z = quat[2]
        goal_pose.pose.orientation.w = quat[3]
        
        # Request plan
        path = self.navigator.getPath(
            start=None,  # Use current pose
            goal=goal_pose
        )
        
        return path
    
    def navigate_to_goal(self, goal_x: float, goal_y: float, 
                        goal_theta: float = 0.0) -> TaskResult:
        """
        Navigate robot to goal location
        
        Returns:
            TaskResult indicating success/failure
        """
        # Create goal
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = goal_x
        goal_pose.pose.position.y = goal_y
        
        # Set orientation
        from scipy.spatial.transform import Rotation as R
        quat = R.from_euler('z', goal_theta).as_quat()
        goal_pose.pose.orientation.x = quat[0]
        goal_pose.pose.orientation.y = quat[1]
        goal_pose.pose.orientation.z = quat[2]
        goal_pose.pose.orientation.w = quat[3]
        
        # Send goal and monitor
        self.navigator.goToPose(goal_pose)
        
        # Wait for result
        while not self.navigator.isNavComplete():
            feedback = self.navigator.getFeedback()
            
            if feedback and feedback.estimated_time_remaining.sec > 0:
                minutes = feedback.estimated_time_remaining.sec // 60
                seconds = feedback.estimated_time_remaining.sec % 60
                self.get_logger().info(
                    f'Estimated time remaining: {minutes}m {seconds}s'
                )
        
        result = self.navigator.getResult()
        return result
```

### Local Planning

```python
"""
Local planning and obstacle avoidance
"""

class Nav2LocalPlanner(Node):
    """
    Local path planning with obstacle avoidance
    """
    
    def __init__(self):
        super().__init__('local_planner')
        
        # Local planner parameters
        self.max_linear_vel = 0.5
        self.max_angular_vel = 1.0
        self.obstacle_distance_threshold = 0.5
        
        # Velocity publisher
        self.vel_pub = self.create_publisher(
            Twist, '/cmd_vel', 10
        )
        
        # Costmap subscriber
        self.costmap_sub = self.create_subscription(
            OccupancyGrid, '/local_costmap/costmap',
            self.costmap_callback, 10
        )
        
        self.costmap = None
    
    def costmap_callback(self, msg):
        """Receive local costmap"""
        self.costmap = msg
    
    def compute_local_plan(self, current_pose, goal_pose) -> Twist:
        """
        Compute local velocity commands
        
        This uses obstacle avoidance (DWA, TEB)
        """
        # Dynamic Window Approach (DWA)
        # Evaluates multiple trajectories and picks best
        
        velocity = Twist()
        
        # Simple example: proportional control with collision avoidance
        dx = goal_pose.position.x - current_pose.position.x
        dy = goal_pose.position.y - current_pose.position.y
        
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance > 0.1:
            velocity.linear.x = min(
                self.max_linear_vel,
                distance  # Proportional to distance
            )
        
        # Check for obstacles
        if self.costmap and self._has_collision_ahead():
            # Slow down or stop
            velocity.linear.x *= 0.5
        
        return velocity
    
    def _has_collision_ahead(self) -> bool:
        """Check if obstacle ahead"""
        if self.costmap is None:
            return False
        
        # Check cells ahead of robot
        # This is a simplified check
        
        data = np.array(self.costmap.data).reshape(
            self.costmap.info.height,
            self.costmap.info.width
        )
        
        # Check forward direction
        forward_check = data[:, -5:]  # Last 5 columns
        
        # If any cell has high cost, obstacle exists
        has_obstacle = np.max(forward_check) > 50  # Threshold
        
        return has_obstacle
```

## Navigation for Humanoid Robots

### Bipedal Gait Planning

```python
"""
Specialized navigation for bipedal humanoid robots
"""

import numpy as np
from enum import Enum

class GaitType(Enum):
    """Different gait patterns"""
    WALK = 1
    RUN = 2
    CLIMB = 3
    BACKWARD = 4

class HumanoidNavigator(Node):
    """
    Navigation specialized for bipedal humanoids
    """
    
    def __init__(self):
        super().__init__('humanoid_navigator')
        
        # Navigation state
        self.current_gait = GaitType.WALK
        self.terrain_type = "flat"
        
        # Gait parameters
        self.gait_params = {
            GaitType.WALK: {
                'step_length': 0.5,
                'step_frequency': 1.5,  # steps/sec
                'hip_height': 0.9,
                'max_speed': 1.0
            },
            GaitType.RUN: {
                'step_length': 0.7,
                'step_frequency': 3.0,
                'hip_height': 0.85,
                'max_speed': 2.5
            },
            GaitType.CLIMB: {
                'step_length': 0.3,
                'step_frequency': 1.0,
                'hip_height': 1.0,
                'max_speed': 0.5
            }
        }
        
        # Footstep publisher
        self.footstep_pub = self.create_publisher(
            FootstepPlan, '/footstep_plan', 10
        )
        
        # IMU subscriber for balance
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10
        )
        
        self.pitch = 0.0
        self.roll = 0.0
    
    def imu_callback(self, msg):
        """Receive IMU data for balance monitoring"""
        # Extract orientation
        from scipy.spatial.transform import Rotation as R
        
        quat = [msg.orientation.x, msg.orientation.y, 
                msg.orientation.z, msg.orientation.w]
        
        rotation = R.from_quat(quat)
        euler = rotation.as_euler('xyz')
        
        self.roll = euler[0]
        self.pitch = euler[1]
    
    def select_gait(self, desired_speed: float) -> GaitType:
        """
        Select appropriate gait based on speed
        """
        if desired_speed < 0.3:
            return GaitType.WALK
        elif desired_speed < 1.5:
            return GaitType.WALK
        else:
            return GaitType.RUN
    
    def plan_footsteps(self, goal_pose, current_pose, 
                      desired_speed: float) -> list:
        """
        Plan footstep sequence to reach goal
        
        Returns:
            List of footstep poses
        """
        gait = self.select_gait(desired_speed)
        params = self.gait_params[gait]
        
        # Calculate distance to goal
        dx = goal_pose.position.x - current_pose.position.x
        dy = goal_pose.position.y - current_pose.position.y
        distance = np.sqrt(dx**2 + dy**2)
        goal_angle = np.arctan2(dy, dx)
        
        # Generate footstep sequence
        footsteps = []
        current_x = current_pose.position.x
        current_y = current_pose.position.y
        current_theta = 0.0
        
        # Estimate number of steps needed
        num_steps = int(distance / params['step_length']) + 1
        
        for i in range(num_steps):
            # Alternate between left and right foot
            is_left = (i % 2 == 0)
            
            # Generate footstep position
            step_progress = min(i / num_steps, 1.0)
            intermediate_x = current_pose.position.x + dx * step_progress
            intermediate_y = current_pose.position.y + dy * step_progress
            
            # Add lateral offset for left/right feet
            lateral_offset = 0.1 if is_left else -0.1
            foot_x = intermediate_x - np.sin(goal_angle) * lateral_offset
            foot_y = intermediate_y + np.cos(goal_angle) * lateral_offset
            
            footsteps.append({
                'position': [foot_x, foot_y],
                'yaw': goal_angle,
                'foot': 'left' if is_left else 'right',
                'swing_height': 0.1,
                'swing_time': 0.5
            })
        
        return footsteps
    
    def check_balance(self) -> bool:
        """
        Check if robot maintains balance
        """
        # Check if pitch/roll within acceptable limits
        max_tilt = 0.3  # radians (~17 degrees)
        
        is_balanced = (abs(self.roll) < max_tilt and 
                      abs(self.pitch) < max_tilt)
        
        if not is_balanced:
            self.get_logger().warn(
                f'Balance warning: roll={self.roll:.2f}, '
                f'pitch={self.pitch:.2f}'
            )
        
        return is_balanced
```

## Behavior Trees

### Behavior Tree Configuration

```xml
<!-- navigate_w_recovery.xml -->
<!-- Behavior tree for navigation with recovery -->

<root main_tree_to_execute = "MainTree">
  <BehaviorTree ID="MainTree">
    <Sequence name="Root">
      
      <!-- Initialize map -->
      <Action ID="InitializeMap"/>
      
      <!-- Main navigation loop -->
      <ForceSuccess>
        <Sequence name="NavigationSequence">
          
          <!-- Plan path -->
          <Action ID="ComputePath"/>
          
          <!-- Follow path with recovery -->
          <RecoveryNode>
            <FollowPath/>
            <Sequence name="Recovery">
              <Action ID="Spin"/>
              <Action ID="BackUp"/>
              <Action ID="Wait"/>
              <Action ID="ComputePath"/>
            </Sequence>
          </RecoveryNode>
          
          <!-- Check if reached goal -->
          <Action ID="IsGoalReached"/>
          
        </Sequence>
      </ForceSuccess>
      
    </Sequence>
  </BehaviorTree>
</root>
```

### Custom Behavior Implementation

```python
"""
Custom behavior for humanoid-specific navigation
"""

from nav2_core.behavior import Behavior
from nav_msgs.msg import Path

class HumanoidTraversalBehavior(Behavior):
    """
    Custom behavior for humanoid terrain traversal
    """
    
    def __init__(self):
        super().__init__('HumanoidTraversal')
        self.terrain_detector = TerrainDetector()
    
    def on_enter(self):
        """Initialize behavior"""
        self.terrain_type = self.terrain_detector.detect_terrain()
        self.get_logger().info(f'Detected terrain: {self.terrain_type}')
    
    def on_loop(self, **kwargs):
        """Execute behavior"""
        # Analyze terrain
        terrain = self.terrain_detector.detect_terrain()
        
        if terrain == 'stairs':
            return self._climb_stairs()
        elif terrain == 'slope':
            return self._climb_slope()
        elif terrain == 'rough':
            return self._navigate_rough_terrain()
        else:
            return self._navigate_flat()
    
    def _climb_stairs(self):
        """Handle stair climbing"""
        # Adjust hip height and step frequency
        self.navigator.set_gait(GaitType.CLIMB)
        # Slower, more deliberate steps
        return TaskResult.RUNNING
    
    def _climb_slope(self):
        """Handle slope"""
        angle = self.terrain_detector.get_slope_angle()
        
        # Adjust balance correction
        # Lean forward slightly
        return TaskResult.RUNNING
    
    def _navigate_rough_terrain(self):
        """Handle rough terrain"""
        # Shorter steps, slower speed
        return TaskResult.RUNNING
    
    def _navigate_flat(self):
        """Handle flat terrain"""
        # Normal walking
        return TaskResult.RUNNING
```

## Summary

Nav2 provides a complete navigation framework supporting diverse robot platforms. With proper configuration and customization, it enables autonomous navigation for everything from mobile robots to complex humanoids.

## Key Takeaways

- Nav2 is the standard ROS 2 navigation framework
- Global planning finds optimal paths; local planning handles real-time collision avoidance
- AMCL provides robust localization using particle filters
- Behavior trees enable complex navigation logic
- Humanoid-specific modifications enable bipedal locomotion
- Recovery behaviors help robots escape stuck situations
- Extensive configuration allows adaptation to any robot platform
- Simulation validation before real-world deployment is essential