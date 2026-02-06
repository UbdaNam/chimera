import inspect
import pytest


def _import_skills_module():
    try:
        from chimera import skills
        return skills
    except Exception as e:
        pytest.fail(f"Failed to import `chimera.skills` module: {e}")


def test_skill_generate_content_signature():
    skills = _import_skills_module()
    func = getattr(skills, "skill_generate_content", None)
    assert callable(func), "`skill_generate_content` is not implemented or not callable"

    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    assert "topicId" in params or "**kwargs" in params, "`topicId` param missing"
    assert "objective" in params or "**kwargs" in params, "`objective` param missing"
    assert "constraints" in params or "**kwargs" in params, "`constraints` param missing"


def test_skill_publish_content_signature():
    skills = _import_skills_module()
    func = getattr(skills, "skill_publish_content", None)
    assert callable(func), "`skill_publish_content` is not implemented or not callable"

    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    assert "assetPackageId" in params or "**kwargs" in params, "`assetPackageId` param missing"
    assert "channels" in params or "**kwargs" in params, "`channels` param missing"
    assert "credentialsRef" in params or "**kwargs" in params, "`credentialsRef` param missing"
