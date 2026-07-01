#!/usr/bin/env python3
"""
Unit tests for the RISEN Orchestrator Agent
Tests key logic paths by mocking API calls and file operations.
"""

import os
import sys
import unittest
import json
import shutil
import tempfile
from unittest.mock import patch, MagicMock

# Import the orchestrator script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scripts.orchestrate as orchestrate

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        # Create a temp directory for files
        self.test_dir = tempfile.mkdtemp()
        
        # Override paths in orchestrate
        self.old_config_path = orchestrate.CONFIG_PATH
        self.old_context_path = orchestrate.CONTEXT_PATH
        self.old_log_path = orchestrate.LOG_PATH
        
        orchestrate.CONFIG_PATH = os.path.join(self.test_dir, "skills.json")
        orchestrate.CONTEXT_PATH = os.path.join(self.test_dir, "context.json")
        orchestrate.LOG_PATH = os.path.join(self.test_dir, "routing_log.jsonl")
        
        # Set up a sample skills file
        self.skills_data = {
            "skills": [
                {
                    "name": "brand_kit",
                    "description": "Applies brand guidelines",
                    "trigger_phrases": ["apply brand kit", "check styles"],
                    "file": "skills/brand_kit.md"
                },
                {
                    "name": "carousel",
                    "description": "Builds carousels",
                    "trigger_phrases": ["carousel component", "slides"],
                    "file": "skills/carousel.md"
                }
            ]
        }
        with open(orchestrate.CONFIG_PATH, "w") as f:
            json.dump(self.skills_data, f)
            
        # Create dummy skill files
        os.makedirs(os.path.join(self.test_dir, "skills"), exist_ok=True)
        with open(os.path.join(self.test_dir, "skills/brand_kit.md"), "w") as f:
            f.write("# Brand Kit Prompt")
        with open(os.path.join(self.test_dir, "skills/carousel.md"), "w") as f:
            f.write("# Carousel Prompt")
            
        # Set up default context
        self.context = {
            "active_skill": None,
            "confidence_threshold": 0.80,
            "history": [],
            "session_count": 1,
            "last_updated": ""
        }
        orchestrate.save_context(self.context)

    def tearDown(self):
        # Restore paths
        orchestrate.CONFIG_PATH = self.old_config_path
        orchestrate.CONTEXT_PATH = self.old_context_path
        orchestrate.LOG_PATH = self.old_log_path
        shutil.rmtree(self.test_dir)

    def test_load_skills(self):
        skills = orchestrate.load_skills()
        self.assertEqual(len(skills), 2)
        self.assertEqual(skills[0]["name"], "brand_kit")

    def test_meta_command_reset(self):
        # Setup context with history
        context = orchestrate.load_context()
        context["active_skill"] = "brand_kit"
        context["history"] = [{"role": "user", "text": "hello"}]
        orchestrate.save_context(context)
        
        # Trigger reset
        res = orchestrate.handle_meta_command("/reset", context, self.skills_data["skills"])
        self.assertTrue(res)
        
        new_context = orchestrate.load_context()
        self.assertIsNone(new_context["active_skill"])
        self.assertEqual(len(new_context["history"]), 0)

    def test_meta_command_threshold(self):
        context = orchestrate.load_context()
        
        # Check invalid
        orchestrate.handle_meta_command("/threshold invalid", context, [])
        self.assertEqual(orchestrate.load_context()["confidence_threshold"], 0.80)
        
        # Check valid
        orchestrate.handle_meta_command("/threshold 0.75", context, [])
        self.assertEqual(orchestrate.load_context()["confidence_threshold"], 0.75)

    @patch("scripts.orchestrate.call_gemini")
    def test_classify_intent(self, mock_call):
        mock_call.return_value = json.dumps({
            "explicit_skill_named": None,
            "matches": [{"skill": "brand_kit", "confidence": 0.95}],
            "parameters": {}
        })
        
        skills = orchestrate.load_skills()
        context = orchestrate.load_context()
        result = orchestrate.classify_intent("help check styles", context, skills)
        
        self.assertEqual(result["matches"][0]["skill"], "brand_kit")
        self.assertEqual(result["matches"][0]["confidence"], 0.95)

    @patch("sys.stdin")
    @patch("scripts.orchestrate.call_gemini")
    def test_orchestrate_mismatch_override_yes(self, mock_call, mock_stdin):
        # Mock Gemini to return a mismatch: user explicitly asked for carousel but intent is brand_kit
        mock_call.side_effect = [
            # Classification call
            json.dumps({
                "explicit_skill_named": "carousel",
                "matches": [{"skill": "brand_kit", "confidence": 0.90}],
                "parameters": {}
            }),
            # Execution call
            "Executed brand_kit successfully"
        ]
        
        # Simulate user choosing YES to route to explicit choice
        mock_stdin.readline.side_effect = [
            "yes\n",  # Override choice mismatch
            "\n"      # Handoff confirmation
        ]
        
        skills = orchestrate.load_skills()
        # Mock BASE_DIR to search in test_dir
        with patch("scripts.orchestrate.BASE_DIR", self.test_dir):
            context = orchestrate.load_context()
            orchestrate.orchestrate_query("use carousel to apply brand kit", context, skills)
            
            # Check log
            self.assertTrue(os.path.exists(orchestrate.LOG_PATH))
            with open(orchestrate.LOG_PATH, "r") as f:
                logs = [json.loads(line) for line in f]
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]["chosen_skill"], "carousel") # Because user chose yes to override
            self.assertTrue(logs[0]["user_overrode"])

    @patch("sys.stdin")
    @patch("scripts.orchestrate.call_gemini")
    def test_orchestrate_mismatch_override_no(self, mock_call, mock_stdin):
        mock_call.side_effect = [
            # Classification call
            json.dumps({
                "explicit_skill_named": "carousel",
                "matches": [{"skill": "brand_kit", "confidence": 0.90}],
                "parameters": {}
            }),
            # Execution call
            "Executed brand_kit successfully"
        ]
        
        # Simulate user choosing NO to route to recommendation
        mock_stdin.readline.side_effect = [
            "no\n",  # Override choice mismatch
            "\n"     # Handoff confirmation
        ]
        
        skills = orchestrate.load_skills()
        with patch("scripts.orchestrate.BASE_DIR", self.test_dir):
            context = orchestrate.load_context()
            orchestrate.orchestrate_query("use carousel to apply brand kit", context, skills)
            
            with open(orchestrate.LOG_PATH, "r") as f:
                logs = [json.loads(line) for line in f]
            self.assertEqual(logs[0]["chosen_skill"], "brand_kit")
            self.assertFalse(logs[0]["user_overrode"])

    @patch("sys.stdin")
    @patch("scripts.orchestrate.call_gemini")
    def test_orchestrate_chaining(self, mock_call, mock_stdin):
        # Mock classification to return a chain of brand_kit -> carousel
        mock_call.side_effect = [
            # Classification call
            json.dumps({
                "explicit_skill_named": None,
                "matches": [],
                "chain": ["brand_kit", "carousel"],
                "parameters": {}
            }),
            # Execution call 1 (brand_kit)
            "Brand kit applied",
            # Execution call 2 (carousel)
            "Carousel built with brand kit"
        ]
        
        skills = orchestrate.load_skills()
        with patch("scripts.orchestrate.BASE_DIR", self.test_dir):
            context = orchestrate.load_context()
            orchestrate.orchestrate_query("do brand kit then make carousel", context, skills)
            
            # Context active skill should end up as carousel (last in chain)
            new_context = orchestrate.load_context()
            self.assertEqual(new_context["active_skill"], "carousel")
            self.assertEqual(len(new_context["history"]), 4) # 1 user request + 1 brand_kit execution + 1 brand_kit model resp + 1 carousel model resp

    @patch("sys.stdin")
    @patch("scripts.orchestrate.call_gemini")
    def test_unclear_intent_multiple_plausible(self, mock_call, mock_stdin):
        # Mock classification to return 2 plausible skills under threshold (0.80)
        mock_call.side_effect = [
            # Classification call
            json.dumps({
                "explicit_skill_named": None,
                "matches": [
                    {"skill": "brand_kit", "confidence": 0.40},
                    {"skill": "carousel", "confidence": 0.35}
                ],
                "parameters": {}
            }),
            # Execution call
            "Executed carousel successfully"
        ]
        
        # User selects option 2 (carousel)
        mock_stdin.readline.side_effect = [
            "2\n",  # Select carousel
            "\n"    # Confirm handoff
        ]
        
        skills = orchestrate.load_skills()
        with patch("scripts.orchestrate.BASE_DIR", self.test_dir):
            context = orchestrate.load_context()
            orchestrate.orchestrate_query("help me make something styling related", context, skills)
            
            new_context = orchestrate.load_context()
            self.assertEqual(new_context["active_skill"], "carousel")

if __name__ == "__main__":
    unittest.main()
