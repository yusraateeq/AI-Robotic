# Chapter 3: Bridging Python Agents to ROS Controllers

## Introduction

This chapter explores how to integrate Python-based AI agents with ROS 2 controllers. We'll create a bridge that allows high-level decision-making (agents) to communicate with low-level hardware control (ROS controllers). This is essential for building intelligent robotic systems.

## Architecture Overview

```
┌─────────────────────────────────┐
│   Python AI/ML Agent Layer      │
│  (Decision Making & Planning)   │
└──────────────┬──────────────────┘
               │ (High-level commands)
┌──────────────▼──────────────────┐
│  Python ROS 2 Bridge Node       │
│  (Translation & Coordination)   │
└──────────────┬──────────────────┘
               │ (Standard ROS messages)
┌──────────────▼──────────────────┐
│   ROS 2 Controllers             │
│  (Motor/Actuator Control)       │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│   Hardware (Motors, Sensors)    │
└─────────────────────────────────┘
```

## Part 1: Understanding the Bridge Pattern

### Why We Need a Bridge

1. **Abstraction**: Agents work at higher levels of abstraction
2. **Translation**: Convert agent commands to controller messages
3. **State Management**: Track robot state and provide it to agents
4. **Error Handling**: Handle communication failures gracefully
5. **Rate Conversion**: Convert between different communication frequencies

### Bridge Responsibilities

- Receive commands from the agent
- Validate commands for safety
- Convert to appropriate ROS messages
- Send to controllers
- Monitor controller status
- Report feedback to agent

## Part 2: Building an Agent-Controller Bridge

### Simple Bridge Node

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32

class RobotBridge(Node):
    def __init__(self):
        super().__init__('robot_bridge')
        
        # Publishers to controllers
        self.cmd_vel_pub = self.create_publisher(
            Twist, '/cmd_vel', 10
        )
        self.joint_cmd_pub = self.create_publisher(
            JointState, '/joint_commands', 10
        )
        
        # Subscribers from sensors
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        
        # State storage
        self.current_joint_states = None
        self.get_logger().info('Robot bridge initialized')
    
    def joint_state_callback(self, msg):
        """Receive joint states from controllers"""
        self.current_joint_states = msg
        self.get_logger().debug(f'Joint states: {msg.name}')
    
    def move_forward(self, linear_speed):
        """Command movement forward"""
        cmd = Twist()
        cmd.linear.x = linear_speed
        self.cmd_vel_pub.publish(cmd)
    
    def move_rotate(self, angular_speed):
        """Command rotation"""
        cmd = Twist()
        cmd.angular.z = angular_speed
        self.cmd_vel_pub.publish(cmd)
    
    def command_joints(self, positions):
        """Command joint positions"""
        cmd = JointState()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.name = ['joint_1', 'joint_2', 'joint_3']
        cmd.position = positions
        self.joint_cmd_pub.publish(cmd)
    
    def get_joint_states(self):
        """Get current joint states"""
        return self.current_joint_states

def main(args=None):
    rclpy.init(args=args)
    bridge = RobotBridge()
    rclpy.spin(bridge)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Advanced Bridge with Safety Validation

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
import numpy as np

class SafeRobotBridge(Node):
    def __init__(self):
        super().__init__('safe_robot_bridge')
        
        # Define safety limits
        self.max_linear_speed = 1.0  # m/s
        self.max_angular_speed = 1.5  # rad/s
        self.max_joint_speed = 2.0  # rad/s
        self.joint_limits = {
            'shoulder': (-3.14, 3.14),
            'elbow': (-2.0, 2.0),
            'wrist': (-3.14, 3.14)
        }
        
        # Publishers and subscribers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.joint_cmd_pub = self.create_publisher(JointState, '/joint_commands', 10)
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10
        )
        
        self.current_state = None
    
    def validate_velocity(self, linear, angular):
        """Validate velocity commands"""
        if abs(linear) > self.max_linear_speed:
            self.get_logger().warn(f'Linear speed {linear} exceeds limit {self.max_linear_speed}')
            linear = np.sign(linear) * self.max_linear_speed
        
        if abs(angular) > self.max_angular_speed:
            self.get_logger().warn(f'Angular speed {angular} exceeds limit {self.max_angular_speed}')
            angular = np.sign(angular) * self.max_angular_speed
        
        return linear, angular
    
    def validate_joint_positions(self, positions, joint_names):
        """Validate joint positions against limits"""
        validated = []
        for name, pos in zip(joint_names, positions):
            if name in self.joint_limits:
                min_pos, max_pos = self.joint_limits[name]
                if pos < min_pos or pos > max_pos:
                    self.get_logger().warn(
                        f'Joint {name} position {pos} out of limits [{min_pos}, {max_pos}]'
                    )
                    pos = np.clip(pos, min_pos, max_pos)
            validated.append(pos)
        return validated
    
    def safe_move(self, linear, angular):
        """Safe velocity command"""
        linear, angular = self.validate_velocity(linear, angular)
        cmd = Twist()
        cmd.linear.x = linear
        cmd.angular.z = angular
        self.cmd_vel_pub.publish(cmd)
    
    def safe_joint_command(self, positions, joint_names):
        """Safe joint command"""
        positions = self.validate_joint_positions(positions, joint_names)
        cmd = JointState()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.name = joint_names
        cmd.position = positions
        self.joint_cmd_pub.publish(cmd)
    
    def joint_state_callback(self, msg):
        self.current_state = msg

def main(args=None):
    rclpy.init(args=args)
    bridge = SafeRobotBridge()
    rclpy.spin(bridge)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Part 3: Integration with AI Agents

### Agent-Bridge Communication Pattern

```python
from rclpy.node import Node
from std_srvs.srv import Empty
import numpy as np

class IntelligentAgent(Node):
    """Base class for AI agents controlling robots"""
    
    def __init__(self, bridge_node):
        super().__init__('intelligent_agent')
        self.bridge = bridge_node
        self.state_history = []
        self.action_history = []
    
    def perceive(self):
        """Get current robot state from bridge"""
        state = {
            'joint_states': self.bridge.get_joint_states(),
            'timestamp': self.get_clock().now().nanoseconds
        }
        self.state_history.append(state)
        return state
    
    def decide(self, state):
        """Agent decision-making logic (override in subclasses)"""
        raise NotImplementedError("Subclasses must implement decide()")
    
    def act(self, action):
        """Execute action through bridge"""
        action_type = action.get('type')
        
        if action_type == 'move':
            self.bridge.safe_move(
                action['linear_speed'],
                action['angular_speed']
            )
        elif action_type == 'joint':
            self.bridge.safe_joint_command(
                action['positions'],
                action['joint_names']
            )
        
        self.action_history.append(action)
    
    def control_loop(self):
        """Main agent control loop"""
        state = self.perceive()
        action = self.decide(state)
        self.act(action)
```

### Example: Reaching Agent

```python
import numpy as np
from rclpy.node import Node

class ReachingAgent(IntelligentAgent):
    """Agent that reaches to target positions"""
    
    def __init__(self, bridge_node):
        super().__init__(bridge_node)
        self.target_position = np.array([0.5, 0.5, 0.3])  # x, y, z
        self.learning_rate = 0.1
    
    def decide(self, state):
        """Simple reaching logic"""
        joint_states = state['joint_states']
        
        if joint_states is None:
            return {'type': 'wait'}
        
        # Simple proportional controller
        current_positions = np.array(joint_states.position)
        target_positions = self.target_position
        
        # Compute error
        error = target_positions - current_positions[:3]
        
        # Scale for joint commands
        action = {
            'type': 'joint',
            'positions': list(current_positions[:3] + self.learning_rate * error),
            'joint_names': ['shoulder', 'elbow', 'wrist']
        }
        
        return action
```

## Part 4: Multi-Rate Control

### Handling Different Update Frequencies

```python
from rclpy.node import Node
from rclpy.timer import Timer

class MultiRateController(Node):
    """Handles nodes running at different frequencies"""
    
    def __init__(self):
        super().__init__('multi_rate_controller')
        
        # High-rate control loop (100 Hz)
        self.control_timer = self.create_timer(0.01, self.control_callback)
        
        # Medium-rate sensing (50 Hz)
        self.sense_timer = self.create_timer(0.02, self.sense_callback)
        
        # Low-rate decision making (10 Hz)
        self.decision_timer = self.create_timer(0.1, self.decision_callback)
        
        # State buffers
        self.sensor_data = None
        self.desired_action = None
    
    def sense_callback(self):
        """Acquire sensor data (50 Hz)"""
        # Read sensors through bridge
        self.sensor_data = self.read_sensors()
    
    def decision_callback(self):
        """Make high-level decisions (10 Hz)"""
        if self.sensor_data is None:
            return
        # Agent makes decision based on sensor data
        self.desired_action = self.agent.decide(self.sensor_data)
    
    def control_callback(self):
        """Execute control commands (100 Hz)"""
        if self.desired_action is None:
            return
        # Send desired action to hardware
        self.send_command(self.desired_action)
    
    def read_sensors(self):
        # Implementation
        pass
    
    def send_command(self, action):
        # Implementation
        pass
```

## Part 5: Example: Complete System

### Putting It All Together

```python
import rclpy
from rclpy.node import Node

class CompleteRobotSystem(Node):
    def __init__(self):
        super().__init__('complete_robot_system')
        
        # Initialize bridge
        from safe_robot_bridge import SafeRobotBridge
        self.bridge = SafeRobotBridge()
        
        # Initialize agent
        from reaching_agent import ReachingAgent
        self.agent = ReachingAgent(self.bridge)
        
        # Main control loop at 10 Hz
        self.control_loop_timer = self.create_timer(0.1, self.main_loop)
    
    def main_loop(self):
        """Main control loop"""
        try:
            # Perception: Get current state
            state = self.agent.perceive()
            
            # Decision: Agent decides on action
            action = self.agent.decide(state)
            
            # Action: Execute through bridge
            self.agent.act(action)
            
            self.get_logger().debug('Control loop executed successfully')
        except Exception as e:
            self.get_logger().error(f'Error in control loop: {e}')

def main(args=None):
    rclpy.init(args=args)
    system = CompleteRobotSystem()
    rclpy.spin(system)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Best Practices

1. **Always Validate Commands**: Check safety limits before sending to hardware
2. **Use Appropriate Timers**: Match control frequency to task requirements
3. **Error Handling**: Gracefully handle communication failures
4. **Logging**: Log important events and errors for debugging
5. **State Management**: Keep track of system state for recovery
6. **Testing**: Test agent decisions in simulation before hardware

## Summary

Bridging Python agents to ROS controllers creates intelligent robotic systems. The bridge pattern provides abstraction, safety, and coordination between high-level decision-making and low-level control. Understanding how to build effective bridges is crucial for robotics applications.

## Key Takeaways

- Bridge nodes translate between agent commands and controller messages
- Safety validation prevents hardware damage
- Multi-rate control handles different component frequencies
- AI agents use perception-decision-action loops
- Proper architecture enables modular, maintainable systems