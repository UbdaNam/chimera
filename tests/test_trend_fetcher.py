import inspect
import pytest


def test_skill_fetch_trends_exists_and_signature():
    """Failing test: verifies `skill_fetch_trends` function exists and accepts expected parameters."""
    try:
        from chimera import skills
    except Exception as e:
        pytest.fail(f"Failed to import `chimera.skills` module: {e}")

    func = getattr(skills, "skill_fetch_trends", None)
    assert callable(func), "`skill_fetch_trends` is not implemented or not callable"

    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    # Required input contract fields (envelope + specific)
    assert "traceId" in params or "**kwargs" in params, "`traceId` not present in function signature"
    assert "specRef" in params or "**kwargs" in params, "`specRef` not present in function signature"
    assert "source" in params or "**kwargs" in params, "`source` parameter missing"
    assert ("since" in params) or ("limit" in params) or "**kwargs" in params, "`since`/`limit` not present"


def test_trend_response_structure_sample():
    """Fails if the sample structure does not match the spec-defined keys/types."""
    # A minimal example response matching the spec
    sample = {
        "topics": [
            {
                "topicId": "t-123",
                "topic": "example",
                "confidence": 0.92,
                "provenance": ["http://source.example/item/1"],
                "sampleSignals": [{"signalType": "mentions", "value": 123}]
            }
        ],
        "warnings": []
    }

    assert isinstance(sample, dict)
    assert "topics" in sample and isinstance(sample["topics"], list)
    topic = sample["topics"][0]
    assert "topicId" in topic and isinstance(topic["topicId"], str)
    assert "topic" in topic and isinstance(topic["topic"], str)
    assert "confidence" in topic and isinstance(topic["confidence"], float)
    assert "provenance" in topic and isinstance(topic["provenance"], list)
    assert "sampleSignals" in topic and isinstance(topic["sampleSignals"], list)
