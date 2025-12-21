# Chapter 3: Building Gazebo Environments and Worlds

## Introduction

Gazebo worlds define the simulation environment where robots operate. This chapter covers creating realistic environments with obstacles, lighting, materials, and dynamic objects. A well-designed world is essential for testing robot algorithms in representative conditions.

## Gazebo World Structure (SDF Format)

### SDF vs URDF

| Aspect | URDF | SDF |
|--------|------|-----|
| Purpose | Robot description | World description |
| Scope | Single robot model | Entire simulation world |
| Physics | Minimal | Complete |
| Extensibility | Limited | Excellent |
| Gazebo support | Via conversion | Native |

### Basic SDF Document Structure

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <!-- World definition -->
  <world name="my_simulation_world">
    
    <!-- Physics configuration -->
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>
    
    <!-- Gravity vector -->
    <gravity>0 0 -9.81</gravity>
    
    <!-- Lighting -->
    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <intensity>1.0</intensity>
      <direction>-0.5 0.1 -0.9</direction>
    </light>
    
    <!-- Static ground plane -->
    <model name="ground_plane" static="true">
      <!-- Model content -->
    </model>
    
    <!-- Dynamic models -->
    <model name="my_robot" static="false">
      <!-- Robot definition -->
    </model>
    
    <!-- Environmental obstacles -->
    <model name="table" static="true">
      <!-- Obstacle definition -->
    </model>
    
  </world>
</sdf>
```

## Creating Ground and Basic Surfaces

### Ground Plane

The ground plane is typically a large static plane at z=0:

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <world name="ground_world">
    
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>
    
    <gravity>0 0 -9.81</gravity>
    
    <!-- Ground plane -->
    <model name="ground_plane" static="true">
      <link name="ground_link">
        <collision name="ground_collision">
          <geometry>
            <!-- Plane is infinite size -->
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        
        <visual name="ground_visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
            <specular>0.8 0.8 0.8 1</specular>
          </material>
        </visual>
      </link>
    </model>
    
  </world>
</sdf>
```

### Textured Ground

```xml
<!-- Ground with image texture -->
<model name="textured_ground" static="true">
  <link name="ground_link">
    <collision name="ground_collision">
      <geometry>
        <plane>
          <normal>0 0 1</normal>
          <size>100 100</size>
        </plane>
      </geometry>
    </collision>
    
    <visual name="ground_visual">
      <geometry>
        <plane>
          <normal>0 0 1</normal>
          <size>100 100</size>
        </plane>
      </geometry>
      <material>
        <!-- Use texture file -->
        <script>
          <uri>file://materials/scripts/gazebo.material</uri>
          <name>Gazebo/Brick</name>
        </script>
      </material>
    </visual>
  </link>
</model>
```

## Creating Obstacles and Structures

### Simple Box Obstacle

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <model name="box_obstacle" static="true">
    <pose>5 5 0.5 0 0 0</pose>
    
    <link name="box_link">
      <!-- Visual geometry -->
      <visual name="box_visual">
        <geometry>
          <box size="1 1 1"/>
        </geometry>
        <material>
          <ambient>1 0 0 1</ambient>
          <diffuse>1 0 0 1</diffuse>
          <specular>0.5 0.5 0.5 1</specular>
        </material>
      </visual>
      
      <!-- Collision geometry -->
      <collision name="box_collision">
        <geometry>
          <box size="1 1 1"/>
        </geometry>
      </collision>
      
      <!-- Inertial properties (even for static, can be needed) -->
      <inertial>
        <mass value="100.0"/>
        <inertia ixx="8.33" ixy="0" ixz="0"
                 iyy="8.33" iyz="0"
                 izz="8.33"/>
      </inertial>
    </link>
  </model>
</sdf>
```

### Complex Structure: Table with Objects

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <world name="manipulation_world">
    
    <!-- Table -->
    <model name="table" static="true">
      <pose>3 3 0 0 0 0</pose>
      
      <!-- Table top -->
      <link name="table_top">
        <pose>0 0 0.75 0 0 0</pose>
        <visual>
          <geometry>
            <box size="1.5 0.8 0.05"/>
          </geometry>
          <material>
            <script>
              <uri>file://materials/scripts/gazebo.material</uri>
              <name>Gazebo/Wood</name>
            </script>
          </material>
        </visual>
        <collision>
          <geometry>
            <box size="1.5 0.8 0.05"/>
          </geometry>
        </collision>
        <inertial>
          <mass value="50.0"/>
          <inertia ixx="5" ixy="0" ixz="0"
                   iyy="5" iyz="0"
                   izz="5"/>
        </inertial>
      </link>
      
      <!-- Leg 1 -->
      <link name="leg_1">
        <pose>-0.6 -0.3 0.375 0 0 0</pose>
        <visual>
          <geometry>
            <box size="0.05 0.05 0.75"/>
          </geometry>
          <material>
            <script>
              <uri>file://materials/scripts/gazebo.material</uri>
              <name>Gazebo/Wood</name>
            </script>
          </material>
        </visual>
        <collision>
          <geometry>
            <box size="0.05 0.05 0.75"/>
          </geometry>
        </collision>
        <inertial>
          <mass value="5.0"/>
          <inertia ixx="0.1" ixy="0" ixz="0"
                   iyy="0.1" iyz="0"
                   izz="0.001"/>
        </inertial>
      </link>
      
      <!-- Additional legs (leg_2, leg_3, leg_4) would be similar -->
      
      <!-- Joints to fix legs to table -->
      <joint name="leg_1_joint" type="fixed">
        <parent>table_top</parent>
        <child>leg_1</child>
      </joint>
    </model>
    
    <!-- Object on table -->
    <model name="cube_on_table" static="false">
      <pose>3 3 0.83 0 0 0</pose>
      
      <link name="cube_link">
        <visual>
          <geometry>
            <box size="0.1 0.1 0.1"/>
          </geometry>
          <material>
            <ambient>0 1 0 1</ambient>
            <diffuse>0 1 0 1</diffuse>
            <specular>0.5 0.5 0.5 1</specular>
          </material>
        </visual>
        <collision>
          <geometry>
            <box size="0.1 0.1 0.1"/>
          </geometry>
        </collision>
        <inertial>
          <mass value="0.5"/>
          <inertia ixx="0.0001" ixy="0" ixz="0"
                   iyy="0.0001" iyz="0"
                   izz="0.0001"/>
        </inertial>
      </link>
    </model>
    
  </world>
</sdf>
```

## Lighting and Materials

### Lighting Types

#### Directional Light (Sun)
```xml
<light name="sun" type="directional">
  <pose>10 10 10 0 0 0</pose>
  <diffuse>1 1 1 1</diffuse>
  <specular>1 1 1 1</specular>
  <intensity>1.0</intensity>
  <direction>-0.5 0.1 -0.9</direction>
  <cast_shadows>true</cast_shadows>
</light>
```

#### Point Light
```xml
<light name="room_light" type="point">
  <pose>5 5 3 0 0 0</pose>
  <diffuse>1 1 1 1</diffuse>
  <specular>0.8 0.8 0.8 1</specular>
  <intensity>0.8</intensity>
  <range>10</range>
  <attenuation>
    <linear>0.01</linear>
    <quadratic>0.001</quadratic>
  </attenuation>
  <cast_shadows>true</cast_shadows>
</light>
```

#### Spot Light
```xml
<light name="spotlight" type="spot">
  <pose>5 5 5 0 0 0</pose>
  <direction>0 0 -1</direction>
  <diffuse>1 1 1 1</diffuse>
  <specular>1 1 1 1</specular>
  <intensity>1.0</intensity>
  <range>5</range>
  <spot>
    <inner_angle>0.3</inner_angle>
    <outer_angle>1.0</outer_angle>
    <falloff>1.0</falloff>
  </spot>
  <cast_shadows>true</cast_shadows>
</light>
```

### Material Properties

```xml
<!-- Shiny metallic material -->
<material name="shiny_metal">
  <ambient>0.3 0.3 0.3 1</ambient>
  <diffuse>0.7 0.7 0.7 1</diffuse>
  <specular>0.9 0.9 0.9 1</specular>
  <emissive>0 0 0 0</emissive>
  <shininess>100</shininess>
</material>

<!-- Matte rubber material -->
<material name="matte_rubber">
  <ambient>0.2 0.2 0.2 1</ambient>
  <diffuse>0.5 0.5 0.5 1</diffuse>
  <specular>0.1 0.1 0.1 1</specular>
  <emissive>0 0 0 0</emissive>
  <shininess>10</shininess>
</material>

<!-- Glowing material -->
<material name="glowing">
  <ambient>0.2 0.2 0.2 1</ambient>
  <diffuse>1 0 0 1</diffuse>
  <specular>0 0 0 0</specular>
  <emissive>1 0 0 1</emissive>
  <shininess>0</shininess>
</material>
```

## Dynamic Objects and Spawning

### Dynamic Object (Interactive)

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <model name="small_sphere" static="false">
    <pose>2 2 1 0 0 0</pose>
    
    <link name="sphere_link">
      <visual>
        <geometry>
          <sphere radius="0.2"/>
        </geometry>
        <material>
          <ambient>0 0 1 1</ambient>
          <diffuse>0 0 1 1</diffuse>
          <specular>0.5 0.5 0.5 1</specular>
        </material>
      </visual>
      
      <collision>
        <surface>
          <friction>
            <ode>
              <mu>0.5</mu>
              <mu2>0.5</mu2>
            </ode>
          </friction>
          <bounce>
            <restitution_coefficient>0.2</restitution_coefficient>
            <threshold>0.05</threshold>
          </bounce>
        </surface>
        <geometry>
          <sphere radius="0.2"/>
        </geometry>
      </collision>
      
      <inertial>
        <mass value="1.0"/>
        <inertia ixx="0.01" ixy="0" ixz="0"
                 iyy="0.01" iyz="0"
                 izz="0.01"/>
      </inertial>
    </link>
  </model>
</sdf>
```

### Programmatic Spawning with Python

```python
import rclpy
from gazebo_msgs.srv import SpawnEntity, DeleteEntity
from geometry_msgs.msg import Pose
import os
from ament_index_python.packages import get_package_share_directory

class GazeboSpawner:
    """Programmatically spawn and delete objects in Gazebo"""
    
    def __init__(self):
        self.client = rclpy.create_node('gazebo_spawner')
        self.spawn_client = self.client.create_client(SpawnEntity, '/spawn_entity')
        self.delete_client = self.client.create_client(DeleteEntity, '/delete_entity')
        
        # Wait for services
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.client.get_logger().info('Waiting for spawn service...')
    
    def spawn_object(self, object_name, model_type='sphere', 
                    position=[0, 0, 1], size=0.1):
        """
        Spawn an object in Gazebo
        
        Args:
            object_name: Unique name for object
            model_type: 'sphere', 'box', 'cylinder'
            position: [x, y, z]
            size: Radius/side length
        """
        
        # Create SDF model string
        sdf_model = self._create_sdf_model(model_type, size)
        
        # Create request
        request = SpawnEntity.Request()
        request.name = object_name
        request.xml = sdf_model
        request.robot_namespace = ''
        request.initial_pose = Pose()
        request.initial_pose.position.x = float(position[0])
        request.initial_pose.position.y = float(position[1])
        request.initial_pose.position.z = float(position[2])
        
        # Send request
        future = self.spawn_client.call_async(request)
        rclpy.spin_until_future_complete(self.client, future)
        
        return future.result()
    
    def delete_object(self, object_name):
        """Delete object from Gazebo"""
        request = DeleteEntity.Request()
        request.name = object_name
        
        future = self.delete_client.call_async(request)
        rclpy.spin_until_future_complete(self.client, future)
        
        return future.result()
    
    def _create_sdf_model(self, model_type, size):
        """Create SDF model string"""
        
        if model_type == 'sphere':
            geometry = f'<sphere radius="{size}"/>'
        elif model_type == 'box':
            geometry = f'<box size="{size} {size} {size}"/>'
        elif model_type == 'cylinder':
            geometry = f'<cylinder radius="{size}" length="{size*2}"/>'
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        sdf = f"""<?xml version="1.0"?>
<sdf version="1.9">
  <model name="dynamic_object" static="false">
    <link name="link">
      <visual>
        <geometry>
          {geometry}
        </geometry>
        <material>
          <ambient>1 0 0 1</ambient>
          <diffuse>1 0 0 1</diffuse>
        </material>
      </visual>
      <collision>
        <geometry>
          {geometry}
        </geometry>
      </collision>
      <inertial>
        <mass value="1.0"/>
        <inertia ixx="0.01" ixy="0" ixz="0"
                 iyy="0.01" iyz="0"
                 izz="0.01"/>
      </inertial>
    </link>
  </model>
</sdf>"""
        return sdf
```

## Complex World Example: Robot Lab

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <world name="robot_lab">
    
    <!-- Physics engine -->
    <physics name="default_physics" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>
    
    <gravity>0 0 -9.81</gravity>
    
    <!-- Lighting -->
    <light name="overhead_light" type="directional">
      <intensity>1.0</intensity>
      <direction>-0.5 0.1 -0.9</direction>
      <cast_shadows>true</cast_shadows>
    </light>
    
    <light name="fill_light" type="point">
      <pose>0 0 5 0 0 0</pose>
      <intensity>0.5</intensity>
      <range>20</range>
    </light>
    
    <!-- Ground plane -->
    <model name="ground" static="true">
      <link name="ground_link">
        <collision>
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>50 50</size>
            </plane>
          </geometry>
        </collision>
        <visual>
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>50 50</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.8 0.8 0.8 1</ambient>
            <diffuse>0.8 0.8 0.8 1</diffuse>
          </material>
        </visual>
      </link>
    </model>
    
    <!-- Work table 1 -->
    <model name="work_table_1" static="true">
      <pose>5 5 0 0 0 0</pose>
      <link name="table_top">
        <pose>0 0 0.75 0 0 0</pose>
        <collision>
          <geometry>
            <box size="2 1 0.05"/>
          </geometry>
        </collision>
        <visual>
          <geometry>
            <box size="2 1 0.05"/>
          </geometry>
          <material>
            <ambient>0.5 0.3 0.1 1</ambient>
            <diffuse>0.5 0.3 0.1 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass value="50"/>
          <inertia ixx="5" ixy="0" ixz="0"
                   iyy="5" iyz="0"
                   izz="5"/>
        </inertial>
      </link>
      
      <!-- Four legs -->
      <link name="leg_fl">
        <pose>-0.8 -0.4 0.375 0 0 0</pose>
        <collision>
          <geometry>
            <box size="0.05 0.05 0.75"/>
          </geometry>
        </collision>
        <visual>
          <geometry>
            <box size="0.05 0.05 0.75"/>
          </geometry>
          <material>
            <ambient>0.3 0.3 0.3 1</ambient>
            <diffuse>0.3 0.3 0.3 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass value="5"/>
          <inertia ixx="0.1" ixy="0" ixz="0"
                   iyy="0.1" iyz="0"
                   izz="0.001"/>
        </inertial>
      </link>
      
      <joint name="leg_fl_joint" type="fixed">
        <parent>table_top</parent>
        <child>leg_fl</child>
      </joint>
      
      <!-- Additional legs would be similar -->
    </model>
    
    <!-- Obstacle wall -->
    <model name="obstacle_wall" static="true">
      <pose>10 0 0 0 0 0</pose>
      <link name="wall">
        <visual>
          <geometry>
            <box size="0.2 15 2"/>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
        <collision>
          <geometry>
            <box size="0.2 15 2"/>
          </geometry>
        </collision>
        <inertial>
          <mass value="100"/>
          <inertia ixx="50" ixy="0" ixz="0"
                   iyy="50" iyz="0"
                   izz="50"/>
        </inertial>
      </link>
    </model>
    
    <!-- Small objects for manipulation -->
    <model name="object_1" static="false">
      <pose>5 5 0.83 0 0 0</pose>
      <link name="link">
        <visual>
          <geometry>
            <box size="0.1 0.1 0.1"/>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
            <diffuse>1 0 0 1</diffuse>
          </material>
        </visual>
        <collision>
          <geometry>
            <box size="0.1 0.1 0.1"/>
          </geometry>
        </collision>
        <inertial>
          <mass value="0.5"/>
          <inertia ixx="0.0001" ixy="0" ixz="0"
                   iyy="0.0001" iyz="0"
                   izz="0.0001"/>
        </inertial>
      </link>
    </model>
    
  </world>
</sdf>
```

## Best Practices for World Design

1. **Use Appropriate Scale**: Match real-world dimensions
2. **Optimize Geometry**: Use primitive shapes when possible
3. **Define Clear Zones**: Designated areas for different tasks
4. **Realistic Lighting**: Match expected deployment conditions
5. **Material Properties**: Accurate friction and restitution
6. **Performance**: Minimize number of dynamic objects
7. **Documentation**: Comment world files for clarity

## Summary

Well-designed Gazebo worlds enable realistic testing of robot algorithms. Combining static infrastructure, dynamic objects, appropriate physics, and realistic lighting creates believable simulation environments for algorithm validation.

## Key Takeaways

- SDF format defines complete worlds (vs URDF for robots)
- Lighting and materials affect simulation perception
- Static vs dynamic objects have different computational costs
- Obstacles and structures make testing more realistic
- Python API enables programmatic environment creation
- Physics parameters must match intended test conditions