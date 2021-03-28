import pytest
import mock
import helpers

# This is another attempt to write tests without knowing how to do that. Forgive me World...

def test_parse_yaml_returns_dict_on_inventory():
    assert type(helpers.parse_yaml('inventory.yaml')) == type({})

def test_parse_yaml_failed_to_find_a_file():
    with pytest.raises(Exception):
        helpers.parse_yaml('imaginary_file.yaml')

def test_yes_or_no_return_true_on_y():
    with mock.patch('builtins.input', return_value="y"):    
        assert helpers.yes_or_no('Question') == True

def test_yes_or_n_exit_on_n():
    with mock.patch('builtins.input', return_value="n"):
        with pytest.raises(SystemExit) as e:
            helpers.yes_or_no('Question')
        assert e.type == SystemExit

def test_yes_or_n_recursion_on_not_y_or_n():
    with mock.patch('builtins.input', return_value="b"):        
        with pytest.raises(RecursionError):
            assert helpers.yes_or_no('Question') == "Uhhhh... please enter Y or N"

def test_hasher_allign_center():
    assert helpers.hasher('BLAH') == '#'*46 + '  BLAH  ' + '#'*46

def test_hasher_allign_left():
    assert helpers.hasher('BLAH', align ='<') == '# BLAH  ' + '#'*92
