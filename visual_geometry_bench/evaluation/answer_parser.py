"""Generic parser for extracting Python literals from CoT-heavy model outputs.

Follows the vf.Parser protocol and uses backscan strategy inspired by ARC-AGI.
"""

from __future__ import annotations

import ast
import re
from typing import Optional

import verifiers as vf
from verifiers.types import Messages


class PythonLiteralParser(vf.Parser):
    """Parser that extracts Python literals from verbose model outputs.

    Strategy:
        1. Try extracting from ```python ... ``` code fence
        2. Backscan for last balanced [...] or {...}
        3. Fallback to parsing whole text if it looks clean

    Returns the extracted literal as a string, or None if extraction fails.
    Task-specific validation is left to the verifier functions.
    """

    def parse_answer(self, completion: Messages) -> Optional[str]:
        """Extract Python literal from completion.

        Args:
            completion: Model completion (string or list of messages)

        Returns:
            Extracted literal string, or None if no valid literal found
        """
        if isinstance(completion, str):
            text = completion
        else:
            text = completion[-1]["content"] if completion else ""

        if not text:
            return None

        # Strategy 1: Try code fence extraction
        code_fence = self._extract_from_code_fence(text)
        if code_fence and self._is_valid_literal(code_fence):
            return code_fence.strip()

        # Strategy 2: Backscan for last balanced bracket structure
        backscanned = self._backscan_literal(text)
        if backscanned and self._is_valid_literal(backscanned):
            return backscanned.strip()

        # Strategy 3: Try parsing whole text if it looks clean
        stripped = text.strip()
        if self._is_valid_literal(stripped):
            return stripped

        return None

    def _extract_from_code_fence(self, text: str) -> Optional[str]:
        """Extract content from ```python ... ``` or ``` ... ``` code fence.

        Returns the last code fence found, or None.
        """
        # Match ```python or just ```
        pattern = r'```(?:python)?\s*(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[-1].strip()  # Return last fence
        return None

    def _backscan_literal(self, text: str) -> Optional[str]:
        """Scan backwards to find last balanced [...] or {...}.

        Adapted from ARC-AGI backscan_json approach.
        """
        # Find last closing bracket
        last_bracket = -1
        closing_bracket = None
        for i in range(len(text) - 1, -1, -1):
            if text[i] in (']', '}'):
                last_bracket = i
                closing_bracket = text[i]
                break

        if last_bracket == -1:
            return None

        opening_bracket = '[' if closing_bracket == ']' else '{'

        # Scan backwards to find matching opening bracket
        bracket_count = 1
        start_idx = -1
        for i in range(last_bracket - 1, -1, -1):
            if text[i] == closing_bracket:
                bracket_count += 1
            elif text[i] == opening_bracket:
                bracket_count -= 1
                if bracket_count == 0:
                    start_idx = i
                    break

        if start_idx == -1:
            return None

        return text[start_idx:last_bracket + 1]

    def _is_valid_literal(self, text: str) -> bool:
        """Check if text is a valid Python literal using ast.literal_eval.

        Args:
            text: String to validate

        Returns:
            True if text can be parsed as a Python literal
        """
        try:
            ast.literal_eval(text)
            return True
        except (ValueError, SyntaxError):
            return False

