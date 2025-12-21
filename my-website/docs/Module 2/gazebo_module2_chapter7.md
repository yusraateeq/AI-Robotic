# Chapter 7: ROS 2 Integration - Gazebo and Unity Communication

## Introduction

ROS 2 is the middleware that connects Gazebo simulation, Unity visualization, and user algorithms. This chapter covers integrating both Gazebo and Unity with ROS 2, enabling seamless communication between physics simulation, visualization, and control algorithms.

## ROS 2 Communication Architecture

### Complete System Architecture

```
┌────────────────────────────────────────────────────┐
│         User Control Algorithm (Python)            │
│              (Decision Making Node)                │
└──────────────┬──────────────────────────────────────┘
               │ ROS 2 Middleware (DDS)
    ┌──────────┴──────────────┬──────────────────┐
    │                         │                  │
┌───▼──────────────────┐ ┌────▼───────────────┐ ┌─▼─────────────────┐
│ Gazebo Simulator     │ │ Unity Visualization│ │ Monitoring Tools  │
│                      │ │                    │ │ (RVIZ, etc)      │
│ Publishers:          │ │ Subscribers:       │ │                   │
│ - /sensor/lidar      │ │ - /robot/state     │ │ Subscribers:      │
│ - /sensor/camera     │ │ - /sensor/data     │ │ - All topics      │
│ - /robot/state       │ │                    │ │                   │
│ - /sensor/imu        │ │ Publishers:        │ │ Publishers:       │
│                      │ │ - /cmd_vel         │ │ - /diagnostics    │
│ Subscribers:         │ │ - /joint_commands  │ │                   │
│ - /cmd_vel           │ │                    │ │                   │
│ - /joint_commands    │ │ Services:          │ │                   │
│                      │ │ - /reset_robot     │ │ Services:         │
│ Services:            │ │ - /spawn_entity    │ │ - /record_bag     │
│ - /spawn_entity      │ │                    │ │                   │
│ - /delete_entity     │ │                    │ │                   │
└──────────────────────┘ └────────────────────┘ └───────────────────┘
```

### Topic Organization Best Practices

```
Recommended Topic Structure:

/robot/[robot_name]/
├── state/
│   ├── joint_states      # Current joint positions/velocities
│   ├── base_state        # Position, velocity of base
│   └── battery           # Battery level
├── sensors/
│   ├── lidar/
│   │   └── points        # Point cloud from LiDAR
│   ├── camera/
│   │   ├── rgb/image     # RGB image
│   │   └── depth/image   # Depth image
│   └── imu/
│       └── data          # IMU measurements
├── commands/
│   ├── cmd_vel           # Velocity commands
│   ├── joint_commands    # Joint position targets
│   └── gripper           # Gripper commands
└── diagnostics/
    ├── health            # System health
    └── status            # Operational status
```

## Gazebo ROS 2 Integration

### Gazebo Plugins for ROS 2

Gazebo uses plugins to publish sensor data and subscribe to commands:

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <world name="ros2_integrated_world">
    
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>
    
    <!-- Robot model -->
    <model name="mobile_manipulator">
      
      <!-- Base link -->
      <link name="base_link">
        <inertial>
          <mass value="20"/>
          <inertia ixx="0.2" ixy="0" ixz="0"
                   iyy="0.2" iyz="0"
                   izz="0.2"/>
        </inertial>
      </link>
      
      <!-- LiDAR sensor with ROS 2 plugin -->
      <link name="lidar_link">
        <pose relative_to="base_link">0 0 0.2 0 0 0</pose>
      </link>
      
      <sensor name="lidar_sensor" type="ray">
        <pose relative_to="lidar_link">0 0 0 0 0 0</pose>
        <ray>
          <scan>
            <horizontal>
              <samples>720</samples>
              <min_angle>-3.14159</min_angle>
              <max_angle>3.14159</max_angle>
            </horizontal>
          </scan>
          <range>
            <min>0.1</min>
            <max>30</max>
          </range>
        </ray>
        <always_on>true</always_on>
        <update_rate>10</update_rate>
        
        <!-- ROS 2 Plugin -->
        <plugin name="gazebo_ros_ray_sensor"
                filename="libgazebo_ros_ray_sensor.so">
          <ros>
            <!-- Remapping for topic name -->
            <remapping>~/out:=/robot/sensors/lidar/scan</remapping>
          </ros>
          <frame_name>lidar_link</frame_name>
        </plugin>
      </sensor>
      
      <!-- Depth Camera with ROS 2 plugin -->
      <link name="camera_link">
        <pose relative_to="base_link">0.2 0 0.1 0 0 0</pose>
      </link>
      
      <sensor name="depth_camera" type="depth_camera">
        <camera>
          <horizontal_fov>1.047</horizontal_fov>
          <image>
            <width>640</width>
            <height>480</height>
          </image>
          <clip>
            <near>0.1</near>
            <far>10</far>
          </clip>
        </camera>
        <always_on>true</always_on>
        <update_rate>30</update_rate>
        
        <!-- ROS 2 Plugin -->
        <plugin name="gazebo_ros_camera_sensor"
                filename="libgazebo_ros_camera_sensor.so">
          <ros>
            <remapping>~/image_raw:=/robot/sensors/camera/rgb</remapping>
            <remapping>~/depth_image_raw:=/robot/sensors/camera/depth</remapping>
          </ros>
          <camera_name>depth_camera</camera_name>
        </plugin>
      </sensor>
      
      <!-- IMU with ROS 2 plugin -->
      <link name="imu_link"/>
      
      <sensor name="imu_sensor" type="imu">
        <!-- ROS 2 Plugin -->
        <plugin name="gazebo_ros_imu_sensor"
                filename="libgazebo_ros_imu_sensor.so">
          <ros>
            <remapping>~/out:=/robot/sensors/imu</remapping>
          </ros>
          <initial_orient_as_reference>false</initial_orient_as_reference>
        </plugin>
      </sensor>
      
    </model>
    
    <!-- Gazebo ROS 2 spawner plugin (world-level) -->
    <plugin name="gazebo_ros_state" 
            filename="libgazebo_ros_state.so"/>
    
  </world>
</sdf>
```

### ROS 2 Node for Gazebo Integration

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from gazebo_msgs.srv import SpawnEntity, DeleteEntity

class GazeboIntegrationNode(Node):
    """
    Node that integrates with Gazebo simulation
    Publishes commands, subscribes to sensor data
    """
    
    def __init__(self):
        super().__init__('gazebo_integration_node')
        
        # Publishers for commands to Gazebo
        self.cmd_vel_pub = self.create_publisher(
            Twist, '/robot/commands/cmd_vel', 10
        )
        
        self.joint_cmd_pub = self.create_publisher(
            Float64, '/robot/arm/joint_1/command', 10
        )
        
        # Subscribers for sensor data from Gazebo
        self.joint_states_sub = self.create_subscription(
            JointState, '/robot/state/joint_states',
            self.joint_states_callback, 10
        )
        
        self.lidar_sub = self.create_subscription(
            LaserScan, '/robot/sensors/lidar/scan',
            self.lidar_callback, 10
        )
        
        self.camera_sub = self.create_subscription(
            Image, '/robot/sensors/camera/rgb',
            self.camera_callback, 10
        )
        
        self.imu_sub = self.create_subscription(
            Imu, '/robot/sensors/imu',
            self.imu_callback, 10
        )
        
        # Gazebo service clients
        self.spawn_client = self.create_client(
            SpawnEntity, '/spawn_entity'
        )
        
        self.get_logger().info('Gazebo Integration Node started')
    
    def joint_states_callback(self, msg):
        """Receive joint states from Gazebo"""
        self.get_logger().debug(f'Joint states: {msg.name}')
    
    def lidar_callback(self, msg):
        """Receive LiDAR data from Gazebo"""
        num_readings = len(msg.ranges)
        self.get_logger().debug(f'LiDAR readings: {num_readings}')
    
    def camera_callback(self, msg):
        """Receive camera data from Gazebo"""
        self.get_logger().debug(f'Camera: {msg.width}x{msg.height}')
    
    def imu_callback(self, msg):
        """Receive IMU data from Gazebo"""
        accel = msg.linear_acceleration
        self.get_logger().debug(
            f'Acceleration: ({accel.x:.2f}, {accel.y:.2f}, {accel.z:.2f})'
        )
    
    def send_velocity_command(self, linear_x, angular_z):
        """Send velocity command to Gazebo"""
        cmd = Twist()
        cmd.linear.x = linear_x
        cmd.angular.z = angular_z
        self.cmd_vel_pub.publish(cmd)
    
    def spawn_object(self, object_name, sdf_model):
        """Spawn object in Gazebo"""
        request = SpawnEntity.Request()
        request.name = object_name
        request.xml = sdf_model
        
        future = self.spawn_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        return future.result()

def main(args=None):
    rclpy.init(args=args)
    node = GazeboIntegrationNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Unity ROS 2 Integration

### Setting Up ROS 2 Communication in Unity

```csharp
using Unity.Robotics.ROSClient;
using RosMessageTypes.Geometry;
using RosMessageTypes.Sensor;
using RosMessageTypes.Std;

public class UnityROS2Integration : MonoBehaviour
{
    // ROS 2 connection
    private ROSConnection ros;
    
    // Publishers
    private uint cmdVelPubID;
    private uint jointCmdPubID;
    
    // Subscribers
    private string jointStatesTopic = "/robot/state/joint_states";
    private string lidarTopic = "/robot/sensors/lidar/scan";
    private string cameraTopic = "/robot/sensors/camera/rgb";
    
    void Start()
    {
        // Initialize ROS connection
        ros = ROSConnection.GetOrCreateInstance();
        
        // Register publishers
        cmdVelPubID = ros.AdvertisePublisher<TwistMsg>(
            "/robot/commands/cmd_vel"
        );
        
        jointCmdPubID = ros.AdvertisePublisher<Float64Msg>(
            "/robot/arm/joint_1/command"
        );
        
        // Register subscribers
        ros.Subscribe<JointStateMsg>(
            jointStatesTopic, 
            JointStatesCallback
        );
        
        ros.Subscribe<LaserScanMsg>(
            lidarTopic,
            LidarCallback
        );
        
        ros.Subscribe<ImageMsg>(
            cameraTopic,
            CameraCallback
        );
        
        Debug.Log("Unity ROS 2 Integration initialized");
    }
    
    void Update()
    {
        // Example: Send velocity command based on keyboard input
        if (Input.GetKey(KeyCode.W))
        {
            PublishVelocity(1f, 0f);  // Move forward
        }
        if (Input.GetKey(KeyCode.S))
        {
            PublishVelocity(-1f, 0f);  // Move backward
        }
        if (Input.GetKey(KeyCode.A))
        {
            PublishVelocity(0f, 1f);  // Turn left
        }
        if (Input.GetKey(KeyCode.D))
        {
            PublishVelocity(0f, -1f);  // Turn right
        }
    }
    
    void PublishVelocity(float linearX, float angularZ)
    {
        TwistMsg cmd = new TwistMsg();
        cmd.linear.x = linearX;
        cmd.angular.z = angularZ;
        
        ros.Publish(cmdVelPubID, cmd);
    }
    
    void JointStatesCallback(JointStateMsg msg)
    {
        // Update UI with joint positions
        for (int i = 0; i < msg.name.Length; i++)
        {
            float position = (float)msg.position[i];
            Debug.Log($"{msg.name[i]}: {position}");
        }
    }
    
    void LidarCallback(LaserScanMsg msg)
    {
        // Process LiDAR data
        float[] ranges = msg.ranges;
        Debug.Log($"LiDAR points: {ranges.Length}");
    }
    
    void CameraCallback(ImageMsg msg)
    {
        // Process camera image
        Debug.Log($"Camera: {msg.width}x{msg.height}");
    }
}
```

### Full Integration Example: Dual Simulation

```python
import rclpy
from rclpy.node import Node
import threading
import time

class DualSimulationController(Node):
    """
    Control both Gazebo (physics) and Unity (visualization)
    simultaneously for comprehensive testing
    """
    
    def __init__(self):
        super().__init__('dual_simulation_controller')
        
        # Gazebo integration
        self.gazebo_cmd_vel = self.create_publisher(
            Twist, '/gazebo_robot/cmd_vel', 10
        )
        
        # Unity integration
        self.unity_cmd_vel = self.create_publisher(
            Twist, '/unity_robot/cmd_vel', 10
        )
        
        # Sensor subscribers
        self.gazebo_sensors = {}
        self.unity_sensors = {}
        
        # Subscribe to both simulations
        self.gazebo_joint_sub = self.create_subscription(
            JointState, '/gazebo_robot/state/joint_states',
            self.gazebo_joint_callback, 10
        )
        
        self.unity_joint_sub = self.create_subscription(
            JointState, '/unity_robot/state/joint_states',
            self.unity_joint_callback, 10
        )
        
        # Validation timer
        self.validation_timer = self.create_timer(
            1.0, self.validate_simulations
        )
        
        self.get_logger().info('Dual Simulation Controller initialized')
    
    def gazebo_joint_callback(self, msg):
        """Receive joint states from Gazebo"""
        self.gazebo_sensors['joint_states'] = msg
    
    def unity_joint_callback(self, msg):
        """Receive joint states from Unity"""
        self.unity_sensors['joint_states'] = msg
    
    def validate_simulations(self):
        """
        Compare outputs from both simulations
        Ensures consistency between physics and visualization
        """
        if 'joint_states' not in self.gazebo_sensors:
            return
        if 'joint_states' not in self.unity_sensors:
            return
        
        gazebo_js = self.gazebo_sensors['joint_states']
        unity_js = self.unity_sensors['joint_states']
        
        # Compare joint positions
        for i, (gz_pos, unity_pos) in enumerate(
            zip(gazebo_js.position, unity_js.position)
        ):
            diff = abs(gz_pos - unity_pos)
            if diff > 0.1:  # 10% tolerance
                self.get_logger().warn(
                    f'Mismatch in joint {i}: '
                    f'Gazebo={gz_pos:.2f}, Unity={unity_pos:.2f}'
                )
    
    def send_synchronized_command(self, linear_x, angular_z):
        """
        Send same command to both simulations
        For synchronized operation
        """
        cmd = Twist()
        cmd.linear.x = linear_x
        cmd.angular.z = angular_z
        
        # Send to both
        self.gazebo_cmd_vel.publish(cmd)
        self.unity_cmd_vel.publish(cmd)
        
        self.get_logger().debug(
            f'Sent synchronized command: '
            f'linear={linear_x}, angular={angular_z}'
        )

def main(args=None):
    rclpy.init(args=args)
    controller = DualSimulationController()
    rclpy.spin(controller)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Bridging Gazebo and Unity

### Synchronized Dual Simulation

```python
import rclpy
from rclpy.node import Node
from threading import Lock
import json

class SimulationBridge(Node):
    """
    Bridge between Gazebo (physics truth) and Unity (visualization)
    Synchronizes state between both simulations
    """
    
    def __init__(self):
        super().__init__('simulation_bridge')
        
        self.state_lock = Lock()
        self.current_state = {}
        
        # Subscribe to Gazebo ground truth
        self.gazebo_state_sub = self.create_subscription(
            JointState, '/gazebo_robot/state',
            self.on_gazebo_state, 10
        )
        
        # Publish to Unity
        self.unity_state_pub = self.create_publisher(
            JointState, '/unity_robot/state', 10
        )
        
        # Publish statistics
        self.stats_pub = self.create_publisher(
            String, '/simulation/stats', 10
        )
        
        # Bridge statistics
        self.message_count = 0
        self.last_update_time = self.get_clock().now()
        
        self.get_logger().info('Simulation Bridge initialized')
    
    def on_gazebo_state(self, msg):
        """Receive state from Gazebo ground truth"""
        with self.state_lock:
            self.current_state = msg
            
            # Forward to Unity for visualization
            self.unity_state_pub.publish(msg)
            
            # Track statistics
            self.message_count += 1
            
            if self.message_count % 100 == 0:
                current_time = self.get_clock().now()
                elapsed = (current_time - self.last_update_time).nanoseconds / 1e9
                rate = 100 / elapsed
                
                stats = {
                    'messages_bridged': self.message_count,
                    'bridge_rate_hz': rate,
                    'gazebo_state_joints': len(msg.name)
                }
                
                self.get_logger().info(f'Bridge stats: {stats}')
                self.last_update_time = current_time
```

## Best Practices for Multi-Simulation Workflows

### Version Control for Simulation Assets

```python
# simulation_config.yaml
gazebo:
  world: "robot_lab.world"
  physics_engine: "ode"
  max_step_size: 0.001
  real_time_factor: 1.0
  
unity:
  scene: "SimulationScene.unity"
  render_scale: 1.0
  target_fps: 60
  
robot:
  urdf: "humanoid_v2.urdf"
  spawn_position: [0, 0, 0]
  initial_state: "standing"
  
sensors:
  lidar:
    enabled: true
    noise: 0.01
  camera:
    enabled: true
    resolution: [640, 480]
  imu:
    enabled: true
    noise: 0.02
```

### Automated Testing Framework

```python
import unittest
import rclpy
from rclpy.node import Node

class SimulationValidationTests(unittest.TestCase):
    """
    Automated tests to validate simulation consistency
    """
    
    @classmethod
    def setUpClass(cls):
        rclpy.init()
        cls.node = Node('test_node')
    
    def test_gravity_effect(self):
        """Test that gravity is applied correctly"""
        # Drop an object and measure fall time
        # Compare with theoretical prediction
        pass
    
    def test_sensor_accuracy(self):
        """Test sensor simulation accuracy"""
        # Place known object in field of view
        # Verify sensor detects it correctly
        pass
    
    def test_gazebo_unity_sync(self):
        """Test synchronization between Gazebo and Unity"""
        # Send command to both
        # Verify states match within tolerance
        pass
    
    def test_network_latency(self):
        """Test network latency simulation"""
        # Measure round-trip time
        # Verify latency within expected bounds
        pass

if __name__ == '__main__':
    unittest.main()
```

## Summary

ROS 2 integration is the critical component that connects Gazebo's physics simulation, Unity's visualization, and user algorithms. Proper integration enables seamless development, testing, and validation workflows.

## Key Takeaways

- Gazebo plugins enable ROS 2 topic-based communication for all sensors
- Unity's ROS 2 client library mirrors Gazebo integration capabilities
- Topics enable real-time data streaming between systems
- Services provide synchronous request-reply communication
- Dual simulation (Gazebo + Unity) validates consistency
- Version control of simulation configurations ensures reproducibility
- Automated testing validates simulation accuracy
- Proper architecture scales to complex multi-robot systems