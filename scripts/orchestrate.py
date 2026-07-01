#!/usr/bin/env python3
"""
Orchestrator Agent CLI
Implements the RISEN (Routing, Intent, Schema, Error-handling, Nurturing) framework
for the .pop Agent System.
"""

import os
import sys
import json
import argparse
import datetime
import urllib.request
import urllib.error
import time

# Constants and Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "skills.json")
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
CONTEXT_PATH = os.path.join(MEMORY_DIR, "context.json")
LOG_PATH = os.path.join(MEMORY_DIR, "routing_log.jsonl")

# Ensure directories exist
os.makedirs(MEMORY_DIR, exist_ok=True)

def get_api_key():
    """Retrieves the Gemini API key from environment or .env file."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        env_path = os.path.join(BASE_DIR, ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip("'\" ")
                        break
    return api_key

def call_gemini(contents, system_instruction=None, json_mode=False, model="gemini-2.5-flash"):
    """Makes a request to the Gemini API using urllib."""
    api_key = get_api_key()
    if not api_key:
        print("\n[ERROR] GEMINI_API_KEY is not set. Please set it in your environment or create a .env file.", file=sys.stderr)
        sys.exit(1)
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": contents
    }
    
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    if json_mode:
        payload["generationConfig"] = {
            "responseMimeType": "application/json"
        }
        
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        try:
            parsed_error = json.loads(error_msg)
            message = parsed_error.get("error", {}).get("message", "HTTP Error")
        except Exception:
            message = error_msg
        raise RuntimeError(f"Gemini API HTTP Error {e.code}: {message}")
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Gemini API: {str(e)}")

# Memory and Context Management
def load_context():
    """Loads session context from context.json."""
    if os.path.exists(CONTEXT_PATH):
        try:
            with open(CONTEXT_PATH, "r") as f:
                context = json.load(f)
                # Ensure structure
                if "history" not in context: context["history"] = []
                if "active_skill" not in context: context["active_skill"] = None
                if "confidence_threshold" not in context: context["confidence_threshold"] = 0.80
                return context
        except Exception:
            pass
            
    # Default context
    return {
        "active_skill": None,
        "confidence_threshold": 0.80,
        "history": [],
        "session_count": 1,
        "last_updated": datetime.datetime.now().isoformat()
    }

def save_context(context):
    """Saves session context to context.json."""
    context["last_updated"] = datetime.datetime.now().isoformat()
    with open(CONTEXT_PATH, "w") as f:
        json.dump(context, f, indent=2)

def load_skills():
    """Loads all registered skills from config/skills.json."""
    if not os.path.exists(CONFIG_PATH):
        print(f"\n[ERROR] Configuration file {CONFIG_PATH} not found.", file=sys.stderr)
        return []
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            return data.get("skills", [])
    except Exception as e:
        print(f"\n[ERROR] Failed to parse config/skills.json: {e}", file=sys.stderr)
        return []

def log_routing_decision(input_msg, intent, confidence, chosen_skill, user_overrode):
    """Logs the routing decision to routing_log.jsonl."""
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "input": input_msg,
        "intent": intent,
        "confidence": confidence,
        "chosen_skill": chosen_skill,
        "user_overrode": user_overrode
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# Intent Classification
def classify_intent(query, context, skills):
    """Uses Gemini API to classify the user's intent."""
    skills_list = []
    for s in skills:
        skills_list.append({
            "name": s["name"],
            "description": s["description"],
            "trigger_phrases": s.get("trigger_phrases", [])
        })
        
    skills_json_str = json.dumps(skills_list, indent=2)
    active_skill = context.get("active_skill")
    threshold = context.get("confidence_threshold", 0.80)
    
    # Format history context
    history_turns = []
    # Only supply last 5 turns of history to keep classification prompt compact and relevant
    for turn in context.get("history", [])[-5:]:
        role_label = "User" if turn["role"] == "user" else "Assistant"
        skill_label = f" (Skill: {turn['skill']})" if turn.get("skill") else ""
        history_turns.append(f"{role_label}{skill_label}: {turn['text']}")
    history_str = "\n".join(history_turns) if history_turns else "None"
    
    system_instruction = "You are the intent classifier for the .pop Orchestrator Agent. Return ONLY valid JSON as specified."
    
    prompt = f"""You are the intent classifier for the .pop Orchestrator Agent.
Your job is to analyze the user's input and select the most appropriate skill from the available skills list.
You must also detect if the user explicitly named a skill they want to use in their query (e.g. "use brand_kit to check styling").

Available Skills:
{skills_json_str}

Active Skill Session: {active_skill}
Confidence Threshold: {threshold}

User Input: "{query}"

Recent History Context:
{history_str}

Please classify the intent. You must respond with a raw JSON object and nothing else.
The JSON object must have this exact structure:
{{
  "explicit_skill_named": "skill-name-if-explicitly-mentioned-in-input-else-null",
  "matches": [
    {{
      "skill": "skill-name",
      "confidence": 0.XX
    }}
  ],
  "chain": ["skill-name-1", "skill-name-2"],
  "parameters": {{}}
}}

Instructions:
1. "explicit_skill_named" should be the name of a registered skill only if the user explicitly named it in their query (e.g., "use brand_kit"). Do not guess.
2. "matches" should be a list of matching skills from the Available Skills list, sorted by confidence descending.
3. If no skills match, return an empty "matches" list. If the user request clearly requires a skill that does not exist in the Available Skills list (e.g. "generate an image of a cat"), add it to matches with a low confidence score or return an empty matches list.
4. "chain" is an optional array of skill names if the request explicitly requires executing multiple skills sequentially (e.g., "research topic X and then write a brand guideline"). If not chaining, omit this field or return an empty array.
5. "parameters" can contain any key-value pairs extracted from the input query.
"""

    contents = [{"parts": [{"text": prompt}]}]
    
    try:
        response_text = call_gemini(contents, system_instruction=system_instruction, json_mode=True)
        # Parse the JSON response
        result = json.loads(response_text)
        return result
    except Exception as e:
        # Fallback in case of classification failure
        print(f"\n[WARNING] Intent classification failed: {e}. Falling back to default routing.")
        return {
            "explicit_skill_named": None,
            "matches": [],
            "parameters": {}
        }

# Execution Handoff
def execute_skill(skill_name, query, context, skills, parameters=None):
    """Executes a specialized skill by reading its system prompt and sending to LLM."""
    skill = next((s for s in skills if s["name"] == skill_name), None)
    if not skill:
        raise ValueError(f"Skill '{skill_name}' is not registered.")
        
    skill_file_path = os.path.join(BASE_DIR, skill["file"])
    if not os.path.exists(skill_file_path):
        raise FileNotFoundError(f"Skill file '{skill['file']}' not found at {skill_file_path}")
        
    with open(skill_file_path, "r") as f:
        skill_prompt = f.read()
        
    # Prepare structured payload context for the skill agent
    metadata = {
        "detected_skill": skill_name,
        "confidence": 1.0,  # Execution is confirmed
        "parsed_parameters": parameters or {}
    }
    
    # Filter history for sliding window (last 10 turns relevant to this skill)
    skill_history = [turn for turn in context["history"] if turn.get("skill") == skill_name]
    sliding_window = skill_history[-10:]
    
    # Construct contents list for Gemini API
    api_contents = []
    for turn in sliding_window:
        api_contents.append({
            "role": "user" if turn["role"] == "user" else "model",
            "parts": [{"text": turn["text"]}]
        })
        
    # Build payload description for the skill agent to understand its context
    payload_intro = f"""[SYSTEM CONTEXT FROM ORCHESTRATOR]
You are being invoked with the following metadata:
{json.dumps(metadata, indent=2)}

Original user request:
"{query}"
--------------------------------------------------
"""
    api_contents.append({
        "role": "user",
        "parts": [{"text": payload_intro}]
    })
    
    # Call the LLM with the skill's instructions as system instructions
    response_text = call_gemini(api_contents, system_instruction=skill_prompt)
    return response_text

# Meta-commands handler
def handle_meta_command(cmd, context, skills):
    """Processes system commands starting with '/'."""
    parts = cmd.split(maxsplit=1)
    base_cmd = parts[0].lower()
    
    if base_cmd == "/skills":
        print("\n--- Available Specialized Skills ---")
        for s in skills:
            print(f"- {s['name']}:")
            print(f"  Description: {s['description']}")
            print(f"  Trigger Phrases: {', '.join(s.get('trigger_phrases', []))}")
        print("------------------------------------\n")
        return True
        
    elif base_cmd == "/history":
        print("\n--- Orchestrator Routing History ---")
        if not os.path.exists(LOG_PATH):
            print("No routing history found.")
        else:
            with open(LOG_PATH, "r") as f:
                for line in f:
                    try:
                        log = json.loads(line)
                        ts = log.get("timestamp", "").split("T")[0]
                        user_in = log.get("input", "")[:30] + ("..." if len(log.get("input", "")) > 30 else "")
                        skill = log.get("chosen_skill") or "None"
                        conf = log.get("confidence", 0.0)
                        override = " [Overridden]" if log.get("user_overrode") else ""
                        print(f"[{ts}] Input: '{user_in}' -> Skill: {skill} (Conf: {conf:.2f}){override}")
                    except Exception:
                        pass
        print("------------------------------------\n")
        return True
        
    elif base_cmd == "/threshold":
        if len(parts) < 2:
            print(f"\nCurrent Confidence Threshold: {context.get('confidence_threshold', 0.80):.2f}\n")
            return True
        try:
            val = float(parts[1])
            if 0.0 <= val <= 1.0:
                context["confidence_threshold"] = val
                save_context(context)
                print(f"\nConfidence threshold updated to: {val:.2f}\n")
            else:
                print("\n[ERROR] Threshold must be a float between 0.0 and 1.0.\n")
        except ValueError:
            print("\n[ERROR] Invalid threshold value. Must be a float.\n")
        return True
        
    elif base_cmd == "/reset":
        context["active_skill"] = None
        context["history"] = []
        save_context(context)
        print("\nConversation history and active skill context have been reset.\n")
        return True
        
    return False

# Orchestration Engine
def orchestrate_query(query, context, skills, queue=None):
    """Processes a single query through the orchestrator's RISEN flow."""
    # 1. Check for command
    if query.startswith("/"):
        if handle_meta_command(query, context, skills):
            return
            
    # 2. Add request to context history
    # Keep track of user's query
    user_turn = {
        "role": "user",
        "text": query,
        "skill": context.get("active_skill"),
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # 3. Intent Detection
    classification = classify_intent(query, context, skills)
    explicit_skill = classification.get("explicit_skill_named")
    matches = classification.get("matches", [])
    chain = classification.get("chain", [])
    parameters = classification.get("parameters", {})
    
    threshold = context.get("confidence_threshold", 0.80)
    
    detected_skill = None
    confidence = 0.0
    
    if matches:
        detected_skill = matches[0]["skill"]
        confidence = matches[0]["confidence"]
        
    # Check for chaining/sequential routing
    if chain and len(chain) > 1:
        print(f"\n[still working with Orchestrator]")
        print(f"Got it — sequential execution plan detected: {' -> '.join(chain)}")
        last_output = query
        for i, skill_name in enumerate(chain):
            print(f"\nGot it — sending step {i+1} of {len(chain)} to {skill_name}...")
            # Log decision
            log_routing_decision(query, f"chain_step_{i+1}", 1.0, skill_name, False)
            try:
                # Update user_turn context skill for execution
                user_turn["skill"] = skill_name
                context["history"].append(user_turn)
                
                result = execute_skill(skill_name, last_output, context, skills, parameters)
                
                # Append assistant output
                assistant_turn = {
                    "role": "model",
                    "text": result,
                    "skill": skill_name,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                context["history"].append(assistant_turn)
                context["active_skill"] = skill_name
                save_context(context)
                
                print(f"\n[{skill_name} Agent response]:\n{result}")
                last_output = result
            except Exception as e:
                print(f"\n[ERROR] {skill_name} failed: {e}")
                print("Sequential chain execution aborted.")
                return
        return

    # Check for skill mismatch (User explicit vs LLM detected)
    user_overrode = False
    routing_skill = detected_skill
    
    if explicit_skill and explicit_skill != detected_skill:
        # Check if explicit skill is valid
        is_valid_explicit = any(s["name"] == explicit_skill for s in skills)
        if is_valid_explicit:
            print(f"\n[Orchestrator]: You asked for {explicit_skill}, but this looks like a {detected_skill} task — should I route to {explicit_skill} instead? (yes/no): ", end="")
            sys.stdout.flush()
            ans = sys.stdin.readline().strip().lower()
            if ans in ["yes", "y", ""]:
                routing_skill = explicit_skill
                user_overrode = True
                print(f"Got it — respecting choice. Routing to {explicit_skill}.")
            else:
                routing_skill = detected_skill
                print(f"Got it — routing to recommended skill: {detected_skill}.")
                
    # Handle low confidence (Unclear Intent flow)
    if not user_overrode and confidence < threshold:
        routing_skill = None
        # Check if ambiguous between 2 or 3 skills (confidence of top 2-3 are non-zero)
        plausible_matches = [m for m in matches if m["confidence"] > 0.15][:3]
        
        if len(plausible_matches) in [2, 3]:
            print(f"\n[Orchestrator]: Unclear intent. Please choose from the plausible skills:")
            for idx, match in enumerate(plausible_matches):
                print(f"  {idx + 1}. {match['skill']} (confidence: {match['confidence'] * 100:.0f}%)")
            print("  Other. Describe what you want to do")
            print("Select a number: ", end="")
            sys.stdout.flush()
            ans = sys.stdin.readline().strip()
            try:
                sel_idx = int(ans) - 1
                if 0 <= sel_idx < len(plausible_matches):
                    routing_skill = plausible_matches[sel_idx]["skill"]
                    confidence = plausible_matches[sel_idx]["confidence"]
            except ValueError:
                pass
        else:
            # Completely unclear: list all 4 available skills
            print(f"\n[Orchestrator]: Unclear intent. Please select from all registered skills:")
            for idx, s in enumerate(skills):
                print(f"  {idx + 1}. {s['name']} - {s['description']}")
            print("  Cancel. Cancel request")
            print("Select a number: ", end="")
            sys.stdout.flush()
            ans = sys.stdin.readline().strip()
            try:
                sel_idx = int(ans) - 1
                if 0 <= sel_idx < len(skills):
                    routing_skill = skills[sel_idx]["name"]
                    confidence = 1.0
            except ValueError:
                pass

    # Handle missing/not built skill suggestions
    if not routing_skill:
        # Check if the user query suggests something we can't do
        # E.g. image generation, writing code
        print(f"\n[Orchestrator]: I cannot handle this request. No matching skill exists for this task.")
        if skills:
            suggested = skills[0]["name"]
            print(f"Suggested alternative: You might find the '{suggested}' skill partially helpful.")
        log_routing_decision(query, "unclear_or_missing", confidence, "None", False)
        return

    # Check if active skill session is different (topic shift indicator)
    previous_active_skill = context.get("active_skill")
    if previous_active_skill and previous_active_skill != routing_skill:
        print(f"\n[Orchestrator]: Still working with {previous_active_skill}. Note: switching to {routing_skill}.")
        # Fresh context window for new skill - will isolate history turns
        user_turn["skill"] = routing_skill
    else:
        user_turn["skill"] = routing_skill
        if previous_active_skill:
            print(f"\n[still working with {routing_skill}]")

    # Confirm routing out loud & briefly allow override
    print(f"\n[Orchestrator]: Got it — sending this to {routing_skill}.")
    print("(Press Enter to proceed, or type 'No, route to <skill_name>' to override): ", end="")
    sys.stdout.flush()
    override_ans = sys.stdin.readline().strip()
    if override_ans.lower().startswith("no"):
        # Extract skill name from override
        # E.g. "no, route to brand_kit" or "no send to brand_kit"
        words = override_ans.lower().split()
        target_override = None
        for w in words:
            if any(s["name"] == w for s in skills):
                target_override = w
                break
        if target_override:
            routing_skill = target_override
            user_overrode = True
            user_turn["skill"] = routing_skill
            print(f"Overridden: routing to {routing_skill} instead.")
        else:
            print("Could not parse target skill from override. Proceeding with original routing.")

    # Save user turn to context history
    context["history"].append(user_turn)
    context["active_skill"] = routing_skill
    save_context(context)
    
    # Log Routing Decision
    log_routing_decision(query, classification.get("matches", [{}])[0].get("skill", "unknown"), confidence, routing_skill, user_overrode)

    # 4. Handoff Execution with Error Handling
    retries = 3
    while retries > 0:
        try:
            result = execute_skill(routing_skill, query, context, skills, parameters)
            
            # Save assistant response
            assistant_turn = {
                "role": "model",
                "text": result,
                "skill": routing_skill,
                "timestamp": datetime.datetime.now().isoformat()
            }
            context["history"].append(assistant_turn)
            save_context(context)
            
            print(f"\n[{routing_skill} Agent response]:\n{result}")
            break
        except Exception as e:
            retries -= 1
            print(f"\n[ERROR] The {routing_skill} agent encountered an error: {e}")
            if retries > 0:
                print("Would you like to retry the task or reroute to a different skill? (retry/reroute/cancel): ", end="")
                sys.stdout.flush()
                ans = sys.stdin.readline().strip().lower()
                if ans == "retry":
                    print("Retrying...")
                    continue
                elif ans == "reroute":
                    print("Select routing skill from available list:")
                    for idx, s in enumerate(skills):
                        print(f"  {idx + 1}. {s['name']}")
                    print("Select a number: ", end="")
                    sys.stdout.flush()
                    s_ans = sys.stdin.readline().strip()
                    try:
                        sel_idx = int(s_ans) - 1
                        if 0 <= sel_idx < len(skills):
                            routing_skill = skills[sel_idx]["name"]
                            user_turn["skill"] = routing_skill
                            save_context(context)
                            retries = 3
                            print(f"Rerouting to {routing_skill}...")
                            continue
                    except ValueError:
                        pass
            print("Request canceled.")
            break

# CLI Loop and Main Entry
def main():
    parser = argparse.ArgumentParser(description="RISEN Orchestrator Agent CLI")
    parser.add_argument("-q", "--query", type=str, help="Run a single query through the orchestrator")
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive orchestrator CLI session")
    parser.add_argument("--skills", action="store_true", help="List all available skills")
    parser.add_argument("--history", action="store_true", help="Show routing history log")
    parser.add_argument("--threshold", type=float, help="Set confidence threshold (0.0 to 1.0)")
    parser.add_argument("--reset", action="store_true", help="Reset session conversation history")
    
    args = parser.parse_args()
    
    context = load_context()
    skills = load_skills()
    
    # Process options
    if args.reset:
        context["active_skill"] = None
        context["history"] = []
        save_context(context)
        print("Session reset.")
        return
        
    if args.threshold is not None:
        val = args.threshold
        if 0.0 <= val <= 1.0:
            context["confidence_threshold"] = val
            save_context(context)
            print(f"Confidence threshold updated to: {val:.2f}")
        else:
            print("[ERROR] Threshold must be between 0.0 and 1.0.")
        return
        
    if args.skills:
        handle_meta_command("/skills", context, skills)
        return
        
    if args.history:
        handle_meta_command("/history", context, skills)
        return

    # Process query
    if args.query:
        # Check for multiple queued queries (split by ';')
        queries = [q.strip() for q in args.query.split(";") if q.strip()]
        for q in queries:
            print(f"\n>>> Processing queued request: {q}")
            orchestrate_query(q, context, skills)
        return

    # Default to interactive if no flags or explicitly requested
    if args.interactive or len(sys.argv) == 1:
        print("====================================================================")
        print(" .pop Agent System - Orchestrator CLI Wrapper (RISEN)")
        print(" Type /skills, /history, /threshold, /reset, or Ctrl+D to exit.")
        print("====================================================================")
        
        # Check API Key
        api_key = get_api_key()
        if not api_key:
            print("\n[WARNING] GEMINI_API_KEY is not set. API calls will fail.")
            print("Please enter your Gemini API Key to run queries: ", end="")
            sys.stdout.flush()
            key_input = sys.stdin.readline().strip()
            if key_input:
                os.environ["GEMINI_API_KEY"] = key_input
                # Create a temporary .env file
                try:
                    with open(os.path.join(BASE_DIR, ".env"), "w") as f:
                        f.write(f"GEMINI_API_KEY={key_input}\n")
                    print(".env file created with key.")
                except Exception as e:
                    print(f"Could not write .env file: {e}")
            else:
                print("Proceeding without key. (Meta-commands will still work).")
                
        while True:
            try:
                active = context.get("active_skill")
                prompt_prefix = f"[{active}] " if active else ""
                print(f"\n{prompt_prefix}pop> ", end="")
                sys.stdout.flush()
                line = sys.stdin.readline()
                if not line: # EOF
                    break
                query = line.strip()
                if not query:
                    continue
                
                # Check for multiple queued queries split by ';'
                queries = [q.strip() for q in query.split(";") if q.strip()]
                for q in queries:
                    orchestrate_query(q, context, skills)
                    # Reload context in case other commands modified it
                    context = load_context()
            except KeyboardInterrupt:
                print("\nUse Ctrl+D to exit.")
            except Exception as e:
                print(f"\n[CRITICAL ERROR] {e}")
                
        print("\nExiting .pop agent.")

if __name__ == "__main__":
    main()
