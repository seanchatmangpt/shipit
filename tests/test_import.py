"""Test shipit."""

import shipit


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(shipit.__name__, str)
