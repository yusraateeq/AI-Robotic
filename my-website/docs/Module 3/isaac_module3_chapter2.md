# Chapter 2: NVIDIA Isaac Sim - Photorealistic Simulation

## Introduction

NVIDIA Isaac Sim is a GPU-accelerated physics and photorealistic rendering engine designed specifically for robotics simulation. This chapter covers setting up Isaac Sim environments, configuring robots, and leveraging photorealistic rendering for synthetic data generation.

## What is Isaac Sim?

Isaac Sim is built on NVIDIA Omniverse and provides:

```
Isaac Sim Stack:
├── Omniverse Platform
│   ├── Collaborative features
│   ├── Asset browser
│   └── Multi-user support
├── Physics Engine
│   ├── PhysX GPU acceleration
│   ├── Multi-GPU support
│   └── Deterministic simulation
├── Rendering Engine
│   ├── Real-time ray tracing
│   ├── Accurate material simulation
│   └── Path tracing for offline renders
└── Sensor Simulation
    ├── RGB cameras
    ├── Depth sensors
    ├── LiDAR
    ├── Radar
    └── Thermal imaging
```

## Installation and Setup

### Installation Steps

```bash
# 1. Download NVIDIA Omniverse Launcher
# https://www.nvidia.com/en-us/omniverse/download/

# 2. Install Isaac Sim through Omniverse Launcher
# Approximate size: 50-100 GB
# Installation time: 30-60 minutes

# 3. Verify installation
isaac-sim --version

# 4. Launch Isaac Sim
isaac-sim

# 5. Install ROS 2 integration
# In Isaac Sim: Window → Extensions → Search "ros"
# Install: "ROS 2 Bridge" and "ROS 2 Humble Bridge"
```

### Project Structure

```
~/isaac_sim_projects/
├── environments/
│   ├── warehouse.usd
│   ├── factory.usd
│   └── home.usd
├── robots/
│   ├── humanoid_robot.usd
│   ├── mobile_manipulator.usd
│   └── quadruped.usd
├── tasks/
│   ├── navigation_task.py
│   ├── manipulation_task.py
│   └── exploration_task.py
├── datasets/
│   ├── synthetic_images/
│   ├── annotations/
│   └── metadata.json
└── scripts/
    ├── data_generation.py
    ├── sensor_config.py
    └── evaluation.py
```

## Creating Isaac Sim Environments

### Basic Scene Setup

```python
"""
Isaac Sim environment setup script
Run in Isaac Sim Python console or as standalone
"""

from isaacsim import SimulationApp

# Initialize simulation app
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
import numpy as np

class IsaacSimEnvironment:
    """Setup and manage Isaac Sim simulation"""
    
    def __init__(self):
        self.world = World(stage_units_in_meters=1.0)
        self.physics_context = self.world.get_physics_context()
        
        # Configure physics
        self.physics_context.set_gravity(np.array([0, 0, -9.81]))
        self.physics_context.set_solver_type("PGS")
        self.physics_context.enable_gpu_dynamics(True)
        
        # Physics timestep
        self.world.set_simulation_dt(0.01)  # 100 Hz
    
    def add_ground_plane(self):
        """Add ground plane to scene"""
        from omni.isaac.core.prims import XformPrim
        from pxr import UsdGeom, Gf
        
        # Create ground plane
        stage = self.world.stage
        ground_path = "/World/Ground"
        
        # Add ground prim
        ground = UsdGeom.Plane.Define(stage, ground_path)
        ground.GetSizeAttr().Set(200.0)  # 200m × 200m
        
        # Add physics
        from omni.physx.scripts import physicsUtils
        physicsUtils.add_rigid_body_if_not_exists(
            stage, ground_path, "static"
        )
        
        return ground_path
    
    def load_robot(self, robot_name, robot_path, position=[0, 0, 0.5]):
        """
        Load robot from URDF or USD
        
        Args:
            robot_name: Name for the robot in scene
            robot_path: Path to robot model (USD or URDF)
            position: Initial [x, y, z] position
        """
        from omni.isaac.core.robots import Robot
        
        # Add robot to stage
        robot_reference = add_reference_to_stage(
            usd_path=robot_path,
            prim_path=f"/World/{robot_name}"
        )
        
        # Create Robot wrapper for easier control
        robot = Robot(
            prim_path=f"/World/{robot_name}",
            name=robot_name,
            position=np.array(position)
        )
        
        return robot
    
    def add_lighting(self):
        """Configure scene lighting for photorealism"""
        from pxr import UsdLux, Gf
        
        stage = self.world.stage
        
        # Add directional light (sun)
        light_path = "/World/Lights/DirectionalLight"
        directional_light = UsdLux.DistantLight.Define(
            stage, light_path
        )
        directional_light.CreateIntensityAttr().Set(2.0)
        directional_light.CreateAngleAttr().Set(0.5)
        
        # Set light direction
        light_prim = stage.GetPrimAtPath(light_path)
        light_xform = light_prim.GetAttribute("xformOp:rotateXYZ")
        light_xform.Set(Gf.Vec3f(45, 45, 0))
        
        # Add fill light for better detail visibility
        fill_light_path = "/World/Lights/FillLight"
        fill_light = UsdLux.SphereLight.Define(
            stage, fill_light_path
        )
        fill_light.CreateIntensityAttr().Set(0.5)
        fill_light.CreateRadiusAttr().Set(5.0)
        
        # Position fill light
        fill_light_xform = fill_light.GetPrim().GetAttribute("xformOp:translate")
        fill_light_xform.Set(Gf.Vec3f(-5, 5, 3))
    
    def add_camera(self, camera_name, position, target):
        """
        Add camera to scene for visualization/rendering
        
        Args:
            camera_name: Name of camera
            position: Camera position [x, y, z]
            target: Look-at target [x, y, z]
        """
        from omni.isaac.core.cameras import Camera
        
        camera = Camera(
            prim_path=f"/World/Cameras/{camera_name}",
            position=np.array(position),
            target=np.array(target),
            resolution=(1280, 720)
        )
        
        return camera
    
    def step(self):
        """Step simulation"""
        self.world.step(render=True)
    
    def reset(self):
        """Reset simulation"""
        self.world.reset()

# Example usage
def main():
    env = IsaacSimEnvironment()
    env.add_ground_plane()
    env.add_lighting()
    
    # Load robot
    assets_root = get_assets_root_path()
    robot_path = f"{assets_root}/NVIDIA/Assets/Isaac/4.0/Isaac/Robots/Humanoids/H1/h1.usd"
    robot = env.load_robot("H1_Robot", robot_path)
    
    # Add observation camera
    camera = env.add_camera(
        "ViewCamera",
        position=[2, 2, 1.5],
        target=[0, 0, 0.5]
    )
    
    # Run simulation
    for frame in range(1000):
        env.step()

if __name__ == "__main__":
    main()
```

## Advanced Scene Configuration

### Material and Rendering Properties

```python
"""
Configure photorealistic materials in Isaac Sim
"""

from pxr import Usd, UsdShade, Sdf
import numpy as np

class MaterialConfig:
    """Configure materials for photorealism"""
    
    @staticmethod
    def create_pbr_material(stage, material_name, properties):
        """
        Create Physically Based Rendering (PBR) material
        
        Args:
            stage: USD stage
            material_name: Name for material
            properties: Dict with 'albedo', 'metallic', 'roughness'
        """
        # Create material path
        material_path = f"/World/Materials/{material_name}"
        
        # Create shader
        material = UsdShade.Material.Define(stage, material_path)
        pbrShader = UsdShade.Shader.Define(
            stage,
            f"{material_path}/Shader"
        )
        
        # Set shader type (USD Preview Surface)
        pbrShader.CreateIdAttr().Set("UsdPreviewSurface")
        
        # Set properties
        albedo = properties.get('albedo', [0.5, 0.5, 0.5])
        pbrShader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
            tuple(albedo)
        )
        
        metallic = properties.get('metallic', 0.0)
        pbrShader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(metallic)
        
        roughness = properties.get('roughness', 0.5)
        pbrShader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(roughness)
        
        # Connect shader to material
        material.CreateSurfaceOutput().ConnectToSource(
            pbrShader.ConnectableAPI(), "surface"
        )
        
        return material_path
    
    @staticmethod
    def apply_material_to_prim(prim, material_path):
        """Apply material to a primitive"""
        rel = prim.CreateRelationship(
            UsdShade.Tokens.materialBinding
        )
        rel.AddTarget(material_path)

class RobotVisualConfig:
    """Configure realistic robot appearance"""
    
    # Material presets
    MATERIALS = {
        'metal_joint': {
            'albedo': [0.2, 0.2, 0.2],
            'metallic': 0.9,
            'roughness': 0.3
        },
        'white_plastic': {
            'albedo': [0.9, 0.9, 0.9],
            'metallic': 0.0,
            'roughness': 0.5
        },
        'black_rubber': {
            'albedo': [0.05, 0.05, 0.05],
            'metallic': 0.0,
            'roughness': 0.8
        },
        'carbon_fiber': {
            'albedo': [0.15, 0.15, 0.15],
            'metallic': 0.3,
            'roughness': 0.2
        }
    }
    
    @classmethod
    def configure_humanoid(cls, stage, robot_prim_path):
        """
        Configure realistic appearance for humanoid robot
        """
        # Apply different materials to different body parts
        body_materials = {
            'torso': 'white_plastic',
            'arm': 'white_plastic',
            'joint': 'metal_joint',
            'foot': 'black_rubber'
        }
        
        for part_name, material_name in body_materials.items():
            material_props = cls.MATERIALS[material_name]
            material_path = MaterialConfig.create_pbr_material(
                stage, f"{part_name}_material", material_props
            )
            
            # Apply to all links with this keyword
            for prim in stage.Traverse():
                if part_name in prim.GetName().lower():
                    MaterialConfig.apply_material_to_prim(
                        prim, material_path
                    )
```

### Physics Configuration for Realism

```python
"""
Configure physics for realistic robot behavior
"""

class PhysicsConfig:
    """Advanced physics configuration for Isaac Sim"""
    
    def __init__(self, world):
        self.world = world
        self.physics_context = world.get_physics_context()
    
    def configure_for_humanoid(self):
        """
        Optimize physics for bipedal humanoid simulation
        """
        # Solver settings for stability
        self.physics_context.set_solver_type("TGS")  # Tesla GPU Solver
        self.physics_context.set_gravity(np.array([0, 0, -9.81]))
        
        # Increase iterations for stability
        self.physics_context.set_default_physics_dt(0.00667)  # 150 Hz
        self.physics_context.enable_gpu_dynamics(True)
        
        # Contact settings
        self.physics_context.set_contact_offset(0.001)
        self.physics_context.set_rest_offset(0.0)
        
        # Broadcast enabled for dynamics
        self.physics_context.enable_gpu_dynamical_state_broadcast(True)
    
    def configure_friction_table(self):
        """
        Configure friction between different material pairs
        Critical for realistic manipulation and walking
        """
        friction_table = {
            ('rubber', 'concrete'): 0.8,
            ('rubber', 'wood'): 0.7,
            ('metal', 'metal'): 0.15,
            ('plastic', 'plastic'): 0.3,
            ('gripper', 'object'): 0.6
        }
        
        return friction_table
    
    def set_link_properties(self, prim_path, mass, friction, restitution):
        """
        Set physics properties for a rigid body
        
        Args:
            prim_path: Path to the prim
            mass: Mass in kg
            friction: Friction coefficient
            restitution: Bounciness (0-1)
        """
        from omni.physx.scripts import physicsUtils
        
        stage = self.world.stage
        prim = stage.GetPrimAtPath(prim_path)
        
        # Set mass
        physicsUtils.setRigidBodyMass(stage, prim_path, mass)
        
        # Set friction
        physicsUtils.setColliderProperties(
            stage, prim_path,
            friction=friction,
            restitution=restitution
        )
```

## Sensor Configuration

### Camera Sensor Setup

```python
"""
Configure realistic camera sensors in Isaac Sim
"""

from omni.isaac.sensor import Camera
import numpy as np

class CameraConfig:
    """Configure RGB and depth cameras"""
    
    @staticmethod
    def create_rgb_camera(
        world, 
        camera_name, 
        position, 
        resolution=(1280, 720),
        fov=60.0
    ):
        """
        Create RGB camera with realistic properties
        
        Args:
            world: Isaac Sim world
            camera_name: Name for camera
            position: Camera position [x, y, z]
            resolution: Image resolution (width, height)
            fov: Horizontal field of view (degrees)
        """
        camera = Camera(
            prim_path=f"/World/Sensors/{camera_name}",
            resolution=resolution,
            position=np.array(position),
            frequency=30
        )
        
        # Configure camera intrinsics
        camera.set_focal_length(1.0)
        camera.set_horizontal_aperture(fov)
        
        return camera
    
    @staticmethod
    def create_depth_camera(
        world,
        camera_name,
        position,
        resolution=(640, 480),
        near_plane=0.1,
        far_plane=10.0
    ):
        """Create depth (RGB-D) camera"""
        from omni.isaac.sensor import Camera
        
        camera = Camera(
            prim_path=f"/World/Sensors/{camera_name}",
            resolution=resolution,
            position=np.array(position),
            frequency=30,
            depth=True  # Enable depth output
        )
        
        # Set depth range
        camera.set_clipping_range(near_plane, far_plane)
        
        return camera

class LiDARConfig:
    """Configure LiDAR sensor simulation"""
    
    @staticmethod
    def create_lidar(
        world,
        lidar_name,
        position,
        num_beams=64,
        rotation_rate=10,  # Hz
        range_max=100.0
    ):
        """
        Create LiDAR sensor
        
        Args:
            world: Isaac Sim world
            lidar_name: Name for LiDAR
            position: Sensor position [x, y, z]
            num_beams: Number of laser beams
            rotation_rate: Rotation frequency
            range_max: Maximum range in meters
        """
        from omni.isaac.sensor import RotatingLidar
        
        lidar = RotatingLidar(
            prim_path=f"/World/Sensors/{lidar_name}",
            position=np.array(position),
            name=lidar_name,
            frequency=rotation_rate,
            channels=num_beams,
            max_range=range_max,
            min_range=0.1
        )
        
        return lidar
```

## Deterministic Simulation for Training

```python
"""
Deterministic simulation for reproducible training
"""

class DeterministicSimulation:
    """Ensure reproducible simulation for training"""
    
    def __init__(self, world, seed=42):
        self.world = world
        self.seed = seed
        self._set_determinism()
    
    def _set_determinism(self):
        """Configure for deterministic behavior"""
        from omni.physx import get_physx_interface
        
        physx = get_physx_interface()
        
        # Enable deterministic mode
        physx.enable_deterministic_solver(True)
        
        # Set random seed
        np.random.seed(self.seed)
        
        # GPU-accelerated physics (deterministic)
        self.world.get_physics_context().enable_gpu_dynamics(True)
    
    def get_state(self):
        """Get complete simulation state"""
        return {
            'time': self.world.current_time,
            'frame': self.world.current_time_step_index
        }
    
    def reset_to_state(self, state):
        """Reset to saved state"""
        # Isaac Sim state management
        self.world.reset()
```

## Integration with ROS 2

```python
"""
Setup ROS 2 bridge for Isaac Sim
"""

class IsaacSimROS2Bridge:
    """Bridge between Isaac Sim and ROS 2"""
    
    def __init__(self, world):
        self.world = world
        self._setup_ros_bridge()
    
    def _setup_ros_bridge(self):
        """Initialize ROS 2 communication"""
        # ROS 2 bridge is typically configured via UI
        # Or use the following programmatic approach:
        
        try:
            import rosgraph
            # Check if ROS 2 master is running
            self.ros_available = True
        except:
            self.ros_available = False
            print("Warning: ROS 2 not available")
    
    def publish_joint_states(self, robot):
        """
        Publish joint states to ROS 2
        Topic: /joint_states
        """
        if not self.ros_available:
            return
        
        # Get joint positions
        joint_positions = robot.get_joint_positions()
        joint_velocities = robot.get_joint_velocities()
        
        # Publish via ROS 2 (requires ros_bridge configuration)
```

## Performance Optimization

### GPU Memory Management

```python
"""
Optimize GPU memory usage in Isaac Sim
"""

class GPUOptimization:
    """Optimize GPU usage for large-scale simulations"""
    
    @staticmethod
    def enable_gpu_dynamics(world):
        """Enable GPU-accelerated dynamics"""
        physics_context = world.get_physics_context()
        physics_context.enable_gpu_dynamics(True)
        physics_context.enable_gpu_dynamical_state_broadcast(True)
    
    @staticmethod
    def configure_for_scale(num_robots, num_objects):
        """
        Configure for large-scale multi-agent simulation
        
        For example: 100 robots, 1000 objects
        """
        # Allocate GPU memory appropriately
        total_elements = num_robots + num_objects
        
        if total_elements > 10000:
            # Use streaming mode
            pass
        else:
            # Standard mode
            pass
    
    @staticmethod
    def profile_performance():
        """Profile Isaac Sim performance"""
        import time
        
        metrics = {
            'fps': 0,
            'frame_time': 0,
            'gpu_memory': 0,
            'cpu_time': 0
        }
        
        return metrics
```

## Summary

NVIDIA Isaac Sim provides a powerful platform for photorealistic robot simulation with GPU acceleration. Its tight integration with modern rendering techniques and physics engines makes it ideal for generating training data and validating algorithms before deployment.

## Key Takeaways

- Isaac Sim offers photorealistic rendering crucial for synthetic data generation
- GPU acceleration enables real-time simulation of complex scenes
- Deterministic simulation ensures reproducibility for training
- Configurable materials and physics enable realistic behavior
- ROS 2 integration provides seamless connection to control algorithms
- Multiple sensor simulation supports diverse perception tasks
- High-fidelity data generation bridges simulation-to-reality gap