"""Tests for planner/fix_loop.py."""

import pytest
from pathlib import Path

from godot_agent.planner.fix_loop import FixLoop, FixIteration


class MockLLM:
    """Mock LLM that returns fixed code."""

    def __init__(self, response: str = None):
        self.response = response

    async def chat(self, messages):
        return self.response


class MockRegistry:
    """Mock tool registry."""

    def __init__(self, lint_result="", harness_result=""):
        self._lint = lint_result
        self._harness = harness_result

    def get(self, name):
        if name == "gd_script_lint":
            return MockLintTool(self._lint)
        if name == "gd_harness_run":
            return MockHarnessTool(self._harness)
        return None


class MockLintTool:
    def __init__(self, result):
        self._result = result

    async def execute(self, **kwargs):
        return self._result


class MockHarnessTool:
    def __init__(self, result):
        self._result = result

    async def execute(self, **kwargs):
        return self._result


class TestFixLoop:
    async def test_fix_file_not_found(self):
        loop = FixLoop(MockLLM(), MockRegistry())
        success, iterations = await loop.fix("/nonexistent/file.gd", ["error"])
        assert success is False
        assert iterations[0].validation_result == "File not found: /nonexistent/file.gd"

    async def test_fix_no_llm_code(self, temp_project):
        loop = FixLoop(MockLLM("   "), MockRegistry(lint_result="❌ error"))
        script = temp_project / "test.gd"
        script.write_text("extends Node2D\n", encoding="utf-8")

        success, iterations = await loop.fix(str(script), ["syntax error"])
        assert success is False
        assert iterations[0].fix_applied == "[LLM did not return code]"

    async def test_fix_success_on_first_try(self, temp_project):
        fixed_code = "extends Node2D\n\nfunc _ready():\n    pass\n"
        llm = MockLLM(f"```gdscript\n{fixed_code}\n```")
        # Use a lint result that doesn't accidentally contain "error" in lowercase
        registry = MockRegistry(lint_result="✅ Clean")
        loop = FixLoop(llm, registry)

        script = temp_project / "test.gd"
        script.write_text("extends Node2D\n", encoding="utf-8")

        success, iterations = await loop.fix(str(script), ["missing func"])
        assert success is True
        assert len(iterations) == 1
        assert iterations[0].validation_result == "PASSED"
        assert script.read_text().strip() == fixed_code.strip()

    async def test_fix_still_fails_after_max_iterations(self, temp_project):
        original = "extends Node2D\n"
        script = temp_project / "test.gd"
        script.write_text(original, encoding="utf-8")

        class AlwaysFailingLLM:
            async def chat(self, messages):
                return "```gdscript\nextends Node2D\n```"

        registry = MockRegistry(lint_result="❌ test.gd:\nLine 1: still broken")
        loop = FixLoop(AlwaysFailingLLM(), registry)

        success, iterations = await loop.fix(str(script), ["error"], max_iterations=2)
        assert success is False
        assert len(iterations) == 2  # max iterations reached

    async def test_extract_code_plain_markdown(self):
        code = FixLoop._extract_code("```\nsome code\n```")
        assert code == "some code"

    async def test_extract_code_gdscript(self):
        code = FixLoop._extract_code("```gdscript\nsome code\n```")
        assert code == "some code"

    async def test_extract_code_no_markdown(self):
        code = FixLoop._extract_code("just text")
        assert code == "just text"
