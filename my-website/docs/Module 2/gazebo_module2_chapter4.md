# Chapter 4: Simulating Sensors - LiDAR, Depth Cameras, and IMUs

## Introduction

Sensors are the robot's perception of the world. Gazebo provides sophisticated sensor simulation that generates realistic data for testing perception algorithms. This chapter covers simulating three critical sensor types: LiDAR, depth cameras, and IMUs.

## Sensor Simulation in Gazebo

### How Sensor Simulation Works

```
Physical Robot Sensor
├── Optical/Mechanical Setup
├── Electronics
├── Signal Processing
├── Calibration
└── Output (raw data)

Gazebo Simulated Sensor
├── Geometric Ray-casting
├── Physics-based Calculation
├── Noise Injection
├── ROS 2 Interface
└── Output (simulated data)
```

### Sensor Plugin Architecture

```xml
<gazebo reference="sensor_link">
  <sensor type="[camera|lidar|imu|...]" name="sensor_name">
    <always_on>true</always_on>
    <update_rate>30</update_rate>
    <visualize>true</visualize>
    
    <!-- Sensor-specific configuration -->
    <[plugin_config]>
      <!-- Parameters -->
    </[plugin_config]>
    
  </sensor>
</gazebo>
```

## LiDAR (Light Detection and Ranging)

### Understanding LiDAR

LiDAR measures distances to objects by bouncing light (usually infrared) and measuring return time:

```
LiDAR Scanning Pattern:
   
    Scene: Robot in hallway with obstacles
    
    ╔════════════════════════════════════╗
    ║                                    ║
    ║         Wall                       ║
    ║    ┌──────────┐                    ║
    ║    │          │                    ║
    ║    │ Obstacle │                    ║
    ║    └──────────┘                    ║
    ║                                    ║
    ║         ▲                          ║
    ║         │ Robot with LiDAR         ║
    ║      ╱╱╱╱╱╱╱                      ║
    ║     ╱ Range ╱ 5m                  ║
    ║    ╱ Beams ╱                      ║
    ║   ╱        ╱                      ║
    ║                                    ║
    ╚════════════════════════════════════╝
    
    Output: Array of distance measurements
    [4.2, 4.1, 3.8, 2.1, 1.9, 2.0, 3.5, 4.0, ...]
```

### LiDAR Types

#### 2D LiDAR (Planar Scanner)
Single horizontal plane scanning:

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <model name="robot_with_lidar2d" static="false">
    
    <!-- Robot body -->
    <link name="base_link">
      <inertial>
        <mass value="10"/>
        <inertia ixx="0.1" ixy="0" ixz="0"
                 iyy="0.1" iyz="0"
                 izz="0.1"/>
      </inertial>
      <visual>
        <geometry>
          <cylinder radius="0.2" length="0.1"/>
        </geometry>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="0.2" length="0.1"/>
        </geometry>
      </collision>
    </link>
    
    <!-- LiDAR mount -->
    <link name="lidar2d_link">
      <pose relative_to="base_link">0 0 0.15 0 0 0</pose>
      <visual>
        <geometry>
          <cylinder radius="0.05" length="0.04"/>
        </geometry>
        <material>
          <ambient>0.5 0.5 0.5 1</ambient>
        </material>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="0.05" length="0.04"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="0.5"/>
        <inertia ixx="0.001" ixy="0" ixz="0"
                 iyy="0.001" iyz="0"
                 izz="0.001"/>
      </inertial>
    </link>
    
    <joint name="lidar2d_joint" type="fixed">
      <parent>base_link</parent>
      <child>lidar2d_link</child>
    </joint>
    
  </model>
</sdf>

<!-- Gazebo plugin for 2D LiDAR -->
<gazebo reference="lidar2d_link">
  <sensor type="ray" name="lidar2d">
    <always_on>true</always_on>
    <update_rate>10</update_rate>
    <visualize>true</visualize>
    
    <ray>
      <!-- Angular resolution -->
      <scan>
        <horizontal>
          <samples>720</samples>        <!-- 0.5° resolution -->
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>  <!-- -180° -->
          <max_angle>3.14159</max_angle>   <!-- +180° -->
        </horizontal>
      </scan>
      
      <!-- Range parameters -->
      <range>
        <min>0.1</min>                  <!-- 10 cm minimum -->
        <max>30</max>                   <!-- 30 m maximum -->
        <resolution>0.01</resolution>   <!-- 1 cm resolution -->
      </range>
      
      <!-- Noise -->
      <noise>
        <type>gaussian</type>
        <mean>0</mean>
        <stddev>0.01</stddev>
      </noise>
    </ray>
    
    <!-- ROS 2 plugin -->
    <plugin name="gazebo_ros_ray_sensor" 
            filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <remapping>~/out:=/lidar/scan</remapping>
      </ros>
    </plugin>
  </sensor>
</gazebo>
```

#### 3D LiDAR (Point Cloud Scanner)
360° horizontal scanning with vertical layers:

```xml
<gazebo reference="lidar3d_link">
  <sensor type="gpu_lidar" name="lidar3d">
    <always_on>true</always_on>
    <update_rate>20</update_rate>
    <visualize>false</visualize>
    
    <lidar>
      <scan>
        <!-- Horizontal scanning -->
        <horizontal>
          <samples>1024</samples>        <!-- 0.35° resolution -->
          <resolution>1</resolution>
          <min_angle>-3.14159</min_angle>
          <max_angle>3.14159</max_angle>
        </horizontal>
        
        <!-- Vertical scanning (multiple layers) -->
        <vertical>
          <samples>64</samples>          <!-- 64 laser beams -->
          <resolution>1</resolution>
          <min_angle>-0.436332</min_angle>  <!-- ~-25° -->
          <max_angle>0.436332</max_angle>   <!-- ~+25° -->
        </vertical>
      </scan>
      
      <!-- Range parameters -->
      <range>
        <min>0.05</min>
        <max>200</max>
        <resolution>0.01</resolution>
      </range>
      
      <!-- Noise for realism -->
      <noise>
        <type>gaussian</type>
        <mean>0</mean>
        <stddev>0.05</stddev>
      </noise>
    </lidar>
    
    <!-- ROS 2 plugin -->
    <plugin name="gazebo_ros_gpu_lidar_sensor" 
            filename="libgazebo_ros_gpu_lidar_sensor.so">
      <ros>
        <remapping>~/out:=/lidar/points</remapping>
      </ros>
    </plugin>
  </sensor>
</gazebo>
```

### Processing LiDAR Data

```python
import rclpy
from sensor_msgs.msg import LaserScan, PointCloud2
from geometry_msgs.msg import TransformStamped
import numpy as np
from ros2_numpy import pointcloud2_to_xyz_array

class LiDARProcessor:
    """Process LiDAR data for navigation and obstacle detection"""
    
    def __init__(self):
        self.node = rclpy.create_node('lidar_processor')
        
        # Subscribe to 2D LiDAR
        self.scan_sub = self.node.create_subscription(
            LaserScan, '/lidar/scan', self.scan_callback, 10
        )
        
        # Subscribe to 3D LiDAR
        self.pointcloud_sub = self.node.create_subscription(
            PointCloud2, '/lidar/points', self.pointcloud_callback, 10
        )
        
        # Publisher for processed data
        self.obstacle_pub = self.node.create_publisher(
            PointCloud2, '/obstacles', 10
        )
    
    def scan_callback(self, msg):
        """Process 2D laser scan"""
        # msg.ranges: array of distance measurements
        ranges = np.array(msg.ranges)
        angles = np.linspace(msg.angle_min, msg.angle_max, len(ranges))
        
        # Convert to Cartesian coordinates
        x = ranges * np.cos(angles)
        y = ranges * np.sin(angles)
        
        # Find obstacles (points closer than threshold)
        threshold = 1.0  # 1 meter
        obstacles = ranges < threshold
        
        self.node.get_logger().info(
            f'Found {np.sum(obstacles)} obstacle measurements'
        )
    
    def pointcloud_callback(self, msg):
        """Process 3D point cloud"""
        # Convert ROS PointCloud2 to numpy array
        xyz_array = pointcloud2_to_xyz_array(msg)
        
        # Filter ground points
        ground_threshold = 0.2  # 20 cm above ground
        above_ground = xyz_array[:, 2] > ground_threshold
        
        # Filter far points
        distance = np.linalg.norm(xyz_array[:, :2], axis=1)
        near_points = distance < 10.0  # 10 meter range
        
        # Combined filter
        valid_points = above_ground & near_points
        filtered_points = xyz_array[valid_points]
        
        self.node.get_logger().debug(
            f'Filtered {len(filtered_points)} valid points'
        )
```

## Depth Cameras

### Understanding Depth Cameras

Depth cameras measure distance to every pixel in the image:

```
RGB-D Camera (Kinect, RealSense style):

    Image Size: 640×480 pixels
    
    Each pixel contains:
    ┌──────────────────────┐
    │ R: Red channel       │
    │ G: Green channel     │
    │ B: Blue channel      │
    │ D: Depth value (mm)  │
    └──────────────────────┘
    
    Typical depth range: 0.1 - 10 meters
```

### Simulating Depth Camera

```xml
<gazebo reference="depth_camera_link">
  <sensor type="depth_camera" name="depth_camera">
    <always_on>true</always_on>
    <update_rate>30</update_rate>
    <visualize>true</visualize>
    
    <camera>
      <!-- Camera intrinsics -->
      <horizontal_fov>1.047</horizontal_fov>  <!-- ~60 degrees -->
      <image>
        <width>640</width>
        <height>480</height>
        <format>R8G8B8</format>
      </image>
      
      <!-- Clipping (near/far planes) -->
      <clip>
        <near>0.1</near>              <!-- 10 cm minimum -->
        <far>10</far>                 <!-- 10 m maximum -->
      </clip>
      
      <!-- Noise simulation -->
      <noise>
        <type>gaussian</type>
        <mean>0</mean>
        <stddev>0.01</stddev>         <!-- 1 cm noise -->
      </noise>
      
      <!-- Distortion (optional) -->
      <distortion>
        <k1>0.0</k1>
        <k2>0.0</k2>
        <k3>0.0</k3>
        <p1>0.0</p1>
        <p2>0.0</p2>
      </distortion>
    </camera>
    
    <!-- ROS 2 plugin -->
    <plugin name="gazebo_ros_camera_sensor" 
            filename="libgazebo_ros_camera_sensor.so">
      <ros>
        <remapping>~/image_raw:=/depth_camera/image</remapping>
        <remapping>~/camera_info:=/depth_camera/camera_info</remapping>
        <remapping>~/depth_image_raw:=/depth_camera/depth</remapping>
      </ros>
      <camera_name>depth_camera</camera_name>
    </plugin>
  </sensor>
</gazebo>
```

### Processing Depth Camera Data

```python
import rclpy
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
import numpy as np

class DepthCameraProcessor:
    """Process depth camera data for 3D perception"""
    
    def __init__(self):
        self.node = rclpy.create_node('depth_processor')
        self.bridge = CvBridge()
        
        # Subscribe to depth image
        self.depth_sub = self.node.create_subscription(
            Image, '/depth_camera/depth', self.depth_callback, 10
        )
        
        # Subscribe to RGB image
        self.rgb_sub = self.node.create_subscription(
            Image, '/depth_camera/image', self.rgb_callback, 10
        )
        
        # Camera calibration
        self.fx = 554.3  # focal length x (pixels)
        self.fy = 554.3  # focal length y (pixels)
        self.cx = 320.0  # principal point x
        self.cy = 240.0  # principal point y
    
    def depth_callback(self, msg):
        """Process depth image"""
        # Convert ROS message to OpenCV image
        depth_cv = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        
        # Depth is typically in mm, convert to meters
        depth_m = depth_cv.astype(np.float32) / 1000.0
        
        # Get statistics
        valid_depth = depth_m[depth_m > 0]
        if len(valid_depth) > 0:
            min_depth = np.min(valid_depth)
            max_depth = np.max(valid_depth)
            mean_depth = np.mean(valid_depth)
            
            self.node.get_logger().debug(
                f'Depth: min={min_depth:.2f}m, max={max_depth:.2f}m, '
                f'mean={mean_depth:.2f}m'
            )
    
    def rgb_callback(self, msg):
        """Process RGB image"""
        rgb_cv = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        
        # Example: object detection
        # (Placeholder - would use actual detection network)
        self.node.get_logger().debug(f'RGB image received: {rgb_cv.shape}')
    
    def depth_to_pointcloud(self, depth_cv):
        """
        Convert depth image to point cloud
        
        Args:
            depth_cv: Depth image (height × width)
        
        Returns:
            Point cloud array (N × 3): [x, y, z] coordinates
        """
        height, width = depth_cv.shape
        
        # Create pixel coordinate arrays
        y_pixels = np.arange(height)
        x_pixels = np.arange(width)
        x_grid, y_grid = np.meshgrid(x_pixels, y_pixels)
        
        # Convert pixel coordinates to 3D using camera intrinsics
        depth = depth_cv.astype(np.float32) / 1000.0  # Convert to meters
        
        x = (x_grid - self.cx) * depth / self.fx
        y = (y_grid - self.cy) * depth / self.fy
        z = depth
        
        # Stack into point cloud
        points = np.stack([x, y, z], axis=-1)
        
        # Reshape to N × 3
        pointcloud = points.reshape(-1, 3)
        
        # Filter invalid points
        valid = (z > 0.1) & (z < 10.0)
        pointcloud = pointcloud[valid.flatten()]
        
        return pointcloud
```

## Inertial Measurement Unit (IMU)

### Understanding IMU

An IMU measures acceleration and rotation:

```
IMU Sensor:
├── Accelerometer (3 axes)
│   └─ Measures: linear acceleration
│       Units: m/s² or g
│       Affected by: gravity, motion
│
├── Gyroscope (3 axes)
│   └─ Measures: angular velocity (rotation rate)
│       Units: rad/s or deg/s
│       
└── Magnetometer (3 axes, optional)
    └─ Measures: magnetic field
        Units: Gauss or Tesla
```

### Simulating IMU

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <model name="robot_with_imu" static="false">
    
    <!-- Robot body -->
    <link name="base_link">
      <inertial>
        <mass value="10"/>
        <inertia ixx="0.1" ixy="0" ixz="0"
                 iyy="0.1" iyz="0"
                 izz="0.1"/>
      </inertial>
      <visual>
        <geometry>
          <box size="0.3 0.3 0.3"/>
        </geometry>
      </visual>
      <collision>
        <geometry>
          <box size="0.3 0.3 0.3"/>
        </geometry>
      </collision>
    </link>
    
  </model>
</sdf>

<!-- IMU Gazebo plugin -->
<gazebo reference="base_link">
  <sensor type="imu" name="imu_sensor">
    <always_on>true</always_on>
    <update_rate>100</update_rate>
    <visualize>false</visualize>
    
    <imu>
      <!-- Accelerometer noise -->
      <linear_acceleration>
        <x>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.02</stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.02</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.02</stddev>
          </noise>
        </z>
      </linear_acceleration>
      
      <!-- Gyroscope noise -->
      <angular_velocity>
        <x>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.005</stddev>
          </noise>
        </x>
        <y>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.005</stddev>
          </noise>
        </y>
        <z>
          <noise type="gaussian">
            <mean>0</mean>
            <stddev>0.005</stddev>
          </noise>
        </z>
      </angular_velocity>
    </imu>
    
    <!-- ROS 2 plugin -->
    <plugin name="gazebo_ros_imu_sensor" 
            filename="libgazebo_ros_imu_sensor.so">
      <ros>
        <remapping>~/out:=/imu/data</remapping>
      </ros>
      <initial_orient_as_reference>false</initial_orient_as_reference>
    </plugin>
  </sensor>
</gazebo>
```

### Processing IMU Data

```python
import rclpy
from sensor_msgs.msg import Imu
import numpy as np
from scipy.spatial.transform import Rotation as R
from collections import deque

class IMUProcessor:
    """Process IMU data for state estimation"""
    
    def __init__(self, buffer_size=100):
        self.node = rclpy.create_node('imu_processor')
        
        # Subscribe to IMU
        self.imu_sub = self.node.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10
        )
        
        # State buffers
        self.accel_buffer = deque(maxlen=buffer_size)
        self.gyro_buffer = deque(maxlen=buffer_size)
        
        # Integration state
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.orientation = R.from_euler('xyz', [0, 0, 0])
        
        self.gravity = np.array([0, 0, 9.81])
    
    def imu_callback(self, msg):
        """Process IMU measurement"""
        
        # Extract measurements
        accel = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])
        
        gyro = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])
        
        # Store in buffers
        self.accel_buffer.append(accel)
        self.gyro_buffer.append(gyro)
        
        # Gravity compensation
        # Raw acceleration includes gravity effect
        accel_compensated = accel - self.gravity
        
        # Integrate to velocity (simple integration)
        dt = 1.0 / 100.0  # 100 Hz IMU
        self.velocity += accel_compensated * dt
        
        # Integrate angular velocity to orientation
        angle_change = gyro * dt
        angle_magnitude = np.linalg.norm(angle_change)
        
        if angle_magnitude > 1e-6:
            angle_axis = angle_change / angle_magnitude
            self.orientation = self.orientation * \
                R.from_rotvec(angle_change)
    
    def get_orientation_euler(self):
        """Get orientation as Euler angles"""
        return self.orientation.as_euler('xyz')
    
    def get_orientation_quaternion(self):
        """Get orientation as quaternion"""
        return self.orientation.as_quat()  # [x, y, z, w]
    
    def get_velocity(self):
        """Get estimated velocity"""
        return self.velocity.copy()
    
    def detect_motion(self, threshold=0.1):
        """Detect if robot is moving"""
        if len(self.accel_buffer) < 10:
            return False
        
        mean_accel = np.mean(list(self.accel_buffer), axis=0)
        motion_magnitude = np.linalg.norm(mean_accel)
        
        return motion_magnitude > threshold
    
    def detect_tilt(self):
        """Detect robot tilt from gravity vector"""
        # In resting state, accelerometer measures -gravity
        # Tilt is deviation from vertical
        if len(self.accel_buffer) < 10:
            return 0
        
        mean_accel = np.mean(list(self.accel_buffer), axis=0)
        accel_norm = mean_accel / (np.linalg.norm(mean_accel) + 1e-6)
        
        # Vertical should be [0, 0, -1] (pointing down)
        vertical = np.array([0, 0, -1])
        
        # Angle between measured and vertical
        cos_angle = np.dot(accel_norm, vertical)
        tilt_angle = np.arccos(np.clip(cos_angle, -1, 1))
        
        return np.degrees(tilt_angle)
```

## Combining Multiple Sensors

### Multi-Sensor Robot Configuration

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <model name="sensor_equipped_robot" static="false">
    
    <!-- Base -->
    <link name="base_link">
      <inertial>
        <mass value="15"/>
        <inertia ixx="0.15" ixy="0" ixz="0"
                 iyy="0.15" iyz="0"
                 izz="0.15"/>
      </inertial>
      <visual>
        <geometry>
          <cylinder radius="0.25" length="0.1"/>
        </geometry>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="0.25" length="0.1"/>
        </geometry>
      </collision>
    </link>
    
    <!-- LiDAR mount (top) -->
    <link name="lidar_link">
      <pose relative_to="base_link">0 0 0.2 0 0 0</pose>
      <visual>
        <geometry>
          <cylinder radius="0.05" length="0.04"/>
        </geometry>
      </visual>
      <inertial>
        <mass value="0.5"/>
        <inertia ixx="0.001" ixy="0" ixz="0"
                 iyy="0.001" iyz="0"
                 izz="0.001"/>
      </inertial>
    </link>
    
    <joint name="lidar_joint" type="fixed">
      <parent>base_link</parent>
      <child>lidar_link</child>
    </joint>
    
    <!-- Depth Camera (front) -->
    <link name="depth_camera_link">
      <pose relative_to="base_link">0.15 0 0.1 0 0 0</pose>
      <visual>
        <geometry>
          <box size="0.05 0.15 0.05"/>
        </geometry>
      </visual>
      <inertial>
        <mass value="0.2"/>
        <inertia ixx="0.0001" ixy="0" ixz="0"
                 iyy="0.0001" iyz="0"
                 izz="0.0001"/>
      </inertial>
    </link>
    
    <joint name="depth_camera_joint" type="fixed">
      <parent>base_link</parent>
      <child>depth_camera_link</child>
    </joint>
    
    <!-- IMU (integrated in base) -->
    <!-- (Uses base_link directly in Gazebo plugin) -->
    
  </model>
</sdf>
```

### Sensor Fusion Example

```python
import rclpy
from sensor_msgs.msg import LaserScan, Image, Imu
import numpy as np

class SensorFusion:
    """Fuse multiple sensor streams for robust perception"""
    
    def __init__(self):
        self.node = rclpy.create_node('sensor_fusion')
        
        self.scan_sub = self.node.create_subscription(
            LaserScan, '/lidar/scan', self.scan_callback, 10)
        self.depth_sub = self.node.create_subscription(
            Image, '/depth_camera/depth', self.depth_callback, 10)
        self.imu_sub = self.node.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)
        
        self.latest_scan = None
        self.latest_depth = None
        self.latest_imu = None
    
    def scan_callback(self, msg):
        self.latest_scan = msg
        self.fuse_sensors()
    
    def depth_callback(self, msg):
        self.latest_depth = msg
        self.fuse_sensors()
    
    def imu_callback(self, msg):
        self.latest_imu = msg
        self.fuse_sensors()
    
    def fuse_sensors(self):
        """Fuse available sensor data"""
        
        # Check which sensors have data
        sensors_available = [
            self.latest_scan is not None,
            self.latest_depth is not None,
            self.latest_imu is not None
        ]
        
        if sum(sensors_available) < 2:
            return  # Need at least 2 sensors
        
        # Multi-sensor fusion logic
        # Example: Use LiDAR for obstacle detection
        #         Use IMU for motion estimation
        #         Use Depth for object recognition
        
        self.node.get_logger().debug(
            f'Fusing {sum(sensors_available)} sensors'
        )
```

## Summary

Gazebo provides comprehensive sensor simulation enabling realistic robot perception testing. LiDAR, depth cameras, and IMUs are fundamental sensors that, when properly simulated, generate data suitable for algorithm validation before hardware deployment.

## Key Takeaways

- LiDAR generates point clouds for navigation and mapping
- Depth cameras provide RGB-D data for object recognition
- IMUs measure acceleration and rotation for state estimation
- Gazebo plugins provide ROS 2 integration for all sensors
- Realistic noise simulation improves algorithm robustness
- Multi-sensor fusion enhances perception reliability
- Simulation enables safe algorithm development and testing