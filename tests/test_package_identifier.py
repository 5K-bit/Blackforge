import pytest
from blackforge.core.generator import generate_project, GenerationError

@pytest.mark.parametrize("name", ["123project", "class", "def", "---"])
def test_invalid_package_names_are_rejected_before_writes(tmp_path, name):
    with pytest.raises(GenerationError):
        generate_project("python-package", name, tmp_path)
    assert list(tmp_path.iterdir()) == []
