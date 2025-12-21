# Chapter 3: Cognitive Planning with Large Language Models

## Introduction

Large Language Models (LLMs) excel at breaking down complex natural language instructions into structured task plans. This chapter explores how to leverage LLMs for cognitive planning, converting high-level goals like "Clean the room" into detailed action sequences executable by robots.

## LLM-Based Planning Architecture

### Planning Pipeline

```
Natural Language Goal
│ "Clean the messy corner"
│
▼
LLM Scene Understanding
├─ What does "clean" mean?
├─ Where is the "corner"?
├─ What needs to be cleaned?
└─ What are the constraints?
│
▼
Task Decomposition
├─ Main objective
├─ Subtasks
├─ Dependencies
└─ Execution order
│
▼
Action Sequence Generation
├─ Primitive actions
├─ Parameters
├─ Safety checks
└─ Fallback strategies
│
▼
ROS 2 Execution
├─ Action dispatch
├─ Monitoring
├─ Error recovery
└─ Feedback loop
```

## Setting Up LLM Integration

### LLM Options

```
Provider        Model              Speed      Cost       Quality
────────────────────────────────────────────────────────────────
OpenAI          GPT-4 Turbo       Medium     $$$$       Excellent
                GPT-3.5 Turbo     Fast       $$         Good
Google          Gemini Pro        Medium     $$$        Excellent
Anthropic       Claude 3          Medium     $$$$       Excellent
Meta            Llama 2           Slow*      Free       Good
Mistral         Mistral 7B        Medium*    $          Good
Local           Ollama            Slow       Free       Varies

* With local GPU
```

### Installation

```bash
#!/bin/bash
# Install LLM libraries

# OpenAI
pip install openai

# Anthropic Claude
pip install anthropic

# Google Gemini
pip install google-generativeai

# For local models
pip install ollama
pip install llama-cpp-python
```

## Building a Planning Agent

### Core Planning Module

```python
"""
Cognitive planning using LLMs
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import json

@dataclass
class ActionStep:
    """Single action in a plan"""
    action: str
    parameters: Dict
    description: str
    expected_duration: float  # seconds
    safety_constraints: List[str]

@dataclass
class TaskPlan:
    """Complete task plan"""
    goal: str
    steps: List[ActionStep]
    total_duration: float
    prerequisites: List[str]
    contingencies: Dict[str, List[ActionStep]]

class CognitivePlannerLLM:
    """
    Use LLMs for task planning
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize planning agent
        
        Args:
            model_name: "gpt-4", "gpt-3.5-turbo", "claude-3", etc
        """
        self.model_name = model_name
        self.llm_client = self._initialize_llm(model_name)
        
        # Robot capability description
        self.robot_capabilities = self._describe_robot_capabilities()
    
    def _initialize_llm(self, model_name: str):
        """Initialize LLM client"""
        if "gpt" in model_name:
            from openai import OpenAI
            return OpenAI()
        elif "claude" in model_name:
            from anthropic import Anthropic
            return Anthropic()
        else:
            raise ValueError(f"Unknown model: {model_name}")
    
    def _describe_robot_capabilities(self) -> str:
        """Describe what robot can do"""
        capabilities = """
        Robot Capabilities:
        
        Movement:
        - walk(distance_m, direction)
        - move_arm_to(position_x, position_y, position_z)
        - rotate_base(angle_degrees)
        
        Manipulation:
        - grasp(object_name)
        - release(object_name)
        - push(object_name, direction, force)
        
        Perception:
        - identify_objects() -> List[Object]
        - locate_object(object_name) -> Position
        - describe_scene() -> str
        
        Navigation:
        - navigate_to(location_name)
        - find_path_to(target)
        
        Constraints:
        - Cannot lift >10kg
        - Gripper opening: 0-10cm
        - Reachable space: 2m radius
        - Max walking speed: 1.5 m/s
        - Cannot navigate stairs (bipedal model)
        """
        return capabilities
    
    def plan(self, goal: str, scene_description: str = None,
            constraints: List[str] = None) -> TaskPlan:
        """
        Generate plan for goal
        
        Args:
            goal: High-level goal ("Pick up all the trash")
            scene_description: Description of current environment
            constraints: Additional constraints (safety, time, etc)
        
        Returns:
            TaskPlan with detailed action steps
        """
        
        # Build prompt
        prompt = self._build_planning_prompt(
            goal, scene_description, constraints
        )
        
        # Get LLM response
        response = self._query_llm(prompt)
        
        # Parse response into structured plan
        plan = self._parse_plan_response(response, goal)
        
        return plan
    
    def _build_planning_prompt(self, goal: str, scene: Optional[str],
                              constraints: Optional[List[str]]) -> str:
        """Build detailed prompt for planning"""
        
        prompt = f"""
You are a task planning agent for a humanoid robot. Your job is to break down 
high-level goals into specific, executable actions.

{self.robot_capabilities}

GOAL: {goal}
"""
        
        if scene:
            prompt += f"\nCURRENT SCENE:\n{scene}\n"
        
        if constraints:
            prompt += f"\nCONSTRAINTS:\n"
            for constraint in constraints:
                prompt += f"- {constraint}\n"
        
        prompt += """
Generate a step-by-step plan. Format each step as JSON:
{{
    "action": "action_name",
    "parameters": {{"param": "value"}},
    "description": "human readable description",
    "expected_duration_seconds": 5,
    "safety_constraints": ["constraint1", "constraint2"]
}}

Consider:
1. Preconditions for each action
2. Error recovery (what if action fails?)
3. Safety (avoid collisions, respect limits)
4. Efficiency (minimize steps, parallel actions where possible)

Provide the complete plan:
"""
        return prompt
    
    def _query_llm(self, prompt: str) -> str:
        """Query LLM with prompt"""
        if "gpt" in self.model_name:
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Low temperature for deterministic output
                max_tokens=2000
            )
            return response.choices[0].message.content
        
        elif "claude" in self.model_name:
            response = self.llm_client.messages.create(
                model=self.model_name,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
    
    def _parse_plan_response(self, response: str, goal: str) -> TaskPlan:
        """Parse LLM response into TaskPlan"""
        
        steps = []
        total_duration = 0
        
        # Extract JSON objects from response
        import re
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        
        matches = re.findall(json_pattern, response)
        
        for match in matches:
            try:
                step_dict = json.loads(match)
                
                step = ActionStep(
                    action=step_dict.get('action', ''),
                    parameters=step_dict.get('parameters', {}),
                    description=step_dict.get('description', ''),
                    expected_duration=step_dict.get('expected_duration_seconds', 0),
                    safety_constraints=step_dict.get('safety_constraints', [])
                )
                
                steps.append(step)
                total_duration += step.expected_duration
                
            except json.JSONDecodeError:
                continue
        
        plan = TaskPlan(
            goal=goal,
            steps=steps,
            total_duration=total_duration,
            prerequisites=[],
            contingencies={}
        )
        
        return plan
    
    def refine_plan(self, plan: TaskPlan, feedback: str) -> TaskPlan:
        """
        Refine plan based on feedback
        
        Args:
            plan: Current plan
            feedback: User feedback or execution error
        
        Returns:
            Refined plan
        """
        prompt = f"""
Current plan for '{plan.goal}':
{json.dumps([step.__dict__ for step in plan.steps], indent=2)}

Feedback/Error:
{feedback}

Please refine the plan to address the feedback.
"""
        
        response = self._query_llm(prompt)
        refined_plan = self._parse_plan_response(response, plan.goal)
        
        return refined_plan
```

## Advanced Reasoning Capabilities

### Few-Shot Prompting

```python
"""
Improve LLM planning with examples
"""

class FewShotPlanner(CognitivePlannerLLM):
    """Planner with few-shot examples"""
    
    def __init__(self, model_name: str = "gpt-4"):
        super().__init__(model_name)
        self.examples = self._load_planning_examples()
    
    def _load_planning_examples(self) -> List[Dict]:
        """Load few-shot examples"""
        examples = [
            {
                'goal': 'Pick up the red cup from the table',
                'plan': [
                    {
                        'action': 'move_arm_to',
                        'parameters': {'x': 0.5, 'y': 0.2, 'z': 0.8},
                        'description': 'Move arm to pre-grasp position above cup'
                    },
                    {
                        'action': 'grasp',
                        'parameters': {'object': 'red_cup'},
                        'description': 'Close gripper around cup'
                    },
                    {
                        'action': 'move_arm_to',
                        'parameters': {'x': 0.3, 'y': 0.3, 'z': 1.0},
                        'description': 'Lift cup to safe height'
                    }
                ]
            },
            {
                'goal': 'Navigate to the kitchen and get a glass of water',
                'plan': [
                    {
                        'action': 'navigate_to',
                        'parameters': {'location': 'kitchen'},
                        'description': 'Walk to kitchen'
                    },
                    {
                        'action': 'identify_objects',
                        'parameters': {'target_class': 'cup'},
                        'description': 'Look for cups in kitchen'
                    },
                    {
                        'action': 'grasp',
                        'parameters': {'object': 'cup'},
                        'description': 'Pick up a cup'
                    }
                ]
            }
        ]
        return examples
    
    def _build_planning_prompt(self, goal: str, scene: Optional[str],
                              constraints: Optional[List[str]]) -> str:
        """Include examples in prompt"""
        
        base_prompt = super()._build_planning_prompt(goal, scene, constraints)
        
        examples_text = "EXAMPLES:\n\n"
        for i, example in enumerate(self.examples):
            examples_text += f"Example {i+1}: {example['goal']}\n"
            examples_text += "Plan:\n"
            for step in example['plan']:
                examples_text += f"  - {step['description']}\n"
                examples_text += f"    Action: {step['action']}\n"
                examples_text += f"    Parameters: {step['parameters']}\n"
            examples_text += "\n"
        
        return examples_text + "\n" + base_prompt
```

### Chain-of-Thought Reasoning

```python
"""
Improve planning with chain-of-thought reasoning
"""

class ChainOfThoughtPlanner(CognitivePlannerLLM):
    """Use chain-of-thought to improve reasoning"""
    
    def plan(self, goal: str, scene_description: str = None,
            constraints: List[str] = None) -> TaskPlan:
        """Plan with explicit reasoning steps"""
        
        # Step 1: Analyze goal
        goal_analysis = self._analyze_goal(goal)
        self.get_logger().info(f"Goal Analysis:\n{goal_analysis}")
        
        # Step 2: Identify preconditions
        preconditions = self._identify_preconditions(goal, scene_description)
        self.get_logger().info(f"Preconditions:\n{preconditions}")
        
        # Step 3: Plan main sequence
        main_sequence = self._plan_main_sequence(
            goal, preconditions, scene_description
        )
        
        # Step 4: Add safety checks
        safe_sequence = self._add_safety_checks(main_sequence)
        
        # Step 5: Plan contingencies
        contingencies = self._plan_contingencies(safe_sequence)
        
        plan = TaskPlan(
            goal=goal,
            steps=safe_sequence,
            total_duration=sum(s.expected_duration for s in safe_sequence),
            prerequisites=preconditions,
            contingencies=contingencies
        )
        
        return plan
    
    def _analyze_goal(self, goal: str) -> str:
        """Analyze what goal requires"""
        prompt = f"""
Analyze this goal: "{goal}"

What does this goal require?
1. What objects are involved?
2. What are the success criteria?
3. What could go wrong?
4. What preconditions must be met?
"""
        return self._query_llm(prompt)
    
    def _identify_preconditions(self, goal: str, 
                               scene: Optional[str]) -> List[str]:
        """Identify what must be true before planning"""
        prompt = f"""
Goal: {goal}
{f"Scene: {scene}" if scene else ""}

What preconditions must be satisfied?
List as bullet points.
"""
        response = self._query_llm(prompt)
        
        # Parse bullet points
        preconditions = [line.strip('- ') for line in response.split('\n') 
                        if line.strip().startswith('-')]
        return preconditions
    
    def _plan_main_sequence(self, goal: str, preconditions: List[str],
                           scene: Optional[str]) -> List[ActionStep]:
        """Plan the main action sequence"""
        # Implementation similar to plan()
        pass
    
    def _add_safety_checks(self, sequence: List[ActionStep]
                          ) -> List[ActionStep]:
        """Add safety validation steps"""
        # Check for collisions, joint limits, etc
        pass
    
    def _plan_contingencies(self, sequence: List[ActionStep]) -> Dict:
        """Plan recovery strategies"""
        contingencies = {}
        
        for i, step in enumerate(sequence):
            prompt = f"""
Step {i}: {step.description}
Action: {step.action}

What could go wrong with this step?
How should the robot recover if it fails?
"""
            recovery = self._query_llm(prompt)
            contingencies[step.action] = recovery
        
        return contingencies
```

## ROS 2 Planning Node

```python
"""
ROS 2 node for cognitive planning
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Pose

class PlanningNode(Node):
    """
    ROS 2 node for LLM-based planning
    """
    
    def __init__(self):
        super().__init__('planning_node')
        
        # Initialize planner
        self.planner = FewShotPlanner(model_name="gpt-4")
        
        # Subscribers
        self.goal_sub = self.create_subscription(
            String, '/robot/goal',
            self.on_goal, 10
        )
        
        self.feedback_sub = self.create_subscription(
            String, '/robot/feedback',
            self.on_feedback, 10
        )
        
        # Publishers
        self.plan_pub = self.create_publisher(
            String, '/robot/plan', 10
        )
        
        self.status_pub = self.create_publisher(
            String, '/robot/planning_status', 10
        )
        
        # State
        self.current_plan = None
        self.current_goal = None
        
        self.get_logger().info('Planning Node initialized')
    
    def on_goal(self, msg):
        """Receive new goal"""
        goal = msg.data
        self.current_goal = goal
        
        self.get_logger().info(f'Received goal: {goal}')
        
        # Generate plan
        self.generate_plan(goal)
    
    def on_feedback(self, msg):
        """Receive feedback about execution"""
        feedback = msg.data
        
        self.get_logger().info(f'Received feedback: {feedback}')
        
        # Refine plan if needed
        if 'failed' in feedback.lower() or 'error' in feedback.lower():
            self.refine_plan(feedback)
    
    def generate_plan(self, goal: str):
        """Generate plan for goal"""
        try:
            self.status_pub.publish(String(data="planning"))
            
            # Get scene description
            scene = self._get_scene_description()
            
            # Generate plan
            plan = self.planner.plan(
                goal=goal,
                scene_description=scene,
                constraints=self._get_constraints()
            )
            
            self.current_plan = plan
            
            # Publish plan
            plan_json = self._plan_to_json(plan)
            self.plan_pub.publish(String(data=plan_json))
            
            self.status_pub.publish(String(data="ready"))
            
            self.get_logger().info(f'Plan generated: {len(plan.steps)} steps')
            
        except Exception as e:
            self.get_logger().error(f'Planning failed: {e}')
            self.status_pub.publish(String(data="error"))
    
    def refine_plan(self, feedback: str):
        """Refine current plan based on feedback"""
        if self.current_plan is None:
            return
        
        try:
            refined_plan = self.planner.refine_plan(
                self.current_plan, feedback
            )
            
            self.current_plan = refined_plan
            
            # Publish refined plan
            plan_json = self._plan_to_json(refined_plan)
            self.plan_pub.publish(String(data=plan_json))
            
        except Exception as e:
            self.get_logger().error(f'Plan refinement failed: {e}')
    
    def _get_scene_description(self) -> str:
        """Get description of current scene"""
        # This would query perception system
        return "Robot is in living room. Table with objects. Floor clear."
    
    def _get_constraints(self) -> List[str]:
        """Get operational constraints"""
        return [
            "Avoid moving objects other than targets",
            "Do not approach humans within 1m",
            "Maintain stability (no dynamic movements)",
            "Complete task within 5 minutes"
        ]
    
    def _plan_to_json(self, plan: TaskPlan) -> str:
        """Convert plan to JSON string"""
        import json
        
        plan_dict = {
            'goal': plan.goal,
            'total_duration': plan.total_duration,
            'steps': [
                {
                    'action': step.action,
                    'parameters': step.parameters,
                    'description': step.description,
                    'expected_duration': step.expected_duration,
                    'safety_constraints': step.safety_constraints
                }
                for step in plan.steps
            ]
        }
        
        return json.dumps(plan_dict, indent=2)

def main(args=None):
    rclpy.init(args=args)
    node = PlanningNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Summary

LLM-based cognitive planning enables robots to handle complex, underspecified goals through natural language. By leveraging the reasoning capabilities of models like GPT-4 and Claude, we can decompose high-level instructions into executable action sequences while considering safety, efficiency, and error recovery.

## Key Takeaways

- LLMs provide powerful reasoning for task decomposition
- Chain-of-thought prompting improves plan quality
- Few-shot examples guide LLM behavior
- Structured output parsing ensures reliable execution
- Plan refinement enables adaptation to failures
- ROS 2 integration enables robot-agnostic execution
- Safety constraints must be explicitly specified
- Confidence and error handling are critical