"""Tests for PythonLiteralParser."""

import ast

import pytest

from visual_geometry_bench.evaluation.answer_parser import PythonLiteralParser


@pytest.fixture
def parser():
    """Fixture providing a parser instance."""
    return PythonLiteralParser()


class TestPythonLiteralParser:
    """Tests for PythonLiteralParser extraction strategies."""

    def test_parse_clean_list(self, parser):
        """Test parsing clean list output."""
        text = "[(0, 1, 0, 1)]"
        result = parser.parse_answer(text)
        assert result == "[(0, 1, 0, 1)]"

    def test_parse_verbose_cot(self, parser):
        """Test extraction from verbose CoT output."""
        text = """
        Let me think through this problem step by step.

        After careful analysis, the answer is:

        [(0, 1, 0, 1)]

        This is the correct configuration.
        """
        result = parser.parse_answer(text)
        assert result == "[(0, 1, 0, 1)]"

    def test_parse_code_fence(self, parser):
        """Test extraction from code fence."""
        text = """
        Here's my solution:

        ```python
        [(0, 1, 0, 1)]
        ```
        """
        result = parser.parse_answer(text)
        assert result == "[(0, 1, 0, 1)]"

    def test_parse_code_fence_no_language(self, parser):
        """Test extraction from code fence without language specifier."""
        text = """
        ```
        [(0, 1, 0, 1)]
        ```
        """
        result = parser.parse_answer(text)
        assert result == "[(0, 1, 0, 1)]"

    def test_parse_multiple_lists_takes_last(self, parser):
        """Test that parser takes the last valid list when multiple present."""
        text = """
        Wrong answer: [1, 2, 3]

        Actually, the correct answer is:
        [(0, 1, 0, 1)]
        """
        result = parser.parse_answer(text)
        assert result == "[(0, 1, 0, 1)]"

    def test_parse_nested_structure(self, parser):
        """Test parsing nested list structures."""
        text = "[[1, 2], [3, 4]]"
        result = parser.parse_answer(text)
        assert result == "[[1, 2], [3, 4]]"

    def test_parse_dict(self, parser):
        """Test parsing dictionary structures."""
        text = '{"key": "value", "nested": [1, 2, 3]}'
        result = parser.parse_answer(text)
        assert result == '{"key": "value", "nested": [1, 2, 3]}'

    def test_parse_invalid_returns_none(self, parser):
        """Test that invalid/unparseable text returns None."""
        text = "I don't know the answer"
        result = parser.parse_answer(text)
        assert result is None

    def test_parse_empty_string(self, parser):
        """Test parsing empty string."""
        text = ""
        result = parser.parse_answer(text)
        assert result is None

    def test_parse_unbalanced_brackets(self, parser):
        """Test that unbalanced brackets return None."""
        text = "[(0, 1, 0, 1]"  # Missing closing bracket
        result = parser.parse_answer(text)
        assert result is None

    def test_parse_message_list(self, parser):
        """Test parsing from message list format."""
        messages = [
            {"role": "user", "content": "What is the answer?"},
            {"role": "assistant", "content": "The answer is [(0, 1, 0, 1)]"}
        ]
        result = parser.parse_answer(messages)
        assert result == "[(0, 1, 0, 1)]"

    def test_parse_empty_message_list(self, parser):
        """Test parsing from empty message list."""
        messages = []
        result = parser.parse_answer(messages)
        assert result is None

    def test_parse_multiline_list(self, parser):
        """Test parsing list with line breaks."""
        text = """
        [
            (0, 1, 0, 1),
            (0, 0, 1, 1)
        ]
        """
        result = parser.parse_answer(text)
        assert result is not None
        # Verify it's valid by parsing
        import ast
        parsed = ast.literal_eval(result)
        assert len(parsed) == 2

    def test_parse_with_trailing_text(self, parser):
        """Test extraction when answer has trailing explanation."""
        text = """
        [(0, 1, 0, 1)]

        This configuration guarantees an interior boundary because...
        """
        result = parser.parse_answer(text)
        assert result == "[(0, 1, 0, 1)]"

    def test_strip_thinking_blocks_before_parsing(self, parser):
        """Content inside <thinking> tags is ignored."""
        text = """
        <thinking>
        [123, 456]  # scratch work
        </thinking>
        assistant: 1100110, 11100, 1110101, 1110111
        """
        result = parser.parse_answer(text)
        assert result is not None
        parsed = ast.literal_eval(result)
        assert list(map(str, parsed)) == ["1100110", "11100", "1110101", "1110111"]

    def test_simple_sequence_preferred_over_backscan(self, parser):
        """Trailing comma list wins even if earlier text has brackets."""
        text = """
        Reasoning with bbox x:[0.1,0.2], y:[0.3,0.4]

        Final neighbours:
        010, 011, 100
        """
        result = parser.parse_answer(text)
        assert result is not None
        parsed = ast.literal_eval(result)
        assert list(map(str, parsed)) == ["010", "011", "100"]

    
    def test_code_fence_priority_over_backscan(self, parser):
        """Test that code fence is tried before backscan."""
        text = """
        Wrong: [1, 2, 3]

        ```python
        [(0, 1, 0, 1)]
        ```

        Also wrong: [4, 5, 6]
        """
        result = parser.parse_answer(text)
        # Should get the code fence content, not the last bracket
        assert result == "[(0, 1, 0, 1)]"

    def test_parse_simple_sequence_with_role_prefix(self, parser):
        """Comma list prefixed by a role label is parsed correctly."""
        text = "assistant: 00110, 00101, 001111, 10010"
        result = parser.parse_answer(text)
        assert result is not None
        parsed = ast.literal_eval(result)
        assert list(map(str, parsed)) == ["00110", "00101", "001111", "10010"]

    def test_parse_simple_sequence_with_arrow_prefix(self, parser):
        """Arrow-separated answers are also accepted."""
        text = "model answer => 00110, 00101, 001111, 10010"
        result = parser.parse_answer(text)
        assert result is not None
        parsed = ast.literal_eval(result)
        assert list(map(str, parsed)) == ["00110", "00101", "001111", "10010"]

    def test_parse_simple_sequence_with_embedded_arrow(self, parser):
        """Handles prose with trailing arrow segment."""
        text = "assistant: Here is the list -> 00110, 00101, 001111, 10010"
        result = parser.parse_answer(text)
        assert result is not None
        parsed = ast.literal_eval(result)
        assert list(map(str, parsed)) == ["00110", "00101", "001111", "10010"]

    def test_parse_simple_sequence_numeric_tokens(self, parser):
        """Plain numeric tokens remain numeric values."""
        text = "0, 1, -2, 3"
        result = parser.parse_answer(text)
        assert result is not None
        parsed = ast.literal_eval(result)
        assert tuple(parsed) == (0, 1, -2, 3)

    def test_parse_simple_sequence_leading_zero_tokens(self, parser):
        """Tokens with leading zeros are preserved as strings."""
        text = "0000, 0001, 0010"
        result = parser.parse_answer(text)
        assert result is not None
        parsed = ast.literal_eval(result)
        assert list(map(str, parsed)) == ["0000", "0001", "0010"]
