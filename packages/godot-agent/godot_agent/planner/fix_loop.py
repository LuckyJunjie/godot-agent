"""FixLoop — LLM-driven error correction with validation feedback."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FixIteration:
    iteration: int
    errors: list[str]
    fix_applied: str
    validation_result: str


class FixLoop:
    """Iteratively fixes code based on validation errors."""

    MAX_ITERATIONS = 5

    FIX_PROMPT = """You are a Godot game developer fixing errors in generated code.

File: {file_path}
Current code:
```gdscript
{code}
```

Validation errors:
{errors}

Please provide the COMPLETE fixed version of the file.
Return ONLY the corrected code inside a ```gdscript block.
Do not explain the changes.
"""

    def __init__(self, llm_client, tool_registry):
        self.llm = llm_client
        self.registry = tool_registry

    async def fix(
        self,
        file_path: str,
        validation_errors: list[str],
        max_iterations: int = MAX_ITERATIONS,
    ) -> tuple[bool, list[FixIteration]]:
        """Attempt to fix a file based on validation errors.

        Returns (success, iterations_log).
        """
        path = Path(file_path)
        if not path.exists():
            return False, [FixIteration(0, validation_errors, "", f"File not found: {file_path}")]

        code = path.read_text(encoding="utf-8")
        iterations: list[FixIteration] = []

        for i in range(max_iterations):
            # Ask LLM to fix
            prompt = self.FIX_PROMPT.format(
                file_path=file_path,
                code=code,
                errors="\n".join(f"- {e}" for e in validation_errors),
            )
            response = await self.llm.chat([{"role": "user", "content": prompt}])
            fixed_code = self._extract_code(response)

            if not fixed_code:
                iterations.append(
                    FixIteration(
                        iteration=i,
                        errors=validation_errors,
                        fix_applied="[LLM did not return code]",
                        validation_result="FAILED",
                    )
                )
                continue

            # Apply fix
            path.write_text(fixed_code, encoding="utf-8")

            # Re-validate
            new_errors = await self._validate(file_path)

            iterations.append(
                FixIteration(
                    iteration=i,
                    errors=validation_errors,
                    fix_applied=fixed_code[:200] + "..." if len(fixed_code) > 200 else fixed_code,
                    validation_result="PASSED" if not new_errors else "FAILED",
                )
            )

            if not new_errors:
                return True, iterations

            validation_errors = new_errors
            code = fixed_code

        return False, iterations

    async def _validate(self, file_path: str) -> list[str]:
        """Run validation tools on a file and return errors."""
        errors = []

        # Try LSP lint
        lint_tool = self.registry.get("gd_script_lint")
        if lint_tool:
            try:
                result = await lint_tool.execute(path=file_path)
                if "❌" in result or "error" in result.lower():
                    errors.append(result)
            except Exception:
                pass

        # Try harness for .gd files
        if file_path.endswith(".gd"):
            harness_tool = self.registry.get("gd_harness_run")
            if harness_tool:
                try:
                    result = await harness_tool.execute(test_script=file_path)
                    if "FAILED" in result:
                        errors.append(result)
                except Exception:
                    pass

        return errors

    @staticmethod
    def _extract_code(response: str) -> Optional[str]:
        """Extract code from markdown code block."""
        text = response.strip()
        if "```gdscript" in text:
            start = text.find("```gdscript") + len("```gdscript")
            end = text.find("```", start)
            return text[start:end].strip()
        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()
