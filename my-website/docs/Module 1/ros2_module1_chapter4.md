# Chapter 4: Understanding URDF for Humanoids

## Introduction

The Unified Robot Description Format (URDF) is an XML-based format for describing robot structure, geometry, and physical properties. This chapter explores URDF in detail, with emphasis on humanoid robot configurations. Understanding URDF is essential for simulation, visualization, and physics-based planning.

## What is URDF?

URDF is a standard format for representing robot models in ROS. It defines:
- **Links**: Rigid bodies (body parts)
- **Joints**: Connections between links (movement constraints)
- **Sensors and Actuators**: Cameras, IMUs, motors
- **Collision Geometry**: For collision detection
- **Visual Geometry**: For visualization
- **Inertial Properties**: Mass, center of mass, inertia tensor

## Basic URDF Structure

```xml
<?xml version="1.0"?>
<robot name="my_robot">
    <!-- Links (rigid bodies) -->
    <link name="base_link">
        <!-- Visual geometry -->
        <!-- Collision geometry -->
        <!-- Inertial properties -->
    </link>
    
    <!-- Joints (connections) -->
    <joint name="joint_name" type="revolute">
        <parent link="parent_link"/>
        <child link="child_link"/>
        <origin xyz="0 0 0" rpy="0 0 0"/>
        <axis xyz="0 0 1"/>
        <limit lower="0" upper="3.14159" effort="10" velocity="1"/>
    </joint>
</robot>
```

## Part 1: Links

### What is a Link?

A link is a rigid body representing a physical component of the robot:
- Base (torso)
- Body segments (upper arm, forearm, hand)
- Wheels
- Gripper

### Link Properties

```xml
<link name="upper_arm">
    <!-- Visual properties for visualization -->
    <visual>
        <origin xyz="0 0 0.25" rpy="0 0 0"/>
        <geometry>
            <cylinder length="0.5" radius="0.05"/>
        </geometry>
        <material name="steel">
            <color rgba="0.5 0.5 0.5 1.0"/>
        </material>
    </visual>
    
    <!-- Collision geometry for physics -->
    <collision>
        <origin xyz="0 0 0.25" rpy="0 0 0"/>
        <geometry>
            <cylinder length="0.5" radius="0.05"/>
        </geometry>
    </collision>
    
    <!-- Inertial properties -->
    <inertial>
        <origin xyz="0 0 0.25" rpy="0 0 0"/>
        <mass value="5.0"/>
        <inertia ixx="0.1" ixy="0" ixz="0"
                 iyy="0.1" iyz="0" 
                 izz="0.01"/>
    </inertial>
</link>
```

### Visual Geometry Types

#### Primitive Shapes
```xml
<!-- Cylinder -->
<geometry>
    <cylinder length="0.5" radius="0.05"/>
</geometry>

<!-- Box -->
<geometry>
    <box size="0.1 0.2 0.3"/>  <!-- length, width, height -->
</geometry>

<!-- Sphere -->
<geometry>
    <sphere radius="0.1"/>
</geometry>
```

#### Mesh Files
```xml
<!-- Using external mesh files -->
<geometry>
    <mesh filename="package://my_robot/meshes/arm.stl"
           scale="0.001 0.001 0.001"/>
</geometry>

<!-- Supported formats: STL, DAE, OBJ -->
```

### Inertial Properties

The inertia tensor describes how mass is distributed around the center of mass:

```xml
<inertial>
    <mass value="2.5"/>
    <!-- Inertia matrix (symmetric) -->
    <inertia ixx="0.05" ixy="0" ixz="0"
             iyy="0.05" iyz="0"
             izz="0.02"/>
</inertial>
```

Where:
- `ixx`, `iyy`, `izz`: Moment of inertia around X, Y, Z axes
- `ixy`, `ixz`, `iyz`: Products of inertia (usually 0 for symmetric objects)

### Origin and Frames

The `<origin>` element defines a reference frame:

```xml
<origin xyz="x y z" rpy="roll pitch yaw"/>
```

- `xyz`: Position relative to parent frame (meters)
- `rpy`: Rotation (roll, pitch, yaw) in radians

## Part 2: Joints

### Joint Types

#### Revolute Joint (Rotating)
Allows rotation around a single axis within limits:

```xml
<joint name="shoulder_pitch" type="revolute">
    <parent link="torso"/>
    <child link="upper_arm"/>
    <origin xyz="0 0.1 0.3" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>  <!-- Rotate around X-axis -->
    <limit lower="-1.57" upper="1.57" effort="50" velocity="2.0"/>
    <dynamics damping="0.1" friction="0.1"/>
</joint>
```

#### Prismatic Joint (Sliding)
Allows linear translation along a single axis:

```xml
<joint name="telescopic_arm" type="prismatic">
    <parent link="base"/>
    <child link="extension"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>  <!-- Slide along Z-axis -->
    <limit lower="0" upper="0.5" effort="100" velocity="0.5"/>
</joint>
```

#### Fixed Joint
No movement (rigid connection):

```xml
<joint name="camera_mount" type="fixed">
    <parent link="head"/>
    <child link="camera"/>
    <origin xyz="0.05 0 0.05" rpy="0 0 0"/>
</joint>
```

#### Planar Joint
Movement in a plane (2D):

```xml
<joint name="mobile_base_planar" type="planar">
    <parent link="world"/>
    <child link="base_link"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
</joint>
```

### Joint Attributes

```xml
<joint name="elbow" type="revolute">
    <!-- Kinematic chain -->
    <parent link="upper_arm"/>
    <child link="forearm"/>
    
    <!-- Position and orientation -->
    <origin xyz="0 0 0.5" rpy="0 0 0"/>
    
    <!-- Rotation axis (unit vector) -->
    <axis xyz="0 1 0"/>  <!-- Y-axis rotation -->
    
    <!-- Motion limits -->
    <limit 
        lower="-2.5"      <!-- Minimum angle (rad) -->
        upper="2.5"       <!-- Maximum angle (rad) -->
        effort="80"       <!-- Maximum torque (N⋅m) -->
        velocity="1.5"/>  <!-- Maximum speed (rad/s) -->
    
    <!-- Physical properties -->
    <dynamics 
        damping="0.2"     <!-- Damping coefficient -->
        friction="0.1"    <!-- Friction coefficient -->
        spring_reference="0"
        spring_stiffness="0"/>
</joint>
```

## Part 3: Simple Humanoid Example

### Basic Human-Like Structure

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">
    
    <!-- ==================== TORSO ==================== -->
    <link name="base_link">
        <visual>
            <geometry>
                <box size="0.3 0.2 0.5"/>
            </geometry>
            <material name="torso_color">
                <color rgba="0.8 0.8 0.8 1.0"/>
            </material>
        </visual>
        <collision>
            <geometry>
                <box size="0.3 0.2 0.5"/>
            </geometry>
        </collision>
        <inertial>
            <mass value="20.0"/>
            <inertia ixx="1.0" ixy="0" ixz="0"
                     iyy="0.8" iyz="0"
                     izz="1.2"/>
        </inertial>
    </link>
    
    <!-- ==================== HEAD ==================== -->
    <link name="head">
        <visual>
            <origin xyz="0 0 0.15" rpy="0 0 0"/>
            <geometry>
                <sphere radius="0.1"/>
            </geometry>
            <material name="head_color">
                <color rgba="0.9 0.7 0.5 1.0"/>
            </material>
        </visual>
        <collision>
            <origin xyz="0 0 0.15" rpy="0 0 0"/>
            <geometry>
                <sphere radius="0.1"/>
            </geometry>
        </collision>
        <inertial>
            <origin xyz="0 0 0.15" rpy="0 0 0"/>
            <mass value="4.0"/>
            <inertia ixx="0.05" ixy="0" ixz="0"
                     iyy="0.05" iyz="0"
                     izz="0.04"/>
        </inertial>
    </link>
    
    <!-- Neck joint -->
    <joint name="neck_joint" type="revolute">
        <parent link="base_link"/>
        <child link="head"/>
        <origin xyz="0 0 0.35" rpy="0 0 0"/>
        <axis xyz="0 0 1"/>
        <limit lower="-1.57" upper="1.57" effort="10" velocity="2.0"/>
    </joint>
    
    <!-- ==================== LEFT ARM ==================== -->
    <link name="left_upper_arm">
        <visual>
            <origin xyz="0 0 -0.15" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.3" radius="0.04"/>
            </geometry>
            <material name="arm_color">
                <color rgba="0.8 0.8 0.8 1.0"/>
            </material>
        </visual>
        <collision>
            <origin xyz="0 0 -0.15" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.3" radius="0.04"/>
            </geometry>
        </collision>
        <inertial>
            <origin xyz="0 0 -0.15" rpy="0 0 0"/>
            <mass value="3.0"/>
            <inertia ixx="0.02" ixy="0" ixz="0"
                     iyy="0.02" iyz="0"
                     izz="0.001"/>
        </inertial>
    </link>
    
    <!-- Left shoulder joint -->
    <joint name="left_shoulder" type="revolute">
        <parent link="base_link"/>
        <child link="left_upper_arm"/>
        <origin xyz="0.15 0 0.2" rpy="0 0 0"/>
        <axis xyz="1 0 0"/>
        <limit lower="-1.57" upper="1.57" effort="30" velocity="1.5"/>
    </joint>
    
    <!-- Left forearm -->
    <link name="left_forearm">
        <visual>
            <origin xyz="0 0 -0.15" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.3" radius="0.035"/>
            </geometry>
            <material name="arm_color">
                <color rgba="0.7 0.7 0.7 1.0"/>
            </material>
        </visual>
        <collision>
            <origin xyz="0 0 -0.15" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.3" radius="0.035"/>
            </geometry>
        </collision>
        <inertial>
            <origin xyz="0 0 -0.15" rpy="0 0 0"/>
            <mass value="2.0"/>
            <inertia ixx="0.01" ixy="0" ixz="0"
                     iyy="0.01" iyz="0"
                     izz="0.0005"/>
        </inertial>
    </link>
    
    <!-- Left elbow joint -->
    <joint name="left_elbow" type="revolute">
        <parent link="left_upper_arm"/>
        <child link="left_forearm"/>
        <origin xyz="0 0 -0.3" rpy="0 0 0"/>
        <axis xyz="0 1 0"/>
        <limit lower="0" upper="2.5" effort="20" velocity="2.0"/>
    </joint>
    
    <!-- ==================== RIGHT ARM ==================== -->
    <!-- (Mirror of left arm) -->
    <link name="right_upper_arm">
        <visual>
            <origin xyz="0 0 -0.15" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.3" radius="0.04"/>
            </geometry>
            <material name="arm_color">
                <color rgba="0.8 0.8 0.8 1.0"/>
            </material>
        </visual>
        <collision>
            <origin xyz="0 0 -0.15" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.3" radius="0.04"/>
            </geometry>
        </collision>
        <inertial>
            <origin xyz="0 0 -0.15" rpy="0 0 0"/>
            <mass value="3.0"/>
            <inertia ixx="0.02" ixy="0" ixz="0"
                     iyy="0.02" iyz="0"
                     izz="0.001"/>
        </inertial>
    </link>
    
    <joint name="right_shoulder" type="revolute">
        <parent link="base_link"/>
        <child link="right_upper_arm"/>
        <origin xyz="-0.15 0 0.2" rpy="0 0 0"/>
        <axis xyz="1 0 0"/>
        <limit lower="-1.57" upper="1.57" effort="30" velocity="1.5"/>
    </joint>
    
    <!-- ==================== LEGS ==================== -->
    <link name="left_upper_leg">
        <visual>
            <origin xyz="0 0 -0.25" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.5" radius="0.05"/>
            </geometry>
            <material name="leg_color">
                <color rgba="0.6 0.6 0.6 1.0"/>
            </material>
        </visual>
        <collision>
            <origin xyz="0 0 -0.25" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.5" radius="0.05"/>
            </geometry>
        </collision>
        <inertial>
            <origin xyz="0 0 -0.25" rpy="0 0 0"/>
            <mass value="5.0"/>
            <inertia ixx="0.05" ixy="0" ixz="0"
                     iyy="0.05" iyz="0"
                     izz="0.003"/>
        </inertial>
    </link>
    
    <joint name="left_hip" type="revolute">
        <parent link="base_link"/>
        <child link="left_upper_leg"/>
        <origin xyz="0.1 0 -0.3" rpy="0 0 0"/>
        <axis xyz="1 0 0"/>
        <limit lower="-1.5" upper="1.5" effort="50" velocity="2.0"/>
    </joint>
    
    <link name="left_lower_leg">
        <visual>
            <origin xyz="0 0 -0.25" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.5" radius="0.045"/>
            </geometry>
            <material name="leg_color">
                <color rgba="0.5 0.5 0.5 1.0"/>
            </material>
        </visual>
        <collision>
            <origin xyz="0 0 -0.25" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.5" radius="0.045"/>
            </geometry>
        </collision>
        <inertial>
            <origin xyz="0 0 -0.25" rpy="0 0 0"/>
            <mass value="4.0"/>
            <inertia ixx="0.03" ixy="0" ixz="0"
                     iyy="0.03" iyz="0"
                     izz="0.002"/>
        </inertial>
    </link>
    
    <joint name="left_knee" type="revolute">
        <parent link="left_upper_leg"/>
        <child link="left_lower_leg"/>
        <origin xyz="0 0 -0.5" rpy="0 0 0"/>
        <axis xyz="1 0 0"/>
        <limit lower="0" upper="2.5" effort="40" velocity="2.0"/>
    </joint>
    
    <!-- Right leg (similar to left) -->
    <link name="right_upper_leg">
        <visual>
            <origin xyz="0 0 -0.25" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.5" radius="0.05"/>
            </geometry>
            <material name="leg_color">
                <color rgba="0.6 0.6 0.6 1.0"/>
            </material>
        </visual>
        <collision>
            <origin xyz="0 0 -0.25" rpy="0 0 0"/>
            <geometry>
                <cylinder length="0.5" radius="0.05"/>
            </geometry>
        </collision>
        <inertial>
            <origin xyz="0 0 -0.25" rpy="0 0 0"/>
            <mass value="5.0"/>
            <inertia ixx="0.05" ixy="0" ixz="0"
                     iyy="0.05" iyz="0"
                     izz="0.003"/>
        </inertial>
    </link>
    
    <joint name="right_hip" type="revolute">
        <parent link="base_link"/>
        <child link="right_upper_leg"/>
        <origin xyz="-0.1 0 -0.3" rpy="0 0 0"/>
        <axis xyz="1 0 0"/>
        <limit lower="-1.5" upper="1.5" effort="50" velocity="2.0"/>
    </joint>

</robot>
```

## Part 4: Advanced URDF Features

### Transmission Elements
Transmissions define how actuators drive joints:

```xml
<transmission name="left_shoulder_trans">
    <type>transmission_interface/SimpleTransmission</type>
    <joint name="left_shoulder">
        <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
    </joint>
    <actuator name="left_shoulder_motor">
        <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
        <mechanicalReduction>50</mechanicalReduction>
    </actuator>
</transmission>
```

### Gazebo-Specific Extensions
Add simulation properties for Gazebo:

```xml
<gazebo reference="left_upper_arm">
    <material>Gazebo/Steel</material>
    <mu1>0.5</mu1>
    <mu2>0.5</mu2>
    <selfCollide>false</selfCollide>
</gazebo>

<gazebo reference="left_elbow">
    <implicitSpringDamper>true</implicitSpringDamper>
</gazebo>
```

### Sensors in URDF

#### IMU Sensor
```xml
<link name="imu_link">
    <inertial>
        <mass value="0.1"/>
        <inertia ixx="0.0001" ixy="0" ixz="0"
                 iyy="0.0001" iyz="0"
                 izz="0.0001"/>
    </inertial>
</link>

<joint name="imu_joint" type="fixed">
    <parent link="base_link"/>
    <child link="imu_link"/>
</joint>

<gazebo reference="imu_link">
    <sensor type="imu" name="imu_sensor">
        <always_on>true</always_on>
        <update_rate>100</update_rate>
    </sensor>
</gazebo>
```

#### Camera Sensor
```xml
<link name="camera_link">
    <visual>
        <geometry>
            <box size="0.05 0.05 0.05"/>
        </geometry>
    </visual>
</link>

<gazebo reference="camera_link">
    <sensor type="camera" name="camera_sensor">
        <camera>
            <horizontal_fov>1.047</horizontal_fov>
            <image>
                <width>640</width>
                <height>480</height>
                <format>R8G8B8</format>
            </image>
            <clip>
                <near>0.1</near>
                <far>100</far>
            </clip>
        </camera>
        <always_on>1</always_on>
        <update_rate>30</update_rate>
        <visualize>true</visualize>
    </sensor>
</gazebo>
```

## Part 5: Loading and Using URDF

### Loading URDF in Python

```python
import rclpy
from ament_index_python.packages import get_package_share_directory
import os

def load_urdf(package_name, urdf_file):
    """Load URDF file"""
    package_path = get_package_share_directory(package_name)
    urdf_path = os.path.join(package_path, 'urdf', urdf_file)
    
    with open(urdf_path, 'r') as f:
        urdf_content = f.read()
    
    return urdf_content
```

### Visualization with RVIZ

```python
from std_msgs.msg import Header
from visualization_msgs.msg import MarkerArray, Marker
import tf_transformations

def visualize_robot_model(urdf_content):
    """Publish robot model for RVIZ visualization"""
    # This is typically done automatically by ROS 2
    # but can be done manually for custom visualizations
    pass
```

## Common Humanoid Configurations

### Degrees of Freedom (DoF) Breakdown

**Typical Humanoid (Example: NAO)**
- Torso: 0 DoF (fixed to world or mobile base)
- Head: 2 DoF (pan, tilt)
- Left Arm: 5 DoF (shoulder pan, shoulder lift, elbow, wrist)
- Right Arm: 5 DoF (mirrored)
- Left Leg: 6 DoF (hip roll, hip pitch, knee, ankle roll, ankle pitch)
- Right Leg: 6 DoF (mirrored)
- **Total: 24 DoF**

### More Complex Humanoid (Example: KUKA iiwa arm humanoid)
- Torso: 1 DoF (rotation)
- Head: 3 DoF
- Each Arm: 7 DoF
- Each Leg: 6 DoF
- **Total: 31+ DoF**

## Debugging URDF

### Check URDF Validity
```bash
check_urdf my_robot.urdf
urdf_to_graphviz my_robot.urdf -o my_robot.pdf
```

### Common Issues
1. **Cyclic chains**: No loops allowed in kinematic tree
2. **Missing inertia**: Add dummy inertia if not specified
3. **Wrong axis orientation**: Use visualization to verify
4. **Collision geometry too large**: Causes unwanted collisions

## Summary

URDF is the standard way to describe robots in ROS 2. For humanoids, it provides a structured way to define complex kinematic chains with proper inertial properties for simulation. Mastering URDF is essential for working with humanoid robots in both simulation and real hardware.

## Key Takeaways

- URDF defines robot structure as a kinematic tree of links and joints
- Links are rigid bodies; joints connect them with motion constraints
- Proper inertial properties are crucial for realistic simulation
- Humanoids typically have 20-30+ degrees of freedom
- Visual and collision geometries can differ
- URDF supports sensors, actuators, and physics properties
- Gazebo extensions enable physics simulation in URDF