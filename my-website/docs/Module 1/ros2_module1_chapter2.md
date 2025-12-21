# Chapter 2: ROS 2 Nodes, Topics, and Services

## Introduction

Nodes, topics, and services are the fundamental building blocks of ROS 2 systems. Understanding how they interact is essential for building distributed robotic applications. This chapter covers these core concepts in detail.

## Part 1: ROS 2 Nodes

### What is a Node?

A node is a single executable that performs a specific function in your robot system. It's an independent process that:
- Runs continuously or for a specific duration
- Communicates with other nodes via topics and services
- Has a unique name within the ROS 2 system
- Can be started, stopped, or restarted independently

### Node Lifecycle

ROS 2 nodes have a managed lifecycle with states:

1. **Unconfigured**: Initial state, node is created but not initialized
2. **Inactive**: Node is configured but not active
3. **Active**: Node is running and functioning
4. **Finalized**: Node is shutting down

### Creating Your First Node

A basic ROS 2 node structure in Python:

```python
import rclpy
from rclpy.node import Node

class MyFirstNode(Node):
    def __init__(self):
        super().__init__('my_first_node')
        self.get_logger().info('Node initialized!')

def main(args=None):
    rclpy.init(args=args)
    node = MyFirstNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Node Features

#### Logging
Every node has a built-in logger for debugging:

```python
self.get_logger().debug('Debug message')
self.get_logger().info('Info message')
self.get_logger().warn('Warning message')
self.get_logger().error('Error message')
```

#### Parameters
Nodes can have configurable parameters:

```python
# Declare parameter
self.declare_parameter('sensor_name', 'default_sensor')

# Get parameter value
sensor_name = self.get_parameter('sensor_name').value

# Set parameter value
self.set_parameters([rclpy.Parameter('sensor_name', 'new_sensor')])
```

#### Timers
Execute functions periodically:

```python
self.timer = self.create_timer(0.1, self.timer_callback)  # Every 100ms

def timer_callback(self):
    self.get_logger().info('Timer triggered!')
```

## Part 2: ROS 2 Topics

### Understanding Topics

Topics implement the publish-subscribe pattern:
- **Publishers** send data to a topic
- **Subscribers** receive data from a topic
- Multiple publishers and subscribers can exist for the same topic
- Communication is asynchronous and one-way

### Topic Structure

```
Topic: /robot/sensor/temperature
├── Message Type: sensor_msgs/msg/Temperature
├── Publishers: 
│   ├── temperature_sensor_node
│   └── temperature_simulator_node
├── Subscribers:
│   ├── logging_node
│   ├── control_node
│   └── monitoring_node
└── Queue Size: 10
```

### Creating a Publisher

```python
from std_msgs.msg import Float32

class SensorPublisher(Node):
    def __init__(self):
        super().__init__('sensor_publisher')
        
        # Create publisher
        self.publisher = self.create_publisher(
            Float32,
            '/sensor/temperature',
            queue_size=10
        )
        
        # Timer for publishing
        self.timer = self.create_timer(1.0, self.publish_data)
        self.counter = 0.0
    
    def publish_data(self):
        msg = Float32()
        msg.data = self.counter
        self.publisher.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')
        self.counter += 0.1
```

### Creating a Subscriber

```python
from std_msgs.msg import Float32

class SensorSubscriber(Node):
    def __init__(self):
        super().__init__('sensor_subscriber')
        
        # Create subscriber
        self.subscription = self.create_subscription(
            Float32,
            '/sensor/temperature',
            self.listener_callback,
            queue_size=10
        )
    
    def listener_callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')
```

### Common Message Types

#### std_msgs
Basic message types:
- `Bool`: Boolean value
- `Int32`, `Int64`: Integer values
- `Float32`, `Float64`: Floating-point values
- `String`: Text messages

#### sensor_msgs
Sensor-specific messages:
- `Temperature`: Temperature data with units
- `Image`: Camera images
- `PointCloud2`: 3D point cloud data
- `Imu`: IMU sensor data
- `JointState`: Joint positions and velocities

#### geometry_msgs
Geometry and motion messages:
- `Point`: 3D point coordinates
- `Quaternion`: Orientation (rotation)
- `Twist`: Linear and angular velocity
- `PoseStamped`: Position and orientation with timestamp

### Topic Best Practices

1. **Naming Convention**: Use descriptive, hierarchical names
   - Good: `/robot/arm/joint_states`
   - Bad: `/data`, `/info`

2. **Message Frequency**: Choose appropriate publication rates
   - Control loops: 50-1000 Hz
   - Sensor data: 10-100 Hz
   - Status updates: 1-10 Hz

3. **Queue Size**: Buffer messages in case subscriber is slow
   - Small queues (1-5): Real-time, drop old messages
   - Large queues (10-100): Store messages for delayed processing

## Part 3: ROS 2 Services

### Understanding Services

Services implement the request-reply pattern:
- **Client** sends a request and waits for a response
- **Server** receives request, processes it, and sends response
- Communication is synchronous and bidirectional
- Used for discrete, infrequent operations

### Service vs Topic

| Aspect | Topic | Service |
|--------|-------|---------|
| Pattern | Publish-Subscribe | Request-Reply |
| Direction | One-way | Bidirectional |
| Synchronization | Asynchronous | Synchronous |
| Use Cases | Continuous streams | Discrete operations |
| Latency | Can be high | Low |

### Creating a Service Server

```python
from example_interfaces.srv import AddTwoInts

class ServiceServer(Node):
    def __init__(self):
        super().__init__('service_server')
        
        # Create service
        self.srv = self.create_service(
            AddTwoInts,
            '/add_two_ints',
            self.add_two_ints_callback
        )
        self.get_logger().info('Service server started')
    
    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Request: {request.a} + {request.b} = {response.sum}')
        return response
```

### Creating a Service Client

```python
import time
from example_interfaces.srv import AddTwoInts

class ServiceClient(Node):
    def __init__(self):
        super().__init__('service_client')
        self.client = self.create_client(
            AddTwoInts,
            '/add_two_ints'
        )
        
        # Wait for service to be available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')
    
    def send_request(self, a, b):
        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        
        # Call service and wait for response
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            self.get_logger().info(f'Result: {future.result().sum}')
        else:
            self.get_logger().error('Service call failed')
```

### Asynchronous Service Calls

For non-blocking service calls:

```python
def send_request_async(self, a, b):
    request = AddTwoInts.Request()
    request.a = a
    request.b = b
    
    # Send request without blocking
    future = self.client.call_async(request)
    future.add_done_callback(self.result_callback)

def result_callback(self, future):
    try:
        response = future.result()
        self.get_logger().info(f'Result: {response.sum}')
    except Exception as e:
        self.get_logger().error(f'Service call failed: {e}')
```

## Communication Patterns in Practice

### Pattern 1: Sensor Publishing
```
Hardware Sensor → Driver Node → Publisher → Topic
                                              ├→ Logger Node
                                              ├→ Control Node
                                              └→ Monitor Node
```

### Pattern 2: Control Command
```
Planning Node → Client → Service Request → Server Node → Hardware Actuator
             ← Server → Response ← Client
```

### Pattern 3: Complex System
```
Lidar Driver ──┐
               ├→ Perception Node ──→ Detection Topic ──→ Decision Node
Camera Driver ─┤                                               ↓
               └→ Processing Node ──→ Processed Data Topic ──→ Control Server
                                                              ↓
                                                         Motor Command Service
```

## Debugging Topics and Services

### Viewing Active Topics
```bash
ros2 topic list
ros2 topic echo /topic_name
ros2 topic info /topic_name
```

### Viewing Active Services
```bash
ros2 service list
ros2 service type /service_name
ros2 service call /service_name service_type '{args}'
```

## Summary

Nodes, topics, and services form the communication backbone of ROS 2 systems. Topics enable efficient streaming of sensor data and status updates, while services handle discrete requests and control commands. Understanding when to use each pattern is crucial for building effective robotic systems.

## Key Takeaways

- Nodes are independent executables performing specific functions
- Topics implement asynchronous one-to-many communication
- Services implement synchronous request-reply communication
- Publishers and subscribers are loosely coupled
- Parameters allow runtime configuration of nodes
- Proper naming conventions and message types improve system clarity
- Debugging tools like `ros2 topic` and `ros2 service` are essential