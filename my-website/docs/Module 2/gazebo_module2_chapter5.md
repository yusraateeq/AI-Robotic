# Chapter 5: High-Fidelity Rendering in Unity

## Introduction

While Gazebo excels at physics simulation, Unity provides state-of-the-art 3D rendering for creating visually realistic robot simulations. This chapter covers setting up Unity for robotics, importing robot models, implementing real-time rendering, and configuring materials and lighting to create photorealistic environments.

## Why Unity for Robotics?

### Strengths of Unity

```
Unity Advantages:
├── Graphics
│   ├── Photorealistic rendering
│   ├── Real-time ray tracing
│   ├── Advanced lighting systems
│   ├── Particle effects
│   └── Post-processing effects
├── Performance
│   ├── Efficient GPU utilization
│   ├── Scalable to mobile platforms
│   ├── 60+ FPS on modern hardware
│   └── Optimization tools
├── Development
│   ├── Visual editor for rapid prototyping
│   ├── Asset store with thousands of resources
│   ├── Strong community support
│   └── Cross-platform deployment
├── Integration
│   ├── ROS 2 communication packages
│   ├── Physics engine (PhysX)
│   └── Sensor simulation plugins
└── HRI
    ├── Intuitive UI frameworks
    ├── Interactive visualizations
    └── Real-time teleoperation capability
```

### When to Use Unity vs Gazebo

| Scenario | Tool |
|----------|------|
| Algorithm testing, reproducible results | Gazebo |
| Visualization for presentation | Unity |
| Hardware-in-loop integration | Gazebo |
| Stakeholder demos | Unity |
| Sensor algorithm validation | Both |
| User interface prototyping | Unity |
| Physics-accurate testing | Gazebo |
| Production deployment preview | Unity |

## Unity Project Setup for Robotics

### Creating a Robotics Project

```
1. Download Unity Hub
2. Install Unity 2021 LTS or Later
3. Create new 3D project
4. Set default physics engine to PhysX
5. Import packages:
   - Universal Render Pipeline (URP) for graphics
   - Unity Robotics Hub from GitHub
   - ROS 2 Communication Bridge
```

### Project Structure

```
Assets/
├── Robots/
│   ├── URDF_Imports/
│   │   └── humanoid_model/
│   │       ├── Meshes/
│   │       ├── Materials/
│   │       └── Prefabs/
│   └── Scripts/
│       ├── RobotController.cs
│       └── JointActuator.cs
├── Scenes/
│   ├── SimulationScene.unity
│   └── VisualizationScene.unity
├── Environments/
│   ├── Meshes/
│   ├── Materials/
│   └── Prefabs/
├── Plugins/
│   ├── ROS2/
│   ├── Sensors/
│   └── Communication/
└── Resources/
    ├── Shaders/
    └── Textures/
```

## Importing URDF Models

### Using Unity Robotics URDF Importer

```
Installation:
1. Add to Packages/manifest.json:
   "com.unity.robotics.urdf-importer": 
     "https://github.com/Unity-Technologies/URDF-Importer.git"

2. In menu: Robotics → URDF Importer → Import URDF
```

### Manual URDF Import Process

```csharp
using UnityEngine;
using Unity.Robotics.UrdfImporter;

public class URDFImporter : MonoBehaviour
{
    /// <summary>
    /// Import a URDF file and create Unity game objects
    /// </summary>
    public void ImportURDF(string urdfPath)
    {
        // Load URDF file
        string urdfContent = System.IO.File.ReadAllText(urdfPath);
        
        // Parse URDF (simplified - actual parsing is complex)
        // In practice, use Unity.Robotics.UrdfImporter.UrdfAssetImporter
        
        // Create root game object
        GameObject robotRoot = new GameObject("Robot");
        
        // The URDF importer handles:
        // - Link → GameObject hierarchy
        // - Joint → Articulation Body constraints
        // - Visual → Mesh Renderer
        // - Collision → Collider component
        // - Inertial → Rigidbody properties
    }
}
```

### Structure After Import

```
Imported Robot Hierarchy:
Robot (root)
├── base_link
│   ├── MeshRenderer (visual)
│   ├── Collider (collision)
│   ├── ArticulationBody (joint constraints)
│   └── left_upper_arm
│       ├── MeshRenderer
│       ├── Collider
│       ├── ArticulationBody
│       └── left_forearm
│           ├── MeshRenderer
│           ├── Collider
│           └── ArticulationBody
├── right_upper_arm
│   └── ... (similar structure)
└── head
    └── ... (similar structure)
```

## Real-Time Rendering

### Graphics Pipeline in Unity

```
Rendering Pipeline:
┌─────────────────────────────┐
│   Scene (Robots, Env)       │
└──────────────┬──────────────┘
               │
        ┌──────▼──────────┐
        │ Camera Rendering│
        └──────┬──────────┘
               │
        ┌──────▼──────────────────┐
        │ Graphics Pipeline        │
        ├──────────────────────────┤
        │ 1. Geometry rendering    │
        │ 2. Lighting calculations │
        │ 3. Shadows rendering     │
        │ 4. Post-processing       │
        └──────┬───────────────────┘
               │
        ┌──────▼──────────┐
        │ Frame Buffer    │
        └──────┬──────────┘
               │
        ┌──────▼──────────┐
        │ Display/Output  │
        └─────────────────┘
```

### Setting Up the Camera

```csharp
using UnityEngine;

public class RobotCamera : MonoBehaviour
{
    private Camera mainCamera;
    public Transform followTarget;
    public float distance = 5f;
    public float height = 2f;
    public float rotationSpeed = 100f;
    
    private float currentAngle = 0f;
    
    void Start()
    {
        mainCamera = Camera.main;
        
        // Camera settings for robotics visualization
        mainCamera.fieldOfView = 60f;              // Standard FOV
        mainCamera.nearClipPlane = 0.01f;          // Close objects
        mainCamera.farClipPlane = 1000f;           // Distant objects
    }
    
    void LateUpdate()
    {
        if (followTarget == null) return;
        
        // Orbital camera following robot
        currentAngle += Input.GetAxis("Horizontal") * rotationSpeed * Time.deltaTime;
        
        Vector3 targetPos = followTarget.position;
        Vector3 cameraPos = targetPos + 
            new Vector3(
                Mathf.Cos(currentAngle * Mathf.Deg2Rad) * distance,
                height,
                Mathf.Sin(currentAngle * Mathf.Deg2Rad) * distance
            );
        
        mainCamera.transform.position = cameraPos;
        mainCamera.transform.LookAt(targetPos + Vector3.up * 1f);
    }
}
```

### Rendering Performance Optimization

```csharp
using UnityEngine;

public class RenderingOptimizer : MonoBehaviour
{
    void Start()
    {
        // LOD (Level of Detail) optimization
        QualitySettings.masterTextureLimit = 1;  // Reduce texture resolution
        
        // Shadow optimization
        QualitySettings.shadowDistance = 50f;
        QualitySettings.shadowResolution = ShadowResolution.Medium;
        
        // Frame rate limiting
        Application.targetFrameRate = 60;  // Cap at 60 FPS
        
        // Memory optimization
        Resources.UnloadUnusedAssets();
    }
    
    void OnGUI()
    {
        // Display performance stats
        float fps = 1f / Time.deltaTime;
        GUILayout.Label($"FPS: {fps:F1}");
    }
}
```

## Materials and Lighting

### Creating Materials

```csharp
using UnityEngine;

public class MaterialFactory : MonoBehaviour
{
    /// <summary>
    /// Create robot joint material (dark metal)
    /// </summary>
    public static Material CreateJointMaterial()
    {
        Material mat = new Material(Shader.Find("Standard"));
        mat.color = new Color(0.3f, 0.3f, 0.3f, 1f);
        mat.SetFloat("_Metallic", 0.8f);
        mat.SetFloat("_Smoothness", 0.6f);
        return mat;
    }
    
    /// <summary>
    /// Create robot link material (painted surface)
    /// </summary>
    public static Material CreateLinkMaterial(Color color)
    {
        Material mat = new Material(Shader.Find("Standard"));
        mat.color = color;
        mat.SetFloat("_Metallic", 0.1f);
        mat.SetFloat("_Smoothness", 0.7f);
        return mat;
    }
    
    /// <summary>
    /// Create environment material (concrete floor)
    /// </summary>
    public static Material CreateConcreteFloor()
    {
        Material mat = new Material(Shader.Find("Standard"));
        mat.color = new Color(0.8f, 0.8f, 0.8f, 1f);
        mat.SetFloat("_Metallic", 0f);
        mat.SetFloat("_Smoothness", 0.3f);
        
        // Load texture if available
        Texture2D concreteTex = Resources.Load<Texture2D>("Textures/concrete");
        if (concreteTex != null)
        {
            mat.mainTexture = concreteTex;
            mat.SetTextureScale("_MainTex", new Vector2(4, 4));
        }
        
        return mat;
    }
}
```

### Physically-Based Rendering (PBR)

```
PBR Material Properties:

Albedo (Base Color):
  - The base color without lighting
  - Use RGB values [0-255] or [0-1]
  - Example: Robot arm = RGB(100, 100, 100)

Metallic:
  - 0 = non-metal (plastic, rubber, paint)
  - 1 = full metal (steel, aluminum)
  - Common values:
    * Painted robot: 0.1
    * Metal joint: 0.8
    * Rubber wheel: 0.0

Smoothness (Roughness):
  - 0 = rough (matte surface)
  - 1 = smooth (polished mirror)
  - Common values:
    * Matte paint: 0.4
    * Polished metal: 0.7
    * Rough plastic: 0.3

Normal Map:
  - Adds surface detail without geometry
  - Essential for high-fidelity rendering
```

### Lighting Setup

```csharp
using UnityEngine;

public class LightingSetup : MonoBehaviour
{
    void Start()
    {
        // Main directional light (sun)
        GameObject sunGO = new GameObject("DirectionalLight");
        Light sunLight = sunGO.AddComponent<Light>();
        sunLight.type = LightType.Directional;
        sunLight.intensity = 1.2f;
        sunLight.color = new Color(1f, 0.95f, 0.8f);  // Warm daylight
        sunGO.transform.rotation = Quaternion.Euler(45f, -45f, 0f);
        
        // Enable shadows
        sunLight.shadows = LightShadows.Soft;
        sunLight.shadowResolution = LightShadowResolution.High;
        
        // Fill light (reduce harsh shadows)
        GameObject fillGO = new GameObject("FillLight");
        Light fillLight = fillGO.AddComponent<Light>();
        fillLight.type = LightType.Directional;
        fillLight.intensity = 0.3f;
        fillLight.color = new Color(0.7f, 0.8f, 1f);   // Cool shadow fill
        fillGO.transform.rotation = Quaternion.Euler(-30f, 135f, 0f);
        
        // Ambient light (global illumination)
        RenderSettings.ambientLight = new Color(0.5f, 0.5f, 0.5f, 1f);
        RenderSettings.ambientIntensity = 0.3f;
    }
}
```

### Advanced Lighting Effects

#### Real-Time Shadows

```csharp
public class ShadowConfiguration : MonoBehaviour
{
    void Start()
    {
        // Shadow settings
        QualitySettings.shadowDistance = 100f;  // Shadow render distance
        QualitySettings.shadowResolution = ShadowResolution.VeryHigh;
        QualitySettings.shadowProjection = ShadowProjection.StableFit;
        
        // Per-light shadow settings
        Light mainLight = GetComponent<Light>();
        mainLight.shadows = LightShadows.Soft;
        mainLight.shadowBias = 0.05f;
        mainLight.shadowNormalBias = 0.4f;
    }
}
```

#### Post-Processing Effects

```csharp
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

public class PostProcessing : MonoBehaviour
{
    void Start()
    {
        // Get the Volume component (should be in scene)
        Volume volume = GetComponent<Volume>();
        
        if (volume.profile.TryGet<Bloom>(out var bloom))
        {
            bloom.active = true;
            bloom.intensity.value = 0.5f;
        }
        
        if (volume.profile.TryGet<DepthOfField>(out var dof))
        {
            dof.active = false;  // Disable for clear robot view
        }
        
        if (volume.profile.TryGet<MotionBlur>(out var motionBlur))
        {
            motionBlur.active = false;  // Disable for precise tracking
        }
    }
}
```

## Joint and Animation Control

### Articulation Bodies for Joint Control

```csharp
using UnityEngine;

public class JointController : MonoBehaviour
{
    private ArticulationBody articulationBody;
    public float targetPosition = 0f;
    public float driveForce = 100f;
    
    void Start()
    {
        articulationBody = GetComponent<ArticulationBody>();
        
        if (articulationBody != null)
        {
            // Configure joint drive
            var drive = articulationBody.xDrive;
            drive.targetPosition = targetPosition;
            drive.stiffness = 1000f;
            drive.damping = 50f;
            drive.forceLimit = driveForce;
            articulationBody.xDrive = drive;
        }
    }
    
    public void SetTargetPosition(float position)
    {
        targetPosition = position;
        if (articulationBody != null)
        {
            var drive = articulationBody.xDrive;
            drive.targetPosition = Mathf.Clamp(
                position,
                articulationBody.xDrive.lowerLimit,
                articulationBody.xDrive.upperLimit
            );
            articulationBody.xDrive = drive;
        }
    }
    
    public float GetCurrentPosition()
    {
        if (articulationBody == null) return 0f;
        return articulationBody.jointPosition[0];
    }
}
```

### Robot State Animator

```csharp
using UnityEngine;
using System.Collections.Generic;

public class RobotStateAnimator : MonoBehaviour
{
    private Dictionary<string, JointController> joints = 
        new Dictionary<string, JointController>();
    
    void Start()
    {
        // Find all joint controllers in children
        JointController[] jointControllers = 
            GetComponentsInChildren<JointController>();
        
        foreach (var joint in jointControllers)
        {
            joints[joint.gameObject.name] = joint;
        }
    }
    
    /// <summary>
    /// Set all joint positions for a specific pose
    /// </summary>
    public void SetPose(Dictionary<string, float> poseDict)
    {
        foreach (var kvp in poseDict)
        {
            if (joints.ContainsKey(kvp.Key))
            {
                joints[kvp.Key].SetTargetPosition(kvp.Value);
            }
        }
    }
    
    /// <summary>
    /// Smoothly interpolate to target pose
    /// </summary>
    public void AnimateToPose(
        Dictionary<string, float> targetPose, 
        float duration)
    {
        StartCoroutine(AnimatePoseCoroutine(targetPose, duration));
    }
    
    private System.Collections.IEnumerator AnimatePoseCoroutine(
        Dictionary<string, float> targetPose, 
        float duration)
    {
        float elapsed = 0f;
        var startPositions = new Dictionary<string, float>();
        
        // Store starting positions
        foreach (var kvp in targetPose)
        {
            if (joints.ContainsKey(kvp.Key))
            {
                startPositions[kvp.Key] = 
                    joints[kvp.Key].GetCurrentPosition();
            }
        }
        
        // Animate smoothly
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = Mathf.Clamp01(elapsed / duration);
            
            // Smooth interpolation
            float smoothT = Mathf.SmoothStep(0, 1, t);
            
            foreach (var kvp in targetPose)
            {
                if (startPositions.ContainsKey(kvp.Key))
                {
                    float start = startPositions[kvp.Key];
                    float target = kvp.Value;
                    float current = Mathf.Lerp(start, target, smoothT);
                    joints[kvp.Key].SetTargetPosition(current);
                }
            }
            
            yield return null;
        }
        
        // Ensure final positions
        SetPose(targetPose);
    }
}
```

## Performance Profiling

### Frame Rate Monitoring

```csharp
using UnityEngine;
using UnityEngine.UI;

public class PerformanceMonitor : MonoBehaviour
{
    private Text fpsText;
    private float updateInterval = 0.5f;
    private float lastUpdateTime = 0f;
    private int frameCount = 0;
    
    void Start()
    {
        // Create UI text element
        GameObject canvasGO = new GameObject("PerformanceCanvas");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        
        GameObject textGO = new GameObject("FPSText");
        textGO.transform.SetParent(canvasGO.transform);
        fpsText = textGO.AddComponent<Text>();
        fpsText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        fpsText.fontSize = 20;
    }
    
    void Update()
    {
        frameCount++;
        
        if (Time.realtimeSinceStartup >= lastUpdateTime + updateInterval)
        {
            float fps = frameCount / (Time.realtimeSinceStartup - lastUpdateTime);
            fpsText.text = $"FPS: {fps:F1}";
            
            // Memory usage
            long memoryUsage = System.GC.GetTotalMemory(false);
            fpsText.text += $"\nMemory: {memoryUsage / 1024 / 1024} MB";
            
            frameCount = 0;
            lastUpdateTime = Time.realtimeSinceStartup;
        }
    }
}
```

## Summary

Unity provides professional-grade 3D rendering and visualization capabilities essential for presenting robot simulations to stakeholders, validating HRI designs, and creating engaging demonstrations. When combined with Gazebo's physics simulation, it creates a complete robotics development pipeline.

## Key Takeaways

- Unity excels at visual fidelity and real-time rendering
- URDF importing enables robot model integration
- PBR materials create photorealistic appearance
- Articulation bodies simulate joint mechanics
- Lighting and shadows significantly impact visual quality
- Performance optimization ensures smooth interaction
- Combined Gazebo+Unity workflow leverages strengths of both