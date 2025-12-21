# Chapter 3: Synthetic Data Generation for AI Training

## Introduction

One of the most powerful capabilities of Isaac Sim is automated synthetic data generation. This chapter covers creating large-scale training datasets with domain randomization, automatic annotation, and the techniques needed to bridge the sim-to-real gap.

## Why Synthetic Data?

### Advantages of Synthetic Data

```
Synthetic Data Benefits:
├── Cost
│   ├── No expensive real hardware needed
│   ├── No human annotators required
│   └── Parallel data generation (100× speedup)
├── Diversity
│   ├── Infinite variation generation
│   ├── Rare scenarios easily created
│   └── Perfect occlusion handling
├── Annotation
│   ├── Automatic perfect labels
│   ├── Pixel-perfect segmentation
│   ├── Precise 3D annotations
│   └── Depth and semantics "free"
├── Reproducibility
│   ├── Exact same conditions reproducible
│   ├── Controlled variability
│   └── Deterministic results
└── Efficiency
    ├── Run 1000 simulations in parallel
    ├── Generate 1 million images in hours
    └── Train on full diversity
```

### Data Requirements for Deep Learning

```
Model Type          Images Needed    Annotation Type
──────────────────────────────────────────────────
Classification      100k-1M          Image labels
Object Detection    10k-100k         Bounding boxes + class
Segmentation        10k-100k         Pixel-wise masks
Pose Estimation     50k-500k         Joint keypoints
SLAM/Depth          100k-1M          Depth ground truth
3D Detection        50k-500k         3D boxes + labels
```

## Domain Randomization

### Core Concept

Domain randomization involves varying simulation parameters to create diverse training scenarios:

```python
"""
Domain randomization for robust model training
"""

import random
import numpy as np
from typing import Dict, List, Tuple

class DomainRandomizer:
    """
    Randomize simulation parameters for diverse training data
    """
    
    def __init__(self):
        self.randomization_config = self._default_config()
    
    def _default_config(self) -> Dict:
        """Default randomization parameters"""
        return {
            'lighting': {
                'enabled': True,
                'intensity': [0.3, 2.0],           # min, max
                'direction': [0, 360],              # degrees
                'color_temp': [3000, 7000]          # Kelvin
            },
            'camera': {
                'enabled': True,
                'position_offset': [-0.5, 0.5],    # meters
                'focal_length': [0.5, 2.0],        # normalized
                'aperture': [16, 64]                # f-number
            },
            'materials': {
                'enabled': True,
                'albedo_variation': 0.2,            # ±20%
                'roughness_variation': 0.1,         # ±10%
                'metallic_variation': 0.1
            },
            'objects': {
                'enabled': True,
                'scale': [0.8, 1.2],                # scale variation
                'rotation_jitter': [0, 360],        # degrees
                'position_noise': 0.05              # meters
            },
            'weather': {
                'enabled': True,
                'rain': {'probability': 0.1, 'intensity': [0, 1]},
                'fog': {'probability': 0.1, 'density': [0, 0.5]},
                'snow': {'probability': 0.05}
            },
            'dynamics': {
                'enabled': True,
                'gravity': [9.6, 10.2],             # m/s²
                'friction': [0.3, 1.5],
                'restitution': [0.0, 0.5]
            }
        }
    
    def randomize_lighting(self) -> Dict:
        """Randomize scene lighting"""
        cfg = self.randomization_config['lighting']
        
        return {
            'intensity': random.uniform(*cfg['intensity']),
            'direction': random.uniform(*cfg['direction']),
            'color_temp': random.uniform(*cfg['color_temp']),
            # Random warm/cool tone
            'color': tuple(np.random.uniform(0.7, 1.0, 3))
        }
    
    def randomize_camera(self) -> Dict:
        """Randomize camera parameters"""
        cfg = self.randomization_config['camera']
        
        # Slight camera motion/jitter
        position_offset = [
            random.uniform(*cfg['position_offset']),
            random.uniform(*cfg['position_offset']),
            random.uniform(*cfg['position_offset'])
        ]
        
        return {
            'position_offset': position_offset,
            'focal_length': random.uniform(*cfg['focal_length']),
            'aperture': random.uniform(*cfg['aperture'])
        }
    
    def randomize_materials(self, material_name: str) -> Dict:
        """Randomize material appearance"""
        cfg = self.randomization_config['materials']
        
        # Base material properties
        base = {
            'plastic': (0.8, 0.5, 0.0),      # (albedo, roughness, metallic)
            'metal': (0.3, 0.3, 1.0),
            'rubber': (0.05, 0.8, 0.0),
            'concrete': (0.7, 0.6, 0.0)
        }
        
        base_props = base.get(material_name, (0.5, 0.5, 0.0))
        
        # Add variation
        varied = (
            np.clip(base_props[0] + random.uniform(-cfg['albedo_variation'], 
                                                    cfg['albedo_variation']), 0, 1),
            np.clip(base_props[1] + random.uniform(-cfg['roughness_variation'],
                                                    cfg['roughness_variation']), 0, 1),
            np.clip(base_props[2] + random.uniform(-cfg['metallic_variation'],
                                                    cfg['metallic_variation']), 0, 1)
        )
        
        return {
            'albedo': varied[0],
            'roughness': varied[1],
            'metallic': varied[2]
        }
    
    def randomize_object_pose(self, initial_pos: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Randomize object position and rotation
        
        Returns:
            (position, rotation_euler)
        """
        cfg = self.randomization_config['objects']
        
        # Position noise
        noise = np.random.normal(0, cfg['position_noise'], 3)
        new_pos = initial_pos + noise
        
        # Rotation jitter
        rotation = np.random.uniform(*cfg['rotation_jitter'], 3)
        
        return new_pos, rotation
    
    def randomize_physics(self) -> Dict:
        """Randomize physics parameters"""
        cfg = self.randomization_config['dynamics']
        
        return {
            'gravity': random.uniform(*cfg['gravity']),
            'friction': random.uniform(*cfg['friction']),
            'restitution': random.uniform(*cfg['restitution'])
        }
    
    def randomize_weather(self) -> Dict:
        """Randomize weather conditions"""
        cfg = self.randomization_config['weather']
        
        weather = {}
        
        if random.random() < cfg['rain']['probability']:
            weather['rain'] = {
                'enabled': True,
                'intensity': random.uniform(*cfg['rain']['intensity'])
            }
        
        if random.random() < cfg['fog']['probability']:
            weather['fog'] = {
                'enabled': True,
                'density': random.uniform(*cfg['fog']['density'])
            }
        
        if random.random() < cfg['snow']['probability']:
            weather['snow'] = {'enabled': True}
        
        return weather
    
    def apply_randomization(self, world):
        """Apply all randomizations to world"""
        randomization = {
            'lighting': self.randomize_lighting(),
            'camera': self.randomize_camera(),
            'physics': self.randomize_physics(),
            'weather': self.randomize_weather()
        }
        
        # Apply to Isaac Sim scene
        # Implementation depends on Isaac Sim API
        
        return randomization
```

## Automated Data Collection

### Data Generation Pipeline

```python
"""
Automated data collection from Isaac Sim
"""

import os
import json
import numpy as np
from pathlib import Path
from datetime import datetime

class IsaacSimDataCollector:
    """
    Collect synthetic datasets from Isaac Sim
    """
    
    def __init__(self, output_dir: str, num_images: int = 100000):
        self.output_dir = Path(output_dir)
        self.num_images = num_images
        self.frame_count = 0
        
        # Create directory structure
        self._create_directories()
        self.randomizer = DomainRandomizer()
        self.metadata = []
    
    def _create_directories(self):
        """Create output directory structure"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        (self.output_dir / 'images').mkdir(exist_ok=True)
        (self.output_dir / 'depth').mkdir(exist_ok=True)
        (self.output_dir / 'segmentation').mkdir(exist_ok=True)
        (self.output_dir / 'normals').mkdir(exist_ok=True)
        (self.output_dir / 'annotations').mkdir(exist_ok=True)
        (self.output_dir / 'metadata').mkdir(exist_ok=True)
    
    def collect_batch(self, world, robots, cameras, num_frames: int = 100):
        """
        Collect a batch of data
        
        Args:
            world: Isaac Sim world
            robots: List of robot objects
            cameras: List of camera sensors
            num_frames: Number of frames to collect
        """
        batch_data = []
        
        for frame_idx in range(num_frames):
            # Apply randomization
            randomization = self.randomizer.apply_randomization(world)
            
            # Randomize robot configuration
            for robot in robots:
                self._randomize_robot_pose(robot)
            
            # Step simulation
            world.step(render=True)
            
            # Collect data from all cameras
            for camera in cameras:
                rgb_image = camera.get_rgb()
                depth_image = camera.get_depth()
                segmentation = camera.get_instance_segmentation()
                normals = camera.get_normals()
                
                # Save images
                frame_data = self._save_frame(
                    frame_idx,
                    rgb_image,
                    depth_image,
                    segmentation,
                    normals,
                    randomization
                )
                batch_data.append(frame_data)
                self.frame_count += 1
        
        return batch_data
    
    def _randomize_robot_pose(self, robot):
        """Randomize robot configuration"""
        # Random joint angles
        dof = robot.get_dof()
        joint_targets = np.random.uniform(-1, 1, dof)
        robot.set_joint_targets(joint_targets)
    
    def _save_frame(self, frame_idx: int, rgb, depth, seg, normals, 
                   randomization: Dict) -> Dict:
        """
        Save frame and create metadata
        
        Returns:
            Metadata dictionary for this frame
        """
        # Create filenames
        frame_id = f"{self.frame_count:06d}"
        
        # Save images
        rgb_path = self.output_dir / 'images' / f"{frame_id}.png"
        depth_path = self.output_dir / 'depth' / f"{frame_id}.npz"
        seg_path = self.output_dir / 'segmentation' / f"{frame_id}.png"
        normals_path = self.output_dir / 'normals' / f"{frame_id}.png"
        
        # Save RGB (JPEG)
        import cv2
        cv2.imwrite(str(rgb_path), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        
        # Save depth (compressed numpy)
        np.savez_compressed(depth_path, depth=depth)
        
        # Save segmentation
        cv2.imwrite(str(seg_path), seg)
        
        # Save normals
        cv2.imwrite(str(normals_path), 
                   ((normals + 1) * 127).astype(np.uint8))
        
        # Create metadata
        metadata = {
            'frame_id': self.frame_count,
            'timestamp': datetime.now().isoformat(),
            'rgb_path': str(rgb_path.relative_to(self.output_dir)),
            'depth_path': str(depth_path.relative_to(self.output_dir)),
            'segmentation_path': str(seg_path.relative_to(self.output_dir)),
            'normals_path': str(normals_path.relative_to(self.output_dir)),
            'randomization': randomization,
            'image_size': rgb.shape[:2],
            'depth_range': [float(depth.min()), float(depth.max())]
        }
        
        self.metadata.append(metadata)
        
        return metadata
    
    def save_metadata(self):
        """Save all metadata to JSON"""
        metadata_path = self.output_dir / 'metadata' / 'all_frames.json'
        
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Save dataset summary
        summary = {
            'total_frames': len(self.metadata),
            'timestamp_created': datetime.now().isoformat(),
            'randomization_config': self.randomizer.randomization_config
        }
        
        summary_path = self.output_dir / 'dataset_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def generate_full_dataset(self, world, robots, cameras):
        """Generate complete dataset"""
        batch_size = 1000
        num_batches = self.num_images // batch_size
        
        for batch_idx in range(num_batches):
            print(f"Generating batch {batch_idx + 1}/{num_batches}")
            self.collect_batch(world, robots, cameras, batch_size)
        
        # Save metadata
        self.save_metadata()
        print(f"Dataset generation complete. Total frames: {self.frame_count}")
```

### Automatic Annotation

```python
"""
Automatic annotation in Isaac Sim
"""

class AnnotationGenerator:
    """Generate ground truth annotations"""
    
    @staticmethod
    def generate_segmentation(world, instance_segmentation):
        """
        Convert instance segmentation to semantic segmentation
        """
        # Map instance IDs to semantic classes
        semantic_classes = {
            'robot': 1,
            'gripper': 2,
            'object': 3,
            'table': 4,
            'wall': 5,
            'background': 0
        }
        
        semantic_mask = np.zeros_like(instance_segmentation)
        
        # This would iterate through objects and assign classes
        return semantic_mask
    
    @staticmethod
    def generate_bounding_boxes(segmentation, camera_intrinsics):
        """
        Generate 2D bounding boxes from segmentation
        
        Returns:
            List of bounding boxes: [x1, y1, x2, y2, class_id]
        """
        from scipy import ndimage
        
        boxes = []
        
        # Find connected components
        labeled, num_features = ndimage.label(segmentation > 0)
        
        for obj_id in range(1, num_features + 1):
            mask = labeled == obj_id
            
            # Get bounding box
            y_coords, x_coords = np.where(mask)
            
            if len(x_coords) > 0:
                x1, x2 = x_coords.min(), x_coords.max()
                y1, y2 = y_coords.min(), y_coords.max()
                
                boxes.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'class_id': obj_id,
                    'area': np.sum(mask)
                })
        
        return boxes
    
    @staticmethod
    def generate_3d_annotations(world, camera):
        """
        Generate 3D annotations (object positions, poses)
        """
        annotations_3d = []
        
        # Get all objects in scene
        for obj in world.get_all_objects():
            pos = obj.get_position()
            rot = obj.get_rotation()
            
            # Convert to camera frame
            cam_pos = camera.get_position()
            cam_rot = camera.get_rotation()
            
            # Transform to camera coordinates
            relative_pos = pos - cam_pos
            
            annotations_3d.append({
                'object_id': obj.name,
                'position': pos.tolist(),
                'rotation': rot.tolist(),
                'position_in_camera_frame': relative_pos.tolist()
            })
        
        return annotations_3d
```

## Dataset Organization and Format

### COCO Format for Detection

```python
"""
Generate dataset in COCO format for object detection
"""

class COCODatasetGenerator:
    """Generate COCO-format dataset for detection"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.coco_data = {
            'info': {
                'description': 'Synthetic robot dataset',
                'version': '1.0',
                'year': 2024,
                'date_created': datetime.now().isoformat()
            },
            'images': [],
            'annotations': [],
            'categories': []
        }
        self.category_id_map = {}
        self.annotation_id = 0
        self.image_id = 0
    
    def add_category(self, category_name: str, category_id: int):
        """Add annotation category"""
        self.coco_data['categories'].append({
            'id': category_id,
            'name': category_name,
            'supercategory': 'object'
        })
        self.category_id_map[category_name] = category_id
    
    def add_image(self, image_path: str, width: int, height: int):
        """Add image entry"""
        self.coco_data['images'].append({
            'id': self.image_id,
            'file_name': image_path,
            'width': width,
            'height': height
        })
        return self.image_id
    
    def add_annotation(self, image_id: int, category: str, 
                      bbox: List[float], area: float):
        """
        Add bounding box annotation
        
        Args:
            image_id: Image ID
            category: Object category name
            bbox: [x, y, width, height]
            area: Bounding box area
        """
        self.coco_data['annotations'].append({
            'id': self.annotation_id,
            'image_id': image_id,
            'category_id': self.category_id_map[category],
            'bbox': bbox,
            'area': area,
            'iscrowd': 0
        })
        self.annotation_id += 1
    
    def save(self):
        """Save COCO dataset"""
        output_path = self.output_dir / 'annotations.json'
        with open(output_path, 'w') as f:
            json.dump(self.coco_data, f, indent=2)
```

## Synthetic Data Validation

```python
"""
Validate synthetic data quality
"""

class DatasetValidator:
    """Validate synthetic dataset"""
    
    @staticmethod
    def check_data_distribution(metadata_list: List[Dict]):
        """Check distribution of randomization parameters"""
        import matplotlib.pyplot as plt
        
        lightings = [m['randomization']['lighting']['intensity'] 
                    for m in metadata_list]
        
        plt.figure(figsize=(10, 4))
        plt.hist(lightings, bins=50)
        plt.xlabel('Lighting Intensity')
        plt.ylabel('Frequency')
        plt.title('Distribution of Lighting in Dataset')
        plt.savefig('lighting_distribution.png')
        plt.close()
    
    @staticmethod
    def validate_annotation_coverage(dataset_path: str):
        """
        Verify that annotations cover all objects
        """
        with open(dataset_path / 'annotations.json', 'r') as f:
            coco = json.load(f)
        
        # Statistics
        print(f"Total images: {len(coco['images'])}")
        print(f"Total annotations: {len(coco['annotations'])}")
        print(f"Categories: {len(coco['categories'])}")
        
        # Check distribution
        category_counts = {}
        for ann in coco['annotations']:
            cat_id = ann['category_id']
            category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
        
        print("\nAnnotations per category:")
        for cat in coco['categories']:
            count = category_counts.get(cat['id'], 0)
            print(f"  {cat['name']}: {count}")
```

## Summary

Synthetic data generation with domain randomization is the key to building robust AI models for robotics. By carefully varying simulation parameters and automatically collecting diverse data, we can train models that transfer well to real-world scenarios.

## Key Takeaways

- Domain randomization creates diversity without real-world data collection
- Automatic annotation eliminates manual labeling effort
- Synthetic datasets can be millions of images in hours
- COCO format enables standard tooling and benchmarking
- Validation ensures dataset quality and coverage
- Sim-to-real transfer requires careful parameter selection
- Large-scale parallelization makes synthetic data cost-effective