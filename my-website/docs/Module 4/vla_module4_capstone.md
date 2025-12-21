# Chapter 4: Capstone Project - The Autonomous Humanoid

## Project Overview

This capstone project integrates everything learned throughout the course: ROS 2 middleware, physics simulation, AI perception, navigation, and vision-language models. You will build a complete system where a simulated humanoid robot receives voice commands, understands the task, plans the execution, navigates an environment, perceives objects, and manipulates them.

## Project Architecture

### Complete System Integration

```
User Voice Command
│ "Pick up the red cube and place it on the table"
│
├─────────────────────────────────────────────┐
│                                             │
▼                                             │
Voice-to-Text Node (Whisper)             Command Parser
│ Audio → Transcription                  Entity Extraction
│                                             │
└─────────────────────────────────────────────┘
                    │
                    ▼
         Planning Node (LLM)
         Goal → Action Sequence
         ├─ Navigate to object location
         ├─ Identify red cube with vision
         ├─ Compute grasp pose
         ├─ Execute grasp
         ├─ Navigate to table
         └─ Place on table
                    │
                    ▼
         Navigation Stack (Nav2)
         Path planning & obstacle avoidance
                    │
                    ▼
         Perception Pipeline
         ├─ Camera feed analysis
         ├─ Object detection
         ├─ Pose estimation
         └─ Spatial reasoning
                    │
                    ▼
         Motion Execution
         ├─ Base movement commands
         ├─ Arm control
         ├─ Gripper manipulation
         └─ Feedback & monitoring
                    │
                    ▼
         Isaac Sim / Real Robot Hardware
         ├─ Physics simulation
         ├─ Sensor publishing
         └─ Command execution
```

## Project Phases

### Phase 1: Environment Setup (Week 1)

#### 1.1 Simulation Environment

```python
"""
Setup Isaac Sim environment for capstone
"""

from isaacsim import SimulationApp
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
import os

class CapstoneSimulationSetup:
    """Initialize capstone project environment"""
    
    def __init__(self):
        self.simulation_app = SimulationApp({"headless": False})
        self.world = World(stage_units_in_meters=1.0)
        
        # Configure physics
        self._configure_physics()
        
        # Setup environment
        self._load_robot()
        self._setup_workspace()
        self._place_objects()
    
    def _configure_physics(self):
        """Configure physics engine"""
        physics_context = self.world.get_physics_context()
        physics_context.enable_gpu_dynamics(True)
        physics_context.set_gravity([0, 0, -9.81])
        self.world.set_simulation_dt(0.01)  # 100 Hz
    
    def _load_robot(self):
        """Load humanoid robot"""
        # Load from local URDF or Omniverse models
        robot_path = "/World/H1_Robot"
        
        # Add robot to stage
        add_reference_to_stage(
            usd_path="/Isaac/Robots/Humanoids/H1/h1.usd",
            prim_path=robot_path
        )
        
        self.robot = self.world.scene.add_robot(robot_path)
    
    def _setup_workspace(self):
        """Create manipulation workspace"""
        # Add table
        table_path = "/World/WorkTable"
        add_reference_to_stage(
            usd_path="/Isaac/Props/Table/Table.usd",
            prim_path=table_path
        )
        
        # Add objects to manipulate
        self._add_cube("red_cube", [0.5, 0.3, 0.8], color=[1, 0, 0])
        self._add_cube("blue_cube", [0.6, 0.2, 0.8], color=[0, 0, 1])
        self._add_cylinder("green_cylinder", [0.4, 0.4, 0.8], color=[0, 1, 0])
    
    def _add_cube(self, name: str, position: list, color: list):
        """Add cube to scene"""
        from pxr import UsdGeom, Gf, UsdPhysics
        
        stage = self.world.stage
        cube_path = f"/World/{name}"
        
        # Create cube
        cube = UsdGeom.Cube.Define(stage, cube_path)
        cube.GetSizeAttr().Set(0.05)
        
        # Set position
        xform_attr = stage.GetPrimAtPath(cube_path).GetAttribute("xformOp:translate")
        xform_attr.Set(Gf.Vec3f(*position))
        
        # Add physics
        UsdPhysics.CollisionAPI.Apply(stage.GetPrimAtPath(cube_path))
        UsdPhysics.RigidBodyAPI.Apply(stage.GetPrimAtPath(cube_path))
        
        # Set color
        self._apply_material(cube_path, color)
    
    def _add_cylinder(self, name: str, position: list, color: list):
        """Add cylinder to scene"""
        from pxr import UsdGeom, Gf
        
        stage = self.world.stage
        cyl_path = f"/World/{name}"
        
        cyl = UsdGeom.Cylinder.Define(stage, cyl_path)
        cyl.GetRadiusAttr().Set(0.025)
        cyl.GetHeightAttr().Set(0.05)
        
        xform_attr = stage.GetPrimAtPath(cyl_path).GetAttribute("xformOp:translate")
        xform_attr.Set(Gf.Vec3f(*position))
        
        self._apply_material(cyl_path, color)
    
    def _apply_material(self, prim_path: str, color: list):
        """Apply color material"""
        # Implementation for PBR material
        pass
    
    def _place_objects(self):
        """Place objects for manipulation task"""
        # Objects are placed by _setup_workspace
        pass
    
    def step_simulation(self):
        """Step simulation"""
        self.world.step(render=True)
    
    def reset(self):
        """Reset simulation"""
        self.world.reset()
```

#### 1.2 ROS 2 Workspace Setup

```bash
#!/bin/bash
# Setup ROS 2 workspace for capstone

# Create workspace
mkdir -p ~/capstone_ws/src
cd ~/capstone_ws

# Clone required packages
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_perception.git
git clone https://github.com/ros-navigation/navigation2.git
git clone https://github.com/ros2/object_recognition_msgs.git

# Install dependencies
rosdep install --from-paths src --ignore-src -y

# Build workspace
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

# Source setup
source install/setup.bash
```

### Phase 2: Voice and Planning (Week 2)

#### 2.1 Voice Command System

```python
"""
Capstone voice command handler
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from capstone_interfaces.msg import TaskGoal

class CapstoneVoiceHandler(Node):
    """Handle voice commands for capstone"""
    
    def __init__(self):
        super().__init__('capstone_voice_handler')
        
        # Initialize voice system
        self.voice_capture = RealtimeAudioCapture()
        self.asr = WhisperASR(model_size="base")
        self.parser = CommandParser()
        
        # ROS 2 publishers
        self.task_goal_pub = self.create_publisher(
            TaskGoal, '/capstone/task_goal', 10
        )
        
        self.status_pub = self.create_publisher(
            String, '/capstone/status', 10
        )
        
        # Start listening
        self.timer = self.create_timer(1.0, self.listen_and_process)
    
    def listen_and_process(self):
        """Listen for voice commands"""
        try:
            # Capture audio
            audio = self.voice_capture.record_until_silence(
                silence_duration=1.5
            )
            
            # Transcribe
            result = self.asr.transcribe_audio_array(audio)
            
            if result['confidence'] < 0.7:
                self.get_logger().warn('Low confidence transcription')
                return
            
            self.get_logger().info(f"Transcribed: {result['text']}")
            
            # Parse command
            parsed = self.parser.parse(result['text'], use_llm=True)
            
            # Create task goal
            task_goal = TaskGoal()
            task_goal.goal_text = result['text']
            task_goal.intent = parsed.intent.value
            
            # Publish
            self.task_goal_pub.publish(task_goal)
            
        except Exception as e:
            self.get_logger().error(f"Error: {e}")
```

#### 2.2 Planning Node

```python
"""
Planning node for capstone
"""

class CapstoneTaskPlanner(Node):
    """Plan tasks using LLM"""
    
    def __init__(self):
        super().__init__('capstone_task_planner')
        
        self.planner = ChainOfThoughtPlanner(model_name="gpt-4")
        
        # Subscribers
        self.task_sub = self.create_subscription(
            TaskGoal, '/capstone/task_goal',
            self.on_task_goal, 10
        )
        
        # Publishers
        self.plan_pub = self.create_publisher(
            String, '/capstone/action_plan', 10
        )
    
    def on_task_goal(self, msg):
        """Receive task goal"""
        goal_text = msg.goal_text
        
        self.get_logger().info(f"Planning task: {goal_text}")
        
        # Get scene description
        scene_desc = self._get_scene_description()
        
        # Generate plan
        plan = self.planner.plan(
            goal=goal_text,
            scene_description=scene_desc,
            constraints=self._get_constraints()
        )
        
        # Publish plan
        plan_json = self._plan_to_json(plan)
        self.plan_pub.publish(String(data=plan_json))
    
    def _get_scene_description(self) -> str:
        """Describe current scene"""
        return """
        Scene: Lab environment
        - Red cube at position (0.5, 0.3, 0.8)
        - Blue cube at position (0.6, 0.2, 0.8)
        - Green cylinder at position (0.4, 0.4, 0.8)
        - Table at (0.5, 0.5, 0.4)
        - Robot at origin, facing +X direction
        """
    
    def _get_constraints(self) -> List[str]:
        return [
            "Avoid collisions with environment",
            "Respect robot joint limits",
            "Maintain balance (humanoid)",
            "Maximum task duration: 10 minutes"
        ]
```

### Phase 3: Perception and Navigation (Week 3)

#### 3.1 Object Detection and Localization

```python
"""
Perception module for capstone
"""

class CapstonePerception(Node):
    """Perception pipeline for object detection"""
    
    def __init__(self):
        super().__init__('capstone_perception')
        
        # Load detection model
        self.detector = ObjectDetectionModel()
        self.depth_estimator = DepthEstimator()
        
        # Subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/rgb/image_raw',
            self.on_image, 10
        )
        
        self.depth_sub = self.create_subscription(
            Image, '/camera/depth/image_raw',
            self.on_depth, 10
        )
        
        # Publishers
        self.detections_pub = self.create_publisher(
            DetectionArray, '/capstone/detections', 10
        )
        
        self.object_poses_pub = self.create_publisher(
            String, '/capstone/object_poses', 10
        )
    
    def on_image(self, msg):
        """Process incoming image"""
        frame = self.bridge.imgmsg_to_cv2(msg)
        
        # Run detection
        detections = self.detector.detect(frame)
        
        # Publish detections
        self.publish_detections(detections)
    
    def on_depth(self, msg):
        """Process depth image"""
        depth = self.bridge.imgmsg_to_cv2(msg)
        
        # Convert pixel coordinates to 3D positions
        if hasattr(self, 'latest_detections'):
            object_poses = self.compute_3d_poses(
                self.latest_detections, depth
            )
            
            # Publish poses
            self.object_poses_pub.publish(
                String(data=json.dumps(object_poses))
            )
    
    def compute_3d_poses(self, detections, depth):
        """Compute 3D poses from detections and depth"""
        poses = {}
        
        for det in detections:
            # Get center pixel
            x_pixel = (det.bbox.x1 + det.bbox.x2) // 2
            y_pixel = (det.bbox.y1 + det.bbox.y2) // 2
            
            # Get depth
            z_depth = depth[y_pixel, x_pixel]
            
            # Convert to 3D
            fx = 554.3  # Camera focal length
            fy = 554.3
            cx = 320
            cy = 240
            
            x_3d = (x_pixel - cx) * z_depth / fx
            y_3d = (y_pixel - cy) * z_depth / fy
            z_3d = z_depth
            
            poses[det.class_name] = {
                'position': [x_3d, y_3d, z_3d],
                'confidence': det.confidence
            }
        
        return poses
```

#### 3.2 Navigation Node

```python
"""
Navigation for humanoid in capstone
"""

class CapstoneNavigation(Node):
    """Navigate humanoid to locations"""
    
    def __init__(self):
        super().__init__('capstone_navigation')
        
        # Initialize Nav2 client
        self.navigator = BasicNavigator()
        
        # Subscribers
        self.nav_goal_sub = self.create_subscription(
            PoseStamped, '/capstone/nav_goal',
            self.on_nav_goal, 10
        )
        
        # Publishers
        self.path_pub = self.create_publisher(
            Path, '/capstone/planned_path', 10
        )
    
    def on_nav_goal(self, msg):
        """Receive navigation goal"""
        target_pose = msg
        
        self.get_logger().info(
            f"Navigating to ({target_pose.pose.position.x:.2f}, "
            f"{target_pose.pose.position.y:.2f})"
        )
        
        # Plan path
        self.navigator.goToPose(target_pose)
        
        # Monitor
        while not self.navigator.isNavComplete():
            feedback = self.navigator.getFeedback()
            if feedback:
                self.get_logger().debug(
                    f"Distance remaining: "
                    f"{feedback.distance_remaining:.2f}m"
                )
```

### Phase 4: Task Execution (Week 4)

#### 4.1 Integrated Task Executor

```python
"""
Main task execution node
"""

class CapstoneTaskExecutor(Node):
    """Execute complete tasks end-to-end"""
    
    def __init__(self):
        super().__init__('capstone_task_executor')
        
        # Task state machine
        self.state = 'idle'
        self.current_plan = None
        self.current_step = 0
        
        # Action client for arm movement
        self._action_clients = {}
        
        # Subscribers
        self.plan_sub = self.create_subscription(
            String, '/capstone/action_plan',
            self.on_plan, 10
        )
        
        self.status_sub = self.create_subscription(
            String, '/capstone/action_status',
            self.on_action_status, 10
        )
        
        # Publishers
        self.nav_goal_pub = self.create_publisher(
            PoseStamped, '/capstone/nav_goal', 10
        )
        
        self.arm_command_pub = self.create_publisher(
            JointTrajectory, '/capstone/arm_command', 10
        )
        
        # Execution timer
        self.exec_timer = self.create_timer(0.1, self.execute_step)
    
    def on_plan(self, msg):
        """Receive new plan"""
        plan_json = msg.data
        self.current_plan = json.loads(plan_json)
        self.current_step = 0
        self.state = 'executing'
        
        self.get_logger().info(
            f"Executing plan with {len(self.current_plan['steps'])} steps"
        )
    
    def execute_step(self):
        """Execute current step"""
        if self.state != 'executing':
            return
        
        if self.current_step >= len(self.current_plan['steps']):
            self.state = 'complete'
            self.get_logger().info("Task complete!")
            return
        
        step = self.current_plan['steps'][self.current_step]
        action = step['action']
        params = step['parameters']
        
        self.get_logger().info(f"Executing step {self.current_step}: {action}")
        
        try:
            if action == 'navigate_to':
                self.execute_navigation(params)
            elif action == 'identify_object':
                self.execute_identification(params)
            elif action == 'grasp':
                self.execute_grasp(params)
            elif action == 'place':
                self.execute_place(params)
            elif action == 'move_arm_to':
                self.execute_arm_move(params)
            
            # Move to next step
            self.current_step += 1
            
        except Exception as e:
            self.get_logger().error(f"Step failed: {e}")
            self.state = 'error'
    
    def execute_navigation(self, params):
        """Navigate to location"""
        target = params.get('location', 'table')
        
        # Convert location name to coordinates
        location_map = {
            'cube_location': [0.5, 0.3],
            'table': [0.5, 0.5],
            'start': [0, 0]
        }
        
        x, y = location_map.get(target, [0, 0])
        
        # Create goal
        goal = PoseStamped()
        goal.header.frame_id = 'map'
        goal.pose.position.x = float(x)
        goal.pose.position.y = float(y)
        goal.pose.position.z = 0.0
        
        # Publish
        self.nav_goal_pub.publish(goal)
    
    def execute_identification(self, params):
        """Identify object"""
        object_class = params.get('object_class', 'cube')
        self.get_logger().info(f"Identifying {object_class}")
        
        # This triggers perception pipeline
        # Results published to /capstone/object_poses
    
    def execute_grasp(self, params):
        """Grasp object"""
        object_name = params.get('object_name', 'red_cube')
        
        # Get object position from perception
        # Compute grasp pose
        # Execute arm movement to grasp
        # Close gripper
        
        self.get_logger().info(f"Grasping {object_name}")
    
    def execute_place(self, params):
        """Place object"""
        target = params.get('target', 'table')
        
        # Move to placement position
        # Open gripper
        # Retract
        
        self.get_logger().info(f"Placing on {target}")
    
    def execute_arm_move(self, params):
        """Move arm to position"""
        x = float(params.get('x', 0.5))
        y = float(params.get('y', 0.3))
        z = float(params.get('z', 0.8))
        
        self.get_logger().info(f"Moving arm to ({x}, {y}, {z})")
        
        # Compute IK
        # Execute trajectory
    
    def on_action_status(self, msg):
        """Receive action status"""
        status = msg.data
        
        if 'success' in status.lower():
            self.get_logger().info("Action completed successfully")
        elif 'failed' in status.lower():
            self.get_logger().error("Action failed")
            self.state = 'error'
```

### Phase 5: Testing and Validation (Week 5)

#### 5.1 Test Suite

```python
"""
Unit and integration tests for capstone
"""

import unittest

class TestCapstoneSystem(unittest.TestCase):
    """Test complete capstone system"""
    
    def setUp(self):
        """Setup test environment"""
        self.setup = CapstoneSimulationSetup()
    
    def test_voice_to_text(self):
        """Test voice transcription"""
        # Test with audio samples
        pass
    
    def test_command_parsing(self):
        """Test command parsing"""
        parser = CommandParser()
        
        # Test various command formats
        commands = [
            "Pick up the red cube",
            "Place the cube on the table",
            "Navigate to the corner",
            "Identify all objects"
        ]
        
        for cmd in commands:
            parsed = parser.parse(cmd)
            self.assertIsNotNone(parsed.intent)
    
    def test_planning(self):
        """Test task planning"""
        planner = FewShotPlanner()
        
        plan = planner.plan("Pick up the red cube")
        
        self.assertGreater(len(plan.steps), 0)
        self.assertIsNotNone(plan.steps[0].action)
    
    def test_navigation(self):
        """Test navigation in simulation"""
        navigator = CapstoneNavigation()
        
        # Test navigation to multiple points
        points = [[0.5, 0.3], [0.6, 0.4], [0.5, 0.5]]
        
        for point in points:
            goal = PoseStamped()
            goal.pose.position.x = point[0]
            goal.pose.position.y = point[1]
            
            # Navigate
            navigator.on_nav_goal(goal)
    
    def test_object_detection(self):
        """Test object detection"""
        perception = CapstonePerception()
        
        # Capture frame
        # Run detection
        # Verify objects detected
        pass
    
    def test_end_to_end(self):
        """Test complete pipeline"""
        # Simulate voice command
        # Process through entire system
        # Verify task completion
        pass

if __name__ == '__main__':
    unittest.main()
```

## Evaluation Criteria

### Success Metrics

```
Functionality:
✓ Voice command recognition (>90% accuracy)
✓ Intent parsing (>85% accuracy)
✓ Task planning generates valid sequences
✓ Navigation completes without collisions
✓ Object detection identifies all objects
✓ Grasp execution succeeds >80% of time
✓ Complete task execution end-to-end

Robustness:
✓ Handle noisy speech input
✓ Graceful degradation on failures
✓ Recovery from perception errors
✓ Timeout handling

Performance:
✓ Voice processing: <2 seconds
✓ Planning: <5 seconds
✓ Navigation: reaches goal within time limit
✓ Object detection: >15 FPS
✓ Overall task: <10 minutes

Code Quality:
✓ Well-documented code
✓ Modular architecture
✓ Comprehensive error handling
✓ Unit tests for critical components
```

## Demonstration Script

```bash
#!/bin/bash
# Capstone demo script

echo "=== Autonomous Humanoid Capstone Project ==="
echo ""

# Start simulation
echo "Starting Isaac Sim..."
python3 simulation_setup.py &
ISAAC_PID=$!

sleep 5

# Start ROS 2 nodes
echo "Starting ROS 2 core..."
ros2 daemon start

echo "Starting perception node..."
ros2 run capstone_package perception_node &

echo "Starting planning node..."
ros2 run capstone_package planning_node &

echo "Starting navigation node..."
ros2 run capstone_package navigation_node &

echo "Starting task executor..."
ros2 run capstone_package task_executor_node &

echo "Starting voice handler..."
ros2 run capstone_package voice_handler_node &

sleep 3

echo ""
echo "System ready! Say a voice command like:"
echo "  'Pick up the red cube and place it on the table'"
echo ""

# Keep running
wait
```

## Summary and Learning Outcomes

By completing this capstone project, you will have:

1. **Integrated all course concepts** into a cohesive system
2. **Built real-world robotics applications** combining AI and robotics
3. **Solved multi-modal problem spaces** (voice → planning → execution)
4. **Debugged complex distributed systems** using ROS 2
5. **Deployed end-to-end AI pipelines** on simulated hardware
6. **Demonstrated mastery** of robotics fundamentals and advanced AI

## Next Steps

After completing this capstone:

1. **Deploy to Real Hardware**
   - Use same code on physical robot
   - Handle sim-to-real transfer

2. **Expand Capabilities**
   - Add more complex tasks
   - Support multiple robots
   - Implement learning from experience

3. **Advanced Topics**
   - Reinforcement learning for optimization
   - Hierarchical task learning
   - Multi-robot coordination
   - Safety-critical verification

## Key Takeaways

- Vision-Language-Action models represent the future of robotics
- Complete systems require integration of multiple AI techniques
- ROS 2 provides the glue that makes everything work together
- Simulation is essential for safe algorithm development
- Real-world deployment requires careful validation
- Continuous learning and adaptation improve robot performance