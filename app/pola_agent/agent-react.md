This is a brilliant practical application. You are moving from a **"single-script pipeline"** to a **"conversational AI agent"** that can dynamically interact with the user. 

The workflow you described (Crop → Confirm → Shift → Analyze) is a perfect use case for a **LangChain ReAct Agent**. ReAct (Reasoning + Acting) allows the LLM to decide which tool to use, observe the result, and decide the next step in a loop.

Here is exactly how to design, implement, and integrate your existing tools into this agent.

---

### 🧠 The Agent's Toolset (The "Brain")

We need to wrap your existing functions into LangChain `BaseTool` objects. 

| Tool Name | Purpose | Input |
| :--- | :--- | :--- |
| **Crop Tool** | Scans a long video, detects start/end frames of the trick using your algorithm (e.g., motion detection). | `video_path` |
| **Shift & Trim Tool** | Uses `ffmpeg` to cut the video again, adjusting the start time by X seconds forward or backward. | `video_path`, `shift_seconds` |
| **Histogram Analyzer** | This is the **super-tool** we designed earlier. It takes the cropped video, runs MediaPipe, detects phases, calculates Z-scores, finds the critical frame, and calls the LLM for feedback. | `video_path` |

---

### 🏗️ Step 1: Implement the Tools in LangChain Format

Here is how you wrap them. Note how the **Confirmation** step is handled inside the agent's reasoning loop, not as a tool.

```python
import subprocess
import json
from typing import Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# --- Tool 1: Crop Detection (Your existing logic) ---
class CropInput(BaseModel):
    video_path: str = Field(description="Path to the long raw video file.")

class CropTool(BaseTool):
    name: str = "CropVideo"
    description: str = "Scans a long video file to detect where the pole trick starts and ends. Returns the start and end timestamps in seconds."
    args_schema: Type[BaseModel] = CropInput

    def _run(self, video_path: str) -> str:
        # >>> INSERT YOUR EXISTING CROP ALGORITHM HERE <<<
        # Example: detect motion in MediaPipe hip coordinates
        start_time = 12.5  # e.g., your algorithm finds it starts at 12.5s
        end_time = 17.8    # ends at 17.8s
        return json.dumps({
            "status": "success",
            "start": start_time,
            "end": end_time,
            "duration": end_time - start_time,
            "suggested_output": f"cropped_{video_path}"
        })

# --- Tool 2: Shift / Re-trim (FFMPEG wrapper) ---
class ShiftInput(BaseModel):
    video_path: str = Field(description="Path to the originally cropped video file.")
    shift_seconds: float = Field(description="Seconds to shift the start time. Positive moves forward, negative moves backward.")
    current_start: float = Field(description="The current start time of the cropped clip from the CropTool.")

class ShiftTool(BaseTool):
    name: str = "ShiftVideo"
    description: str = "Uses ffmpeg to shift the start time of a previously cropped video by X seconds. Useful if the user says 'the trick starts 1 second later'."
    args_schema: Type[BaseModel] = ShiftInput

    def _run(self, video_path: str, shift_seconds: float, current_start: float) -> str:
        new_start = max(0, current_start + shift_seconds)
        
        # FFMPEG command to re-cut
        # Example: ffmpeg -ss {new_start} -i original_long_video.mp4 -t {duration} -c copy shifted_output.mp4
        # (Note: You need to know the original long video path or pass it)
        
        output_path = f"shifted_{shift_seconds}_{video_path}"
        command = [
            "ffmpeg", "-ss", str(new_start), 
            "-i", "original_long_video.mp4", 
            "-t", "5",  # Calculate duration dynamically
            "-c", "copy", output_path
        ]
        # subprocess.run(command, check=True)
        
        return json.dumps({
            "status": "success",
            "new_start": new_start,
            "output_video": output_path,
            "message": f"Video shifted by {shift_seconds} seconds. New start at {new_start}s."
        })

# --- Tool 3: The Histogram Analyzer (The Super Tool from previous steps) ---
class AnalyzeInput(BaseModel):
    video_path: str = Field(description="Path to the final cropped video file (either original crop or shifted).")

class HistogramAnalyzerTool(BaseTool):
    name: str = "AnalyzeTrick"
    description: str = "Analyzes the final cropped pole dance video. Detects Entrance/Execution/Exit, finds the worst technical flaw, generates a histogram plot, and calls the coaching LLM. Returns the feedback."
    args_schema: Type[BaseModel] = AnalyzeInput

    def _run(self, video_path: str) -> str:
        # >>> INSERT THE ENTIRE PIPELINE FROM PREVIOUS STEPS HERE <<<
        # 1. MediaPipe extraction
        # 2. Phase detection
        # 3. Z-score outlier detection
        # 4. Extract frame and plot
        # 5. Call coaching LLM
        
        # For now, a mock response
        return json.dumps({
            "status": "success",
            "phases": {"Entrance": "0s-1.5s", "Execution": "1.5s-4.0s", "Exit": "4.0s-5.2s"},
            "feedback": "Your hips are dropping too early in the Execution phase. Focus on driving your knees up before extending."
        })
```

---

### 🔧 Step 2: Build the ReAct Agent

Now we instantiate the agent with these tools and a custom prompt that instructs it to follow **your exact workflow**.

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Initialize the LLM (use GPT-4 for best reasoning)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Gather tools
tools = [CropTool(), ShiftTool(), HistogramAnalyzerTool()]

# CRITICAL: The prompt that enforces the workflow
template = """You are a helpful Pole Dance Coaching Assistant. You have access to the following tools:

{tools}

You must follow this EXACT workflow for EVERY video:
1. Use `CropVideo` on the user's long video path to detect the trick.
2. Report the found start/end times to the user and ASK if they are correct.
3. If the user says "yes", proceed to step 5.
4. If the user says "shift by X seconds" or "start later", use `ShiftVideo` with the specified seconds. Then repeat the confirmation step.
5. Once the user confirms the crop is perfect, use `AnalyzeTrick` on the final video path to get the coaching feedback.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Important: If you have a crop result and ask the user for confirmation, you MUST wait for their response in the next User Input before proceeding.

Begin!

Previous conversation history:
{chat_history}

Question: {input}
{agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

# Create the agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True,
    max_iterations=10
)
```

---

### 💬 Step 3: The Interactive Loop (Handling the "Confirmation")

The hardest part is the **user confirmation** step, because the agent needs to "pause" and ask a question. 

**Option A (Recommended for simplicity)**: The `ShiftTool` returns a string like `"The video currently starts at 12.5s. Do you want to shift it? Please respond with 'yes' or 'shift by X'."` The main application loop can handle this by passing the user's reply back into the `AgentExecutor` with the `chat_history`.

Here is how to manage the conversation state:

```python
import os

def run_agent_conversation(initial_user_input):
    chat_history = []
    
    # Initialize the first input
    current_input = initial_user_input
    final_answer = None
    
    # This simulates a conversation loop
    while True:
        response = agent_executor.invoke({
            "input": current_input,
            "chat_history": "\n".join(chat_history)
        })
        
        output = response['output']
        print(f"Agent: {output}")
        
        # Check if the agent is asking a question (contains a "?")
        if "?" in output and "shift" in output.lower():
            # The agent is asking for confirmation. Get user input.
            user_reply = input("You: ")
            chat_history.append(f"User: {current_input}")
            chat_history.append(f"Assistant: {output}")
            # The user's reply becomes the next input for the agent
            current_input = user_reply
        else:
            # If no question, the agent is done (or it's just a statement)
            # We assume it's the final answer if it contains "feedback".
            if "feedback" in output.lower() or "analysis" in output.lower():
                final_answer = output
                break
            else:
                # If it's a generic statement, we ask the user what to do next.
                user_reply = input("You: ")
                chat_history.append(f"User: {current_input}")
                chat_history.append(f"Assistant: {output}")
                current_input = user_reply
    
    return final_answer

# Start the conversation
user_query = "I have a long video called 'practice_1.mp4'. Please analyze my pole trick."
run_agent_conversation(user_query)
```

---

### 🔥 Step 4: The Magic of ReAct Reasoning (How it looks in real-time)

Here is exactly how the agent will think and act with your tools:

**Agent Thought**: *"The user provided 'practice_1.mp4'. I must first crop it to find the exact trick."*
**Agent Action**: `CropVideo`
**Action Input**: `{"video_path": "practice_1.mp4"}`
**Observation**: `{"start": 12.5, "end": 17.8, "suggested_output": "cropped_practice_1.mp4"}`

**Agent Thought**: *"I found the crop. Now I need to ask the user if these timings are correct."*
**Final Answer**: `I found your trick starting at 12.5 seconds and ending at 17.8 seconds. Is this correct? If not, tell me how many seconds to shift (e.g., 'shift by 2' or 'start later').`

**[User Input]**: `"shift by -1.5 seconds, it started too early"`

**Agent Thought**: *"The user wants to shift the start earlier by 1.5 seconds. I will use the ShiftVideo tool."*
**Agent Action**: `ShiftVideo`
**Action Input**: `{"video_path": "cropped_practice_1.mp4", "shift_seconds": -1.5, "current_start": 12.5}`
**Observation**: `{"new_start": 11.0, "output_video": "shifted_-1.5_cropped_practice_1.mp4"}`

**Agent Thought**: *"I've shifted the video. I should ask the user to confirm again, or proceed directly if they said it's perfect."*
**Final Answer**: `I have shifted the video to start at 11.0 seconds. Should I proceed with the analysis?`

**[User Input]**: `"Yes, proceed."`

**Agent Thought**: *"The user confirmed. I will now run the full analysis."*
**Agent Action**: `AnalyzeTrick`
**Action Input**: `{"video_path": "shifted_-1.5_cropped_practice_1.mp4"}`
**Observation**: `{"feedback": "Your hips are dropping too early..."}`

**Agent Thought**: *"I have the feedback. I will present it to the user."*
**Final Answer**: `"✅ Analysis complete! Here is your feedback: ..."`

---

### ⚙️ Step 5: Critical Integration Details

1.  **State Management**: The `ShiftTool` needs to know the path to the *original long video* to run FFMPEG. You can pass it as an argument, or better, store it in a global context/dictionary that your tools can access (e.g., using `self.video_store` in the tool).

2.  **FFMPEG Path**: Ensure FFMPEG is in your system PATH or specify the binary path in the subprocess call.

3.  **Error Handling**: Add `try-except` blocks in your tools. If the CropTool fails, the agent should see `"Error: No motion detected"` and ask the user to manually provide timestamps.

4.  **LangChain Agent with Structured Tools**: Since we are using Pydantic schemas, the LLM will correctly format the `Action Input` as a JSON object matching our inputs. 

5.  **Memory**: The `chat_history` is crucial here. Without it, the agent forgets that it already cropped the video. Make sure to pass the history correctly in the loop.

This architecture turns your static `Histogram Analyzer` into a dynamic, conversational coaching bot that can handle mistakes, re-trims, and confirmations, all while using the exact mathematical precision of your MediaPipe pipeline. Do you need me to write the actual `subprocess.run` code for the FFMPEG shifting that preserves quality and handles absolute paths?


