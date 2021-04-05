import yaml
import requests
import json
import urllib3
import key
from pprint import pformat

output = '''
# COMMAND: {}
# SUCCESS: {}
# ERROR: {}
# RESULT: 
{}
'''

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_yaml(file):
    with open(file) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    return result


def yes_or_no(question):
    reply = str(input('\n' + question+' (y/n): ')).lower().strip()
    if reply[:1] == 'y':
        return True
    if reply[:1] == 'n':
        print('### ABORTING ###')
        exit()
    else:
        return yes_or_no("Uhhhh... please enter Y or N")


def hasher(your_text, align='^'):
    if align == '^':
        return '{:#^100s}'.format('  '+your_text+'  ')
    elif align == '<':
        return '{:#<100s}'.format('# '+your_text+'  ')
    else:
        raise ValueError('Only ^ and < are supported')


def command_to_dict(command):
    schema = {'op': None, 'path': None}

    operation = command.split()[0]
    path = command.split()[1:]

    if 'show' in operation:
        schema['op'] = 'showConfig'
    elif 'set' in operation:
        schema['op'] = 'set'
    elif 'delete' in operation:
        schema['op'] = 'delete'
    elif 'comment' in operation:
        schema['op'] = 'comment'
    elif 'get' in operation:
        schema['op'] = 'show'
    else:
        raise ValueError('Operation "{}" not supported'.format(operation))

    schema['path'] = path
    return schema


def all_config(list_of_dict):
    intrusive_commands = {'set', 'delete', 'comment'}
    set_of_operations = set(command['op'] for command in list_of_dict)
    if set_of_operations <= intrusive_commands:
        return True
    else:
        return False

def prepare_data(data, api_key):
    '''
    Creating a dictionary which can be accepted by VyOS
    {'data':(None,DATA),{'key':(None,KEY)}
    '''
    to_push = {}
    to_push['data'] = (None, json.dumps(data))
    to_push['key'] = (None,  getattr(key, api_key))
    return to_push


def get_endpoint_for_operation(operation):
    if 'showConfig' in operation:
        return 'retrieve'
    elif 'show' in operation:
        return 'show'
    elif operation in ['set', 'delete', 'comment']:
        return 'configure'
    else:
        raise ValueError('Operation "{}" not supported'.format(operation))


def save_needed(command_list):
    intrusive_commands = {'set', 'delete', 'comment'}
    set_of_operations = set(command.split()[0] for command in command_list)
    if not intrusive_commands.isdisjoint(set_of_operations):
        return True
    else:
        return False


def pusher(target, port, command_list, api_key, brave=False):
    list_of_dict = [command_to_dict(command) for command in command_list]

    if all_config(list_of_dict):
        data = prepare_data(list_of_dict, api_key)
        endpoint = get_endpoint_for_operation(list_of_dict[0]['op'])
        url = 'https://{}:{}/{}'.format(target, port, endpoint)
        if not brave:
            yes_or_no('Do you want to continue?')
        result = requests.post(url, files=data, verify=False)
        return {'batched': True, 'result': json.loads(result.text)}
    else:
        list_or_results = []
        for command in list_of_dict:
            data = prepare_data(command, api_key)
            endpoint = get_endpoint_for_operation(command['op'])
            url = 'https://{}:{}/{}'.format(target, port, endpoint)
            if not brave:
                if endpoint == 'configure':
                    yes_or_no('Do you want to continue?')
            result = requests.post(url, files=data, verify=False)
            list_or_results.append(json.loads(result.text))
        return {'batched': False, 'result': list_or_results}


def show_result(command, result):
    if isinstance(result['data'],str):
        outcome = result['data'].splitlines()
    else:
        outcome = result['data']
    return output.format(command, 
                         result['success'], 
                         result['error'], 
                         pformat(outcome, width=120))


def save_config(target, port, api_key):
    url = 'https://{}:{}/config-file'.format(target, port)
    data = {"op": "save"}
    to_push = prepare_data(data, api_key)
    result = requests.post(url, files=to_push, verify=False)
    return json.loads(result.text)
