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

        text = self._normalise_text(text)
        text = self._strip_thinking_blocks(text)

        if not text:
            return None

        # Strategy 1: Try code fence extraction
        code_fence = self._extract_from_code_fence(text)
        if code_fence and self._is_valid_literal(code_fence):
            return code_fence.strip()

        stripped = text.strip()

        # Strategy 2: Try parsing whole text if it looks clean
        if self._is_valid_literal(stripped):
            return stripped

        # Strategy 3: Trailing comma-delimited sequences (no brackets)
        simple_list = self._parse_simple_sequence(stripped)
        if simple_list is not None:
            return simple_list

        # Strategy 4: Backscan for last balanced bracket structure
        backscanned = self._backscan_literal(text)
        if backscanned and self._is_valid_literal(backscanned):
            return backscanned.strip()

        return None

    def _extract_from_code_fence(self, text: str) -> Optional[str]:
        """Extract content from ```python ... ``` or ``` ... ``` code fence.

        Returns the last code fence found, or None.
        """
        # Match ```python or just ```
        pattern = r"```(?:[^\n`]*\n)?(.*?)```"
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

    def _parse_simple_sequence(self, text: str) -> Optional[str]:
        """Convert comma/newline separated scalars into a Python list literal."""

        if not text:
            return None

        for candidate in self._simple_sequence_candidates(text):
            literal = self._coerce_simple_sequence(candidate)
            if literal is not None:
                return literal
        return None

    def _simple_sequence_candidates(self, text: str) -> list[str]:
        """Generate candidate substrings likely containing the scalar list."""

        candidates: list[str] = []
        seen: set[str] = set()

        def _add(candidate: str) -> None:
            candidate = candidate.strip()
            if candidate and candidate not in seen:
                seen.add(candidate)
                candidates.append(candidate)

        _add(text)

        # Last non-empty line often carries the answer.
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            _add(lines[-1])

        # Trailing segments after separators (colon/arrow) capture role prefixes, e.g. "assistant: ...".
        for separator in ("->", "=>", ":", "="):
            if separator in text:
                _add(text.rsplit(separator, 1)[-1])

        return candidates

    def _coerce_simple_sequence(self, text: str) -> Optional[str]:
        """Attempt to turn a plain scalar sequence into a list literal."""

        if any(bracket in text for bracket in "[]{}()"):
            return None

        candidate = text.replace("\n", ",")
        tokens = [tok.strip() for tok in candidate.split(",") if tok.strip()]
        if not tokens:
            return None

        allowed = re.compile(r"^[A-Za-z0-9_.\-\"']+$")
        if not all(allowed.fullmatch(tok) for tok in tokens):
            return None

        try:
            normalised = [self._normalise_csv_token(tok) for tok in tokens]
        except ValueError:
            return None

        literal = "[" + ", ".join(normalised) + "]"
        return literal if self._is_valid_literal(literal) else None

    def _normalise_csv_token(self, token: str) -> str:
        """Coerce a simple token into a literal element."""

        if token in {'""', "''"}:
            return '""'

        if (token.startswith('"') and token.endswith('"') and len(token) >= 2) or (
            token.startswith("'") and token.endswith("'") and len(token) >= 2
        ):
            return token

        try:
            value = ast.literal_eval(token)
        except Exception:  # noqa: BLE001 - broad except is fine for literal eval
            value = None

        if isinstance(value, (int, float)):
            # Preserve leading zeros (including "0001") by treating as string literal.
            stripped = token.lstrip("-+")
            if stripped.startswith("0") and len(stripped) > 1:
                return repr(token)
            return token

        return repr(token)

    def _normalise_text(self, text: str) -> str:
        """Replace common typographic quotes with ASCII equivalents."""

        if not text:
            return text

        translation_table = str.maketrans({
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
        })
        return text.translate(translation_table)

    def _strip_thinking_blocks(self, text: str) -> str:
        """Remove <thinking>...</thinking> blocks to ignore CoT scratch space."""

        if not text:
            return text
        pattern = re.compile(r"<thinking>.*?</thinking>", re.IGNORECASE | re.DOTALL)
        return re.sub(pattern, "", text)
