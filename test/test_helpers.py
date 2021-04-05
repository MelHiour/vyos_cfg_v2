import pytest
import mock
import requests_mock
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
            assert helpers.yes_or_no(
                'Question') == "Uhhhh... please enter Y or N"


def test_yes_or_no_wrong_input():
    with pytest.raises(Exception):
        helpers.yes_or_no(300)


def test_hasher_allign_center():
    assert helpers.hasher('BLAH') == '#'*46 + '  BLAH  ' + '#'*46


def test_hasher_allign_left():
    assert helpers.hasher('BLAH', align='<') == '# BLAH  ' + '#'*92


def test_hasher_raises_an_error_on_unkonwn_arg():
    with pytest.raises(ValueError):
        helpers.hasher('BLAH', align='>')


@pytest.mark.parametrize("test_input,expected", [
    ('show interface', {'op': 'showConfig', 'path': ['interface']}),
    ('set interface', {'op': 'set', 'path': ['interface']}),
    ('delete interface', {'op': 'delete', 'path': ['interface']}),
    ('comment interface', {'op': 'comment', 'path': ['interface']})])
def test_command_to_dict_inputs(test_input, expected):
    assert helpers.command_to_dict(test_input) == expected


def test_command_to_dict_raises_error_on_unknown_op():
    with pytest.raises(ValueError):
        helpers.command_to_dict('get interface')


def test_command_to_dict_wrong_input():
    with pytest.raises(Exception):
        helpers.command_to_dict(300)


@pytest.mark.parametrize("test_input,expected", [
    ([{'op': 'showConfig'}, {'op': 'set'}], False),
    ([{'op': 'delete'}, {'op': 'set'}], True)])
def test_all_config_inputs(test_input, expected):
    assert helpers.all_config(test_input) == expected


def test_all_config_wrong_input():
    with pytest.raises(Exception):
        helpers.all_config(300)


def test_prepare_data_happy_path():
    with mock.patch('key.default', '12345'):
        assert helpers.prepare_data('DATA', 'default') == {
            'data': (None, '"DATA"'), 'key': (None, '12345')}


def test_prepare_data_wrong_name():
    with mock.patch('key.default', '12345'):
        with pytest.raises(AttributeError):
            helpers.prepare_data('DATA', 'blah')


def test_prepare_data_wrong_input():
    with pytest.raises(Exception):
        helpers.prepare_data(300, 300)


@pytest.mark.parametrize("test_input,expected", [
    ('showConfig', 'retrieve'),
    ('set', 'configure'),
    ('delete', 'configure'),
    ('comment', 'configure')])
def test_get_endpoint_for_operation_inputs(test_input, expected):
    assert helpers.get_endpoint_for_operation(test_input) == expected


def test_get_endpoint_for_operation_unknown_op():
    with pytest.raises(ValueError):
        helpers.get_endpoint_for_operation('blah')


def test_get_endpoint_for_operation_wrong_input():
    with pytest.raises(Exception):
        helpers.get_endpoint_for_operation(300)

@pytest.mark.parametrize("test_input,expected", [
    (['show config', 'show config'], False),
    (['show config', 'delete config'], True),
    (['show config', 'comment config'], True),
    (['show config', 'set config'], True),
    (['set config', 'set config'], True),
    (['set config', 'delete config'], True),
    (['set config', 'comment config'], True),
    (['delete config', 'delete config'], True),
    (['delete config', 'comment config'], True),
    (['comment config', 'comment config'], True)
    ])
def test_save_needed_inputs(test_input, expected):
    assert helpers.save_needed(test_input) == expected    

def test_pusher_set_commands_succesful():
    with requests_mock.Mocker() as mock:
        result = '{"success": true, "data": null, "error": null}'
        expected = {'batched': True, 'result': {
            "success": True, "data": None, "error": None}}
        mock.post('https://192.0.2.2:443/configure', text=str(result))
        gotten = helpers.pusher(
            '192.0.2.2','443', ['set system host-name test'], 'default', brave=True)
        assert gotten == expected


def test_pusher_show_commands_succesful():
    with requests_mock.Mocker() as mock:
        result = '{"success": true, "data": {"ethernet": {"eth0": {"address": "192.168.0.14/24", "hw-id": "50:01:00:04:00:00"}}}, "error": null}'
        expected = {'batched': False, 'result': [{"success": True, "data": {"ethernet": {
            "eth0": {"address": "192.168.0.14/24", "hw-id": "50:01:00:04:00:00"}}}, "error": None}]}
        mock.post('https://192.0.2.2:443/retrieve', text=str(result))
        gotten = helpers.pusher(
            '192.0.2.2', '443', ['show inteface ethernet'], 'default', brave=True)
        assert gotten == expected


def test_pusher_not_brave_shows_input(capsys):
    with mock.patch('builtins.input', return_value="n"):
        with pytest.raises(SystemExit) as e:
            helpers.pusher(
                '192.0.2.2', '443', ['set system host-name test'], 'default')
            assert e.type == SystemExit


def test_show_result_succesful():
    expected = '\n# COMMAND: some_command\n# SUCCESS: True\n# ERROR: None\n# RESULT: None\n'
    gotten = helpers.show_result(
        'some_command', {"success": True, "data": None, "error": None})
    assert gotten == expected


def test_show_result_wrong_input():
    with pytest.raises(Exception):
        helpers.show_result(300, [])


def test_save_config_succesful():
    with requests_mock.Mocker() as mock:
        result = '{"success": true, "data": "Saving configuration to \'/config/config.boot\'...\\nDone\\n", "error": null}'
        mock.post('https://192.0.2.2:443/config-file', text=str(result))
        assert helpers.save_config('192.0.2.2', '443', 'default') == {
            'success': True, 'data': "Saving configuration to '/config/config.boot'...\nDone\n", 'error': None}


def test_save_config_wrong_ip():
    with pytest.raises(Exception):
        helpers.helpers.save_config('192.0.2.2', '443', 'default')
