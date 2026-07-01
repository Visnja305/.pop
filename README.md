# .pop Agent System

Welcome to the `.pop` agent system workspace. This folder acts as the core operating repository for the `.pop` AI agent, organizing its behavior, capabilities, and active state.

## Folder Structure

- **`config/`**: System configuration files. Contains `skills.json` which maps specific skill files to their triggers and descriptions.
- **`memory/`**: Agent persistent session history and context tracking. Contains `context.json`.
- **`skills/`**: The system prompt markdown files defining the agent's executable capabilities.

## How to Add a New Skill

1. **Write the system prompt**: Define the persona, rules, and triggers for the new skill.
2. **Save as a `.md` file**: Store it in the `skills/` directory (e.g., `skills/my_new_skill.md`).
3. **Register the skill**: Add a new entry to `config/skills.json` describing the skill and its trigger phrases.

## Running a Skill in Antigravity

To execute any skill:
1. Open the desired skill file in the `skills/` directory.
2. Copy the full markdown content of that skill.
3. Paste the contents into the agent's system prompt field within Antigravity.
