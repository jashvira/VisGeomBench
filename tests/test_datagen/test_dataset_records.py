"""Tests for dataset record generation and metadata inheritance."""

import json

import pytest

from visual_geometry_bench.datagen.topology_enumeration import (
    build_problem_id,
    generate_dataset_record,
)
from visual_geometry_bench.dataset import build_records_from_config


class TestDatasetRecordGeneration:
    """Test dataset record generation with validation."""

    def test_generate_dataset_record_structure(self):
        """Dataset record has correct structure and keys."""
        datagen_args = {
            "n_classes": 2,
            "corner_order": ["bottom-left", "bottom-right", "top-right", "top-left"],
        }

        record = generate_dataset_record(
            datagen_args=datagen_args,
            tags=["topology", "visual_reasoning"],
            difficulty="medium",
        )

        # Check required top-level keys
        assert "id" in record
        assert "prompt" in record
        assert "ground_truth" in record
        assert "metadata" in record
        assert "datagen_args" in record

        # Check metadata structure
        assert record["metadata"]["problem_type"] == "topology_enumeration"
        assert record["metadata"]["tags"] == ["topology", "visual_reasoning"]
        assert record["metadata"]["difficulty"] == "medium"
        assert "requires_visual" not in record["metadata"]

        # Check datagen_args preserved
        assert record["datagen_args"] == datagen_args

    def test_generate_dataset_record_json_serializable(self):
        """Dataset record is JSON-serializable."""
        datagen_args = {
            "n_classes": 3,
            "corner_order": ["top-right", "top-left", "bottom-left", "bottom-right"],
        }

        record = generate_dataset_record(
            datagen_args=datagen_args,
            tags=["topology"],
        )

        # Should serialize without errors
        json_str = json.dumps(record, ensure_ascii=False)
        assert isinstance(json_str, str)

        # Should round-trip
        parsed = json.loads(json_str)
        assert parsed["id"] == record["id"]
        assert parsed["ground_truth"] == record["ground_truth"]

    def test_content_addressed_id_deterministic(self):
        """Content-addressed IDs are deterministic for same inputs."""
        datagen_args = {
            "n_classes": 2,
            "corner_order": ["bottom-left", "bottom-right", "top-right", "top-left"],
        }

        record1 = generate_dataset_record(datagen_args=datagen_args, tags=["test"])
        record2 = generate_dataset_record(datagen_args=datagen_args, tags=["test"])

        assert record1["id"] == record2["id"]
        assert len(record1["id"]) == 8  # Short hash

    def test_different_args_different_ids(self):
        """Different datagen_args produce different IDs."""
        args1 = {"n_classes": 2, "corner_order": ["bottom-left", "bottom-right", "top-right", "top-left"]}
        args2 = {"n_classes": 3, "corner_order": ["bottom-left", "bottom-right", "top-right", "top-left"]}

        record1 = generate_dataset_record(datagen_args=args1)
        record2 = generate_dataset_record(datagen_args=args2)

        assert record1["id"] != record2["id"]

    def test_missing_datagen_args_raises(self):
        """Missing required datagen_args raises AssertionError."""
        with pytest.raises(AssertionError, match="missing 'n_classes'"):
            generate_dataset_record(datagen_args={"corner_order": ["a", "b", "c", "d"]})

        with pytest.raises(AssertionError, match="missing 'corner_order'"):
            generate_dataset_record(datagen_args={"n_classes": 2})

    def test_invalid_datagen_args_types_raises(self):
        """Invalid datagen_args types raise AssertionError."""
        with pytest.raises(AssertionError, match="must be int"):
            generate_dataset_record(datagen_args={"n_classes": "2", "corner_order": ["a", "b", "c", "d"]})

        with pytest.raises(AssertionError, match="must be list or tuple"):
            generate_dataset_record(datagen_args={"n_classes": 2, "corner_order": "invalid"})


class TestMetadataInheritance:
    """Test metadata inheritance with tag union."""

    def test_tag_union_inheritance(self):
        """Tags from task and question are merged (union)."""
        config = {
            "task": [{
                "type": "topology_enumeration",
                "metadata": {
                    "tags": ["topology", "visual_reasoning"],
                    "difficulty": "medium",
                },
                "datagen_args_grid": [
                    {
                        "n_classes": 2,
                        "corner_order": ["bottom-left", "bottom-right", "top-right", "top-left"],
                        "metadata": {"tags": ["enumeration"]},
                    }
                ],
            }]
        }

        records = build_records_from_config(config)
        assert len(records) == 1

        # Tags should be union of task + question tags
        tags = set(records[0]["metadata"]["tags"])
        assert tags == {"topology", "visual_reasoning", "enumeration"}

    def test_shallow_override_inheritance(self):
        """Non-tag metadata fields use shallow override."""
        config = {
            "task": [{
                "type": "topology_enumeration",
                "metadata": {
                    "tags": ["topology"],
                    "difficulty": "medium",
                },
                "datagen_args_grid": [
                    {
                        "n_classes": 3,
                        "corner_order": ["bottom-left", "bottom-right", "top-right", "top-left"],
                        "metadata": {"difficulty": "hard"},  # Override
                    }
                ],
            }]
        }

        records = build_records_from_config(config)
        assert records[0]["metadata"]["difficulty"] == "hard"  # Overridden
        assert "requires_visual" not in records[0]["metadata"]

    def test_no_question_metadata_uses_task_defaults(self):
        """Questions without metadata use task-level defaults."""
        config = {
            "task": [{
                "type": "topology_enumeration",
                "metadata": {
                    "tags": ["topology"],
                    "difficulty": "medium",
                },
                "datagen_args_grid": [
                    {
                        "n_classes": 2,
                        "corner_order": ["bottom-left", "bottom-right", "top-right", "top-left"],
                        # No metadata override
                    }
                ],
            }]
        }

        records = build_records_from_config(config)
        assert records[0]["metadata"]["tags"] == ["topology"]
        assert records[0]["metadata"]["difficulty"] == "medium"

