import pytest
import helpers

# This is another attempt to write tests without knowing how to do that. Forgive me World...

def test_parse_yaml_returns_dict():
    assert type(helpers.parse_yaml('inventory.yaml')) == type({})

