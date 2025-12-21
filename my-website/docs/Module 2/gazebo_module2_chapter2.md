# Chapter 2: Gazebo Physics Simulation

## Introduction

Gazebo provides accurate physics simulation essential for testing robot algorithms before deployment to hardware. This chapter covers the fundamentals of physics simulation, gravity, collisions, and friction in Gazebo.

## Physics Engines in Gazebo

### Available Physics Engines

#### ODE (Open Dynamics Engine)
- **Pros**: Well-established, good stability, many features
- **Cons**: Slower computation, less accurate contact modeling
- **Best for**: Stable simulations with moderate accuracy needs

#### Bullet
- **Pros**: Fast, robust, good contact handling
- **Cons**: Less comprehensive than ODE
- **Best for**: Real-time performance requirements

#### DART (Dynamic Animation and Robotics Toolkit)
- **Pros**: Highly accurate, excellent contact modeling, fast
- **Cons**: Less established than ODE
- **Best for**: Research requiring high accuracy

#### Simbody
- **Pros**: Accurate constraint handling, good for biomechanics
- **Cons**: Slower, less commonly used
- **Best for**: Humanoid and biomechanical systems

### Selecting a Physics Engine

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <world name="test_world">
    <!-- Set physics engine -->
    <physics name="default_physics" type="ode">
      <!-- Engine-specific parameters -->
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>
  </world>
</sdf>
```

## Understanding Gravity

### Basic Gravity Setup

Gravity in Gazebo affects all objects with mass:

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <world name="gravity_world">
    <!-- Default Earth gravity -->
    <gravity>0 0 -9.81</gravity>
    
    <!-- Alternative: Moon gravity -->
    <!-- <gravity>0 0 -1.62</gravity> -->
    
    <!-- Alternative: No gravity (space simulation) -->
    <!-- <gravity>0 0 0</gravity> -->
  </world>
</sdf>
```

### Gravity Effects in Robotics

```
┌─────────────────────────────────────────┐
│         Object with Mass (m)            │
└────────────────┬────────────────────────┘
                 │
      Gravity Force = m × g
      (direction: downward)
                 │
        ┌────────▼────────┐
        │                 │
     ┌──▼──┐        ┌─────▼───┐
     │ARM  │        │ TORSO   │
     │MASS │        │ WEIGHT  │
     └─────┘        └─────────┘
        │                 │
    Weight acts as:    - Affects balance
    - Requires joint   - Impacts stability
      torque to lift   - Critical for walking
    - Creates friction - Load on servos
```

### Compensating for Gravity in Control

```python
import numpy as np

class GravityCompensator:
    """Compensate for gravity in joint commands"""
    
    def __init__(self, robot_params):
        self.masses = robot_params['link_masses']
        self.centers_of_mass = robot_params['centers_of_mass']
        self.joint_axes = robot_params['joint_axes']
        self.gravity = 9.81
    
    def compute_gravity_torque(self, joint_angles):
        """
        Compute torque needed to counteract gravity
        This is essential for accurate control in simulation
        """
        gravity_torques = []
        
        for i, angle in enumerate(joint_angles):
            # Calculate potential energy gradient
            torque = 0.0
            for j in range(i, len(self.masses)):
                # Project mass and distance onto joint axis
                mass = self.masses[j]
                com = self.centers_of_mass[j]
                axis = self.joint_axes[i]
                
                # Gravity torque = m * g * r * sin(theta)
                # Where r is perpendicular distance to gravity
                r = np.linalg.norm(com)
                torque += mass * self.gravity * r
            
            gravity_torques.append(torque)
        
        return np.array(gravity_torques)
```

## Collision Detection and Response

### Understanding Collisions

In Gazebo, collision detection involves:

1. **Broad Phase**: Identify potentially colliding pairs (AABB)
2. **Narrow Phase**: Compute exact contact points
3. **Contact Response**: Apply forces based on material properties

```
Object A          Object B
  ┌────────┐        ┌────────┐
  │ URDF   │        │ URDF   │
  │ Link   │        │ Link   │
  └────┬───┘        └───┬────┘
       │                │
  ┌────▼────────────────▼────┐
  │  Collision Geometry       │
  │  (Bounding Volume)        │
  └────┬────────────────┬────┘
       │                │
  ┌────▼─────────┬─────▼────┐
  │ Broad Phase  │ AABB Test│
  │ Detection    └────┬─────┘
  │                   │
  │             Collision?
  │              Yes▼ No▼
  │                │   └─→ No Response
  │                │
  │          ┌─────▼──────────┐
  │          │ Narrow Phase   │
  │          │ Contact Points │
  │          └──────┬─────────┘
  │                 │
  │          ┌──────▼──────────┐
  │          │ Contact Response│
  │          │ Forces & Torques│
  │          └────────────────┘
  └──────────────────────────────┘
```

### Defining Collision Geometry

Collision geometry is usually simpler than visual geometry:

```xml
<?xml version="1.0"?>
<robot name="collision_example">
  
  <link name="gripper_finger">
    <!-- Visual geometry: detailed mesh -->
    <visual>
      <geometry>
        <mesh filename="package://robot/meshes/finger_detailed.stl"/>
      </geometry>
    </visual>
    
    <!-- Collision geometry: simplified primitive -->
    <collision>
      <geometry>
        <box size="0.02 0.01 0.1"/>
      </geometry>
    </collision>
    
    <!-- Inertial properties -->
    <inertial>
      <mass value="0.1"/>
      <inertia ixx="0.001" ixy="0" ixz="0"
               iyy="0.001" iyz="0"
               izz="0.00001"/>
    </inertial>
  </link>

</robot>
```

### Contact Properties

Contact behavior is determined by material properties:

```xml
<?xml version="1.0"?>
<robot name="contact_properties">
  
  <link name="gripper_pad">
    <collision>
      <geometry>
        <box size="0.05 0.05 0.01"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.2"/>
      <inertia ixx="0.0001" ixy="0" ixz="0"
               iyy="0.0001" iyz="0"
               izz="0.0001"/>
    </inertial>
  </link>

</robot>

<!-- In world file or SDF: -->
<gazebo reference="gripper_pad">
  <!-- Friction coefficients -->
  <mu1>0.8</mu1>      <!-- Static friction -->
  <mu2>0.6</mu2>      <!-- Kinetic friction -->
  
  <!-- Restitution (bounciness) -->
  <restitution_coefficient>0.1</restitution_coefficient>
  
  <!-- Bounce threshold -->
  <bounce_threshold>0.1</bounce_threshold>
  
  <!-- Surface properties -->
  <contact>
    <collide_bitmask>0xFFFF</collide_bitmask>
  </contact>
</gazebo>
```

### Friction Modeling

Friction is critical for manipulation and locomotion:

#### Static vs Kinetic Friction

```python
class FrictionModel:
    """
    Friction model for Gazebo simulation
    
    Types:
    1. Coulomb Friction: f = μ * N (most common)
    2. Viscous Friction: f = c * v
    3. Combined: f_total = μ * N + c * v
    """
    
    def __init__(self, mu_static=0.8, mu_kinetic=0.6, viscosity=0.1):
        self.mu_s = mu_static
        self.mu_k = mu_kinetic
        self.c = viscosity  # viscous damping coefficient
    
    def compute_friction_force(self, normal_force, velocity):
        """
        Compute friction force given normal force and velocity
        
        Args:
            normal_force: Normal contact force (N)
            velocity: Sliding velocity (m/s)
        
        Returns:
            Friction force magnitude
        """
        # Maximum static friction
        f_max_static = self.mu_s * normal_force
        
        # Kinetic friction
        f_kinetic = self.mu_k * normal_force
        
        # Viscous component
        f_viscous = self.c * abs(velocity)
        
        # Total friction (simplified)
        if abs(velocity) < 1e-6:  # Nearly static
            return f_max_static
        else:
            return f_kinetic + f_viscous
    
    def friction_cone_constraint(self, normal_force, tangential_limit=None):
        """
        Friction cone: |F_t| <= μ * F_n
        This ensures friction stays within physical limits
        """
        if tangential_limit is None:
            tangential_limit = self.mu_k * normal_force
        return tangential_limit
```

#### Friction Parameters for Common Materials

| Material | μ_static | μ_kinetic | Use Case |
|----------|----------|-----------|----------|
| Rubber on Concrete | 0.7-1.0 | 0.5-0.8 | Wheel traction |
| Metal on Metal | 0.15-0.25 | 0.1-0.2 | Joint lubricated |
| Rubber on Metal | 0.4-0.8 | 0.3-0.6 | Gripper pads |
| Plastic on Plastic | 0.2-0.4 | 0.15-0.3 | Sliding parts |
| Wood on Wood | 0.3-0.5 | 0.2-0.4 | Object surfaces |

## Physics Simulation Parameters

### Time Step Configuration

```xml
<?xml version="1.0"?>
<sdf version="1.9">
  <world name="physics_config">
    <physics name="default_physics" type="ode">
      <!-- Integration time step (critical parameter) -->
      <max_step_size>0.001</max_step_size>  <!-- 1ms steps -->
      
      <!-- Real-time factor -->
      <real_time_factor>1.0</real_time_factor>  <!-- 1.0 = real-time -->
      
      <!-- Update rate (Hz) -->
      <real_time_update_rate>1000</real_time_update_rate>  <!-- 1000 Hz -->
      
      <!-- Solver iterations (more = more accurate, slower) -->
      <iterations>50</iterations>
      
      <!-- ODE-specific parameters -->
      <ode>
        <solver type="world"/>
        <constraints>
          <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
          <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
      </ode>
    </physics>
  </world>
</sdf>
```

### Understanding Time Step Parameters

```
Real-world scenario:
  Real Time: t = 5.0 seconds
  Wall Clock: ~5 seconds elapsed

Simulation with real_time_factor = 1.0:
  Simulation Time: 5.0 seconds
  Wall Clock: ~5 seconds elapsed
  → Matches real-time (good for control testing)

Simulation with real_time_factor = 2.0:
  Simulation Time: 5.0 seconds
  Wall Clock: ~2.5 seconds elapsed
  → Runs 2× faster (good for data collection)

Simulation with real_time_factor = 0.1:
  Simulation Time: 5.0 seconds
  Wall Clock: ~50 seconds elapsed
  → Runs 10× slower (good for detailed analysis)
```

### Choosing Time Step

```python
"""
Time step selection guidelines:

1. Controller Update Rate:
   - If controller runs at 100 Hz → max_step_size ≤ 0.01 s
   - If controller runs at 1000 Hz → max_step_size ≤ 0.001 s

2. Accuracy vs Speed Trade-off:
   - Smaller steps: More accurate, slower
   - Larger steps: Less accurate, faster
   
3. Stability:
   - Too large: Simulation becomes unstable
   - Too small: Unnecessary computation
   
4. Recommended:
   - Robotic control: 0.001 - 0.01 s (1-10 ms)
   - Manipulation: 0.001 s (1 ms)
   - Humanoid walking: 0.002 - 0.005 s (2-5 ms)
"""

class PhysicsParameterSelector:
    @staticmethod
    def get_recommended_params(control_freq_hz):
        """Get recommended physics parameters for control frequency"""
        # Time step should be at least 2-5× smaller than control period
        dt = 1.0 / control_freq_hz
        max_step = dt / 5.0  # Use 5× higher physics rate
        
        return {
            'max_step_size': max_step,
            'real_time_factor': 1.0,
            'real_time_update_rate': 1.0 / max_step,
            'iterations': 50 if control_freq_hz <= 100 else 100
        }
```

## Contact and Collision Dynamics

### Advanced Contact Modeling

```python
class ContactDynamicsModel:
    """
    Model contact dynamics between two objects
    """
    
    def __init__(self):
        self.gravity = 9.81
    
    def sliding_velocity(self, v_relative, friction_coeff, normal_force):
        """
        Compute velocity after friction is applied
        
        F_friction = -μ * N * sign(v_relative)
        a = F_friction / m
        v_new = v_old + a * dt
        """
        # Friction decelerates motion
        max_friction_decel = friction_coeff * self.gravity
        return v_relative * max(0, 1 - max_friction_decel)
    
    def restitution_bounce(self, v_impact, restitution_coeff):
        """
        Velocity after bounce
        e = v_after / v_before
        """
        return -restitution_coeff * v_impact
```

## Debugging Physics Issues

### Common Physics Problems

#### Problem 1: Objects Falling Through Surfaces
```xml
<!-- Solution: Reduce time step or increase solver iterations -->
<physics name="default_physics" type="ode">
  <max_step_size>0.0005</max_step_size>  <!-- Smaller step -->
  <iterations>100</iterations>            <!-- More iterations -->
  <ode>
    <constraints>
      <contact_surface_layer>0.0005</contact_surface_layer>
    </constraints>
  </ode>
</physics>
```

#### Problem 2: Unstable Stacking
```xml
<!-- Solution: Increase damping and friction -->
<gazebo reference="block">
  <mu1>0.9</mu1>
  <mu2>0.7</mu2>
  <restitution_coefficient>0.0</restitution_coefficient>  <!-- No bounce -->
</gazebo>
```

#### Problem 3: Oscillating Joints
```python
# Solution: Tune damping in URDF
class JointDamping:
    """
    Joint damping helps stabilize motion
    f_damping = -b * velocity
    
    Too high: Sluggish, unresponsive
    Too low: Oscillates, instable
    """
    
    @staticmethod
    def recommend_damping(mass, stiffness, desired_damping_ratio=0.7):
        """
        Critical damping: b_c = 2 * sqrt(k * m)
        Recommended: b = damping_ratio * b_c
        """
        import math
        b_critical = 2 * math.sqrt(stiffness * mass)
        b_recommended = desired_damping_ratio * b_critical
        return b_recommended
```

## Physics Validation and Testing

### Comparing Simulation to Reality

```python
import numpy as np

class PhysicsValidator:
    """Validate simulation against real-world measurements"""
    
    def __init__(self):
        self.tolerance = 0.05  # 5% tolerance
    
    def validate_object_drop(self, sim_time, sim_final_height, 
                            real_time, real_final_height):
        """
        Validate free fall behavior
        Real: h = h0 - 0.5 * g * t^2
        Sim should match closely
        """
        # Theoretical fall distance
        g = 9.81
        theoretical_fall = 0.5 * g * sim_time**2
        
        # Compare simulated vs theoretical
        sim_error = abs(sim_final_height - 
                       (1.0 - theoretical_fall))
        
        # Compare simulated vs real
        sim_real_error = abs(sim_final_height - real_final_height)
        
        return {
            'theoretical_match': sim_error < self.tolerance,
            'reality_match': sim_real_error < self.tolerance,
            'sim_error_pct': sim_error * 100,
            'real_error_pct': sim_real_error * 100
        }
    
    def validate_friction(self, sim_decel, theoretical_decel, 
                         material_friction):
        """
        Validate friction model
        Deceleration = friction * g
        """
        decel_error = abs(sim_decel - theoretical_decel) / theoretical_decel
        return decel_error < self.tolerance
```

## Summary

Gazebo physics simulation provides accurate dynamics modeling essential for robot development. Understanding gravity effects, collision detection, friction, and physics parameters enables effective simulation-to-reality transfer.

## Key Takeaways

- Physics engines (ODE, Bullet, DART) each have strengths for different scenarios
- Gravity must be compensated in control algorithms
- Collision detection involves broad and narrow phases
- Friction modeling (static/kinetic) is crucial for manipulation
- Time step selection balances accuracy and computational cost
- Physics parameters must be tuned and validated against reality
- Proper contact properties prevent simulation artifacts