# Chapter 6: Human-Robot Interaction in Unity

## Introduction

Human-Robot Interaction (HRI) is crucial for deploying robots in real-world environments where humans and robots work together. Unity's strengths in user interface design and real-time visualization make it ideal for developing and testing HRI systems. This chapter covers building intuitive interfaces, real-time teleoperation, and interactive visualization systems.

## HRI Principles in Robotics

### Types of Human-Robot Interaction

```
Direct Physical Interaction
├─ Physical contact with robot
├─ Force feedback important
└─ Safety-critical

Remote Teleoperation
├─ Control from distance
├─ Relies on sensor feedback
├─ Communication latency critical

Shared Autonomy
├─ Human and robot collaborate
├─ Human provides guidance
├─ Robot provides intelligence

Supervisory Control
├─ Human monitors robot
├─ Robot operates mostly autonomously
├─ Human intervenes when needed

Information Display
├─ Robot provides status
├─ No direct control
├─ Passive monitoring
```

### Design Principles for HRI

```
1. Situation Awareness
   - Show robot state clearly
   - Display sensor data
   - Indicate intentions

2. Intuitive Control
   - Familiar control paradigms
   - Consistent UI/UX patterns
   - Reduce cognitive load

3. Safety
   - Always show safe state
   - Enable emergency stops
   - Predict robot motion

4. Feedback
   - Provide visual confirmation
   - Use audio cues
   - Show latency/delays

5. Accessibility
   - Support multiple input methods
   - Accommodate disabilities
   - Multi-language support
```

## Building Intuitive Control Interfaces

### Keyboard-Based Teleoperation

```csharp
using UnityEngine;

public class TeleoperationController : MonoBehaviour
{
    private RobotStateManager robotState;
    
    // Movement parameters
    public float linearSpeed = 1f;
    public float angularSpeed = 1f;
    public float gripperSpeed = 0.5f;
    
    void Start()
    {
        robotState = GetComponent<RobotStateManager>();
    }
    
    void Update()
    {
        // Mobile base movement
        float linearX = Input.GetAxis("Vertical") * linearSpeed;
        float angularZ = Input.GetAxis("Horizontal") * angularSpeed;
        robotState.SetBaseVelocity(linearX, 0, angularZ);
        
        // Arm control
        HandleArmControl();
        
        // Gripper control
        HandleGripperControl();
        
        // Safety: Emergency stop
        if (Input.GetKeyDown(KeyCode.Space))
        {
            robotState.EmergencyStop();
        }
    }
    
    void HandleArmControl()
    {
        // Shoulder pitch: Q/E
        float shoulderPitch = 0;
        if (Input.GetKey(KeyCode.Q)) shoulderPitch -= 0.5f;
        if (Input.GetKey(KeyCode.E)) shoulderPitch += 0.5f;
        
        // Shoulder roll: A/D
        float shoulderRoll = 0;
        if (Input.GetKey(KeyCode.A)) shoulderRoll -= 0.5f;
        if (Input.GetKey(KeyCode.D)) shoulderRoll += 0.5f;
        
        // Elbow: W/S
        float elbow = 0;
        if (Input.GetKey(KeyCode.W)) elbow += 0.5f;
        if (Input.GetKey(KeyCode.S)) elbow -= 0.5f;
        
        robotState.SetArmJointVelocities(
            shoulderPitch, shoulderRoll, elbow
        );
    }
    
    void HandleGripperControl()
    {
        // Open gripper: Z
        if (Input.GetKeyDown(KeyCode.Z))
        {
            robotState.SetGripperPosition(1f);  // Open
        }
        
        // Close gripper: X
        if (Input.GetKeyDown(KeyCode.X))
        {
            robotState.SetGripperPosition(0f);  // Closed
        }
    }
}
```

### Mouse and Gamepad Control

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

public class GamepadTeleoperation : MonoBehaviour
{
    private RobotStateManager robotState;
    private InputActions inputActions;
    
    void OnEnable()
    {
        // Initialize new input system
        inputActions = new InputActions();
        inputActions.Enable();
        
        // Subscribe to inputs
        inputActions.Robot.Movement.performed += OnMovementInput;
        inputActions.Robot.ArmControl.performed += OnArmInput;
        inputActions.Robot.Gripper.performed += OnGripperInput;
    }
    
    void OnDisable()
    {
        inputActions.Disable();
    }
    
    void OnMovementInput(InputAction.CallbackContext context)
    {
        Vector2 input = context.ReadValue<Vector2>();
        
        // Left stick: forward/back and turn
        float linearSpeed = input.y;
        float angularSpeed = input.x;
        
        robotState.SetBaseVelocity(linearSpeed, 0, angularSpeed);
    }
    
    void OnArmInput(InputAction.CallbackContext context)
    {
        Vector2 stick = context.ReadValue<Vector2>();
        
        // Right stick: arm control
        // X: shoulder rotation
        // Y: elbow control
        robotState.SetArmVelocities(stick.x, stick.y);
    }
    
    void OnGripperInput(InputAction.CallbackContext context)
    {
        float trigger = context.ReadValue<float>();
        
        // Trigger axis: gripper opening (0-1)
        robotState.SetGripperPosition(trigger);
    }
}
```

### Touch-Based Interface for Mobile

```csharp
using UnityEngine;
using UnityEngine.UI;

public class MobileTouchControl : MonoBehaviour
{
    private RobotStateManager robotState;
    
    // UI elements
    public Joystick leftJoystick;   // Movement
    public Joystick rightJoystick;  // Arm control
    public Button gripperOpenBtn;
    public Button gripperCloseBtn;
    
    void Start()
    {
        gripperOpenBtn.onClick.AddListener(() => robotState.OpenGripper());
        gripperCloseBtn.onClick.AddListener(() => robotState.CloseGripper());
    }
    
    void Update()
    {
        // Left joystick: base movement
        Vector2 leftInput = leftJoystick.Direction;
        robotState.SetBaseVelocity(leftInput.y, 0, leftInput.x);
        
        // Right joystick: arm control
        Vector2 rightInput = rightJoystick.Direction;
        robotState.SetArmVelocities(rightInput.x, rightInput.y);
    }
}
```

## Real-Time State Visualization

### Robot State Display Panel

```csharp
using UnityEngine;
using UnityEngine.UI;

public class RobotStatePanel : MonoBehaviour
{
    private Text jointPositionsText;
    private Text sensorDataText;
    private Text statusText;
    
    private RobotStateManager robotState;
    
    void Start()
    {
        // Create UI panel
        CreateStatePanel();
    }
    
    void CreateStatePanel()
    {
        // Main panel
        GameObject panelGO = new GameObject("StatePanel");
        Image panelImage = panelGO.AddComponent<Image>();
        panelImage.color = new Color(0, 0, 0, 0.7f);
        
        // Joint positions section
        GameObject jointGO = new GameObject("JointPositions");
        jointGO.transform.SetParent(panelGO.transform);
        jointPositionsText = jointGO.AddComponent<Text>();
        jointPositionsText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        jointPositionsText.fontSize = 14;
        
        // Sensor data section
        GameObject sensorGO = new GameObject("SensorData");
        sensorGO.transform.SetParent(panelGO.transform);
        sensorDataText = sensorGO.AddComponent<Text>();
        sensorDataText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        sensorDataText.fontSize = 14;
        
        // Status section
        GameObject statusGO = new GameObject("Status");
        statusGO.transform.SetParent(panelGO.transform);
        statusText = statusGO.AddComponent<Text>();
        statusText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        statusText.fontSize = 14;
    }
    
    void Update()
    {
        // Update joint positions
        UpdateJointDisplay();
        
        // Update sensor data
        UpdateSensorDisplay();
        
        // Update status
        UpdateStatusDisplay();
    }
    
    void UpdateJointDisplay()
    {
        string output = "Joint Positions:\n";
        
        for (int i = 0; i < robotState.JointNames.Length; i++)
        {
            float angle = robotState.GetJointPosition(i);
            output += $"{robotState.JointNames[i]}: {angle:F2}°\n";
        }
        
        jointPositionsText.text = output;
    }
    
    void UpdateSensorDisplay()
    {
        string output = "Sensors:\n";
        
        // LiDAR data
        output += $"LiDAR: {robotState.LidarPoints} points\n";
        
        // IMU data
        Vector3 accel = robotState.GetAcceleration();
        output += $"Acceleration: ({accel.x:F2}, {accel.y:F2}, {accel.z:F2})\n";
        
        // Distance sensors
        output += $"Front Distance: {robotState.GetFrontDistance():F2}m\n";
        
        sensorDataText.text = output;
    }
    
    void UpdateStatusDisplay()
    {
        string output = "Status:\n";
        
        output += $"Battery: {robotState.BatteryLevel:F1}%\n";
        output += $"Mode: {robotState.CurrentMode}\n";
        output += robotState.IsMoving ? "Moving" : "Stationary";
        
        statusText.text = output;
    }
}
```

### Point Cloud Visualization

```csharp
using UnityEngine;
using System.Collections.Generic;

public class LidarVisualization : MonoBehaviour
{
    private ParticleSystem particleSystem;
    private List<Vector3> lidarPoints = new List<Vector3>();
    
    void Start()
    {
        // Create particle system for point cloud
        GameObject particleGO = new GameObject("LidarParticles");
        particleGO.transform.SetParent(transform);
        
        particleSystem = particleGO.AddComponent<ParticleSystem>();
        
        // Configure particle system
        var main = particleSystem.main;
        main.maxParticles = 100000;
        main.startSize = 0.02f;
        main.startColor = new ParticleSystem.MinMaxGradient(Color.green);
        main.startLifetime = 0.1f;
        
        // Disable default rendering
        var renderer = particleGO.GetComponent<ParticleSystemRenderer>();
        renderer.renderMode = ParticleSystemRenderMode.Billboard;
    }
    
    /// <summary>
    /// Update LiDAR point cloud visualization
    /// </summary>
    public void UpdatePointCloud(Vector3[] points)
    {
        if (points == null) return;
        
        // Emit particles at point cloud locations
        ParticleSystem.EmitParams emitParams = new ParticleSystem.EmitParams();
        
        foreach (Vector3 point in points)
        {
            emitParams.position = point;
            particleSystem.Emit(emitParams, 1);
        }
    }
    
    /// <summary>
    /// Visualize obstacles detected by LiDAR
    /// </summary>
    public void VisualizeObstacles(
        Vector3[] points, 
        float obstacleThreshold = 2f)
    {
        ParticleSystem.EmitParams emitParams = new ParticleSystem.EmitParams();
        
        // Change color based on proximity
        var main = particleSystem.main;
        
        foreach (Vector3 point in points)
        {
            float distance = point.magnitude;
            
            // Color gradient: green (far) → yellow (medium) → red (close)
            Color color = distance > obstacleThreshold ? 
                Color.green : Color.Lerp(Color.yellow, Color.red, 
                1 - (distance / obstacleThreshold));
            
            emitParams.position = point;
            emitParams.startColor = color;
            
            particleSystem.Emit(emitParams, 1);
        }
    }
}
```

## Teleoperation with Latency Simulation

### Network Latency Handling

```csharp
using UnityEngine;
using System.Collections.Generic;

public class TeleoperationWithLatency : MonoBehaviour
{
    private Queue<CommandFrame> commandQueue = 
        new Queue<CommandFrame>();
    
    // Simulated latency
    public float networkLatency = 0.1f;  // 100ms
    
    private float timeSinceLastCommand = 0f;
    
    // Command frame structure
    private struct CommandFrame
    {
        public float timestamp;
        public Vector3 baseVelocity;
        public Vector3[] jointVelocities;
    }
    
    void Update()
    {
        // Accumulate time
        timeSinceLastCommand += Time.deltaTime;
        
        // Send command every fixed interval (to simulate network packets)
        if (timeSinceLastCommand >= 0.05f)  // 50ms packet rate
        {
            timeSinceLastCommand = 0;
            SendCommandWithLatency();
        }
        
        // Execute queued commands that have arrived
        ExecuteQueuedCommands();
    }
    
    void SendCommandWithLatency()
    {
        // Get current input
        Vector3 baseVel = GetBaseInput();
        Vector3[] jointVels = GetArmInput();
        
        // Create command frame
        CommandFrame frame = new CommandFrame
        {
            timestamp = Time.time + networkLatency,
            baseVelocity = baseVel,
            jointVelocities = jointVels
        };
        
        // Queue for delayed execution
        commandQueue.Enqueue(frame);
    }
    
    void ExecuteQueuedCommands()
    {
        while (commandQueue.Count > 0)
        {
            CommandFrame frame = commandQueue.Peek();
            
            if (Time.time >= frame.timestamp)
            {
                // Execute command
                ApplyCommand(frame.baseVelocity, frame.jointVelocities);
                commandQueue.Dequeue();
            }
            else
            {
                break;  // Next command not ready yet
            }
        }
    }
    
    void ApplyCommand(Vector3 baseVel, Vector3[] jointVels)
    {
        // Apply to robot
        // ...
    }
    
    Vector3 GetBaseInput() { return Vector3.zero; }
    Vector3[] GetArmInput() { return new Vector3[3]; }
}
```

### Feedback Visualization with Latency

```csharp
using UnityEngine;

public class LatencyDisplay : MonoBehaviour
{
    private Text latencyText;
    private RingBuffer<float> latencyHistory = new RingBuffer<float>(100);
    
    private float lastCommandTime = 0;
    private float measuredLatency = 0;
    
    public void OnCommandSent()
    {
        lastCommandTime = Time.realtimeSinceStartup;
    }
    
    public void OnFeedbackReceived()
    {
        float roundTripTime = Time.realtimeSinceStartup - lastCommandTime;
        measuredLatency = roundTripTime / 2f;  // Half for one-way
        latencyHistory.Add(measuredLatency);
        
        UpdateDisplay();
    }
    
    void UpdateDisplay()
    {
        float avgLatency = 0;
        foreach (float latency in latencyHistory)
        {
            avgLatency += latency;
        }
        avgLatency /= latencyHistory.Count;
        
        // Color warning based on latency
        Color color = Color.green;
        if (measuredLatency > 0.1f) color = Color.yellow;
        if (measuredLatency > 0.2f) color = Color.red;
        
        latencyText.text = $"Latency: {measuredLatency * 1000:F1}ms";
        latencyText.color = color;
    }
}
```

## Interactive Safety Features

### Virtual Boundaries and Collision Avoidance

```csharp
using UnityEngine;
using UnityEngine.UI;

public class SafetyBoundaries : MonoBehaviour
{
    // Define safe operation zones
    private Vector3 boundaryMin;
    private Vector3 boundaryMax;
    
    // Collision detection
    private SphereCollider[] robotLinks;
    
    // Safety UI
    private Image boundaryVisualization;
    private Text warningText;
    
    void Start()
    {
        // Define work cell boundaries
        boundaryMin = new Vector3(-5, 0, -5);
        boundaryMax = new Vector3(5, 3, 5);
        
        // Get all colliders from robot
        robotLinks = GetComponentsInChildren<SphereCollider>();
        
        CreateBoundaryVisualization();
    }
    
    void CreateBoundaryVisualization()
    {
        // Create wireframe box for boundary
        GameObject boundaryGO = new GameObject("BoundaryBox");
        LineRenderer lineRenderer = boundaryGO.AddComponent<LineRenderer>();
        
        // Draw box edges
        Vector3[] corners = GetBoundaryCorners();
        // ... setup line renderer with corner points
    }
    
    void FixedUpdate()
    {
        // Check for boundary violations
        CheckBoundaries();
        
        // Check for collisions
        CheckCollisions();
    }
    
    void CheckBoundaries()
    {
        foreach (var link in robotLinks)
        {
            Vector3 pos = link.transform.position;
            
            // Check if link is outside boundary
            if (pos.x < boundaryMin.x || pos.x > boundaryMax.x ||
                pos.y < boundaryMin.y || pos.y > boundaryMax.y ||
                pos.z < boundaryMin.z || pos.z > boundaryMax.z)
            {
                // Outside boundary - activate safety
                OnBoundaryViolation(link.name);
            }
        }
    }
    
    void CheckCollisions()
    {
        // Check if robot is in collision with environment
        Collider[] hits = Physics.OverlapBox(
            (boundaryMin + boundaryMax) / 2,
            (boundaryMax - boundaryMin) / 2,
            Quaternion.identity
        );
        
        foreach (var hit in hits)
        {
            if (hit.CompareTag("Obstacle"))
            {
                OnCollisionDetected(hit.name);
            }
        }
    }
    
    void OnBoundaryViolation(string linkName)
    {
        warningText.text = $"⚠ {linkName} OUTSIDE BOUNDARY";
        warningText.color = Color.red;
        
        // Trigger safety action
        StopRobot();
    }
    
    void OnCollisionDetected(string objectName)
    {
        warningText.text = $"⚠ COLLISION WITH {objectName}";
        warningText.color = Color.red;
        
        // Trigger safety action
        StopRobot();
    }
    
    void StopRobot()
    {
        // Stop all movement
        GetComponent<RobotStateManager>().EmergencyStop();
    }
    
    Vector3[] GetBoundaryCorners()
    {
        return new Vector3[]
        {
            boundaryMin,
            new Vector3(boundaryMax.x, boundaryMin.y, boundaryMin.z),
            new Vector3(boundaryMax.x, boundaryMax.y, boundaryMin.z),
            new Vector3(boundaryMin.x, boundaryMax.y, boundaryMin.z),
            // ... more corners
        };
    }
}
```

### Emergency Stop Button

```csharp
using UnityEngine;
using UnityEngine.UI;

public class EmergencyStopButton : MonoBehaviour
{
    private Button emergencyStopBtn;
    private RobotStateManager robotState;
    
    // Audio feedback
    private AudioSource alarmSound;
    
    void Start()
    {
        emergencyStopBtn = GetComponent<Button>();
        emergencyStopBtn.onClick.AddListener(OnEmergencyStop);
        
        // Setup alarm sound
        alarmSound = gameObject.AddComponent<AudioSource>();
        alarmSound.clip = Resources.Load<AudioClip>("Sounds/alarm");
    }
    
    void OnEmergencyStop()
    {
        // Immediate robot stop
        robotState.EmergencyStop();
        
        // Visual feedback
        emergencyStopBtn.image.color = Color.red;
        
        // Audio feedback
        alarmSound.Play();
        
        Debug.Log("EMERGENCY STOP ACTIVATED");
    }
    
    public void ResetEmergencyStop()
    {
        // Reset button
        emergencyStopBtn.image.color = Color.white;
        
        // Confirm reset with operator
        if (ConfirmDialog("Reset emergency stop?"))
        {
            robotState.ResetEmergencyStop();
        }
    }
    
    bool ConfirmDialog(string message)
    {
        // Implementation of confirmation dialog
        return true;
    }
}
```

## Summary

Unity's HRI capabilities enable creating professional control interfaces, real-time visualization systems, and safety mechanisms critical for real-world robot deployment. Combined with Gazebo's physics simulation, it provides a complete development environment from algorithm validation to user interface prototyping.

## Key Takeaways

- HRI design requires intuitive interfaces and clear feedback
- Multiple input methods (keyboard, gamepad, touch) improve accessibility
- Real-time visualization of robot state and sensor data is essential
- Network latency simulation prepares for real-world deployment
- Safety features (boundaries, collision detection) prevent accidents
- Emergency stops and clear status indicators are non-negotiable
- Testing HRI in simulation reduces deployment risks