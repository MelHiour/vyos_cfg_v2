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
{}'''

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_yaml(filename):
    '''
    Converting a YAML file into Python native data structures.
    args: filename (str)
    returns: native data structures
    '''
    with open(filename) as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    return result


def yes_or_no(question):
    '''
    Checks what user thinks about the question.
    args: question (str)
    returns: True or just exit
    '''
    reply = str(input('\n' + question+' (y/n): ')).lower().strip()
    if reply[:1] == 'y':
        return True
    if reply[:1] == 'n':
        print('### ABORTING ###')
        exit()
    else:
        return yes_or_no("Uhhhh... please enter Y or N")


def hasher(your_text, align='^'):
    '''
    Just to format a string using hashes.
    args: your_text (str), align(str) = [<^]
    returns: formatted string
    '''
    if align == '^':
        return '{:#^100s}'.format('  '+your_text+'  ')
    elif align == '<':
        return '{:#<100s}'.format('# '+your_text+'  ')
    else:
        raise ValueError('Only ^ and < are supported')


def command_to_dict(command):
    '''
    Converts the command string into a dictionary {'op': , 'path': []}
    args: command (str)
    returns: dictionary
    '''
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
    '''
    We need to check if all commands are intrusive (set,delete,comment).
    The reason is we need to commit such commands together.
    args: list_of_dict(list) [{'op': , 'path': []}, {'op': , 'path': []}]
    returns: True/False
    '''
    intrusive_commands = {'set', 'delete', 'comment'}
    set_of_operations = set(command['op'] for command in list_of_dict)
    if set_of_operations <= intrusive_commands:
        return True
    else:
        return False


def prepare_data(data, api_key):
    '''
    Creating a dictionary which can be accepted by VyOS
    args: 
    data(native data structures), 
    api_key(str) - the name of the key from key.py
    returns: to_push(dict)
    {'data':(None,DATA),{'key':(None,KEY)}
    '''
    to_push = {}
    to_push['data'] = (None, json.dumps(data))
    to_push['key'] = (None,  getattr(key, api_key))
    return to_push


def get_endpoint_for_operation(operation):
    '''
    Returning the name of endpoint based on operation
    args: operation (str)
    returns: endpoint (str)
    '''
    if 'showConfig' in operation:
        return 'retrieve'
    elif 'show' in operation:
        return 'show'
    elif operation in ['set', 'delete', 'comment']:
        return 'configure'
    else:
        raise ValueError('Operation "{}" not supported'.format(operation))


def save_needed(command_list):
    '''
    We need to know if we need to save after pushing the command list.
    Execution of show-like commands only does not require it.
    args: command_list(list)
    returns: True/False
    '''
    intrusive_commands = {'set', 'delete', 'comment'}
    set_of_operations = set(command.split()[0] for command in command_list)
    if not intrusive_commands.isdisjoint(set_of_operations):
        return True
    else:
        return False


def pusher(target, port, command_list, api_key, brave=False):
    '''
    Main function to push the data using API  
    args: 
    target(str) - IP address or hostname
    port(str) - TCP port
    command_list (list) - the list of commands to push
    api_key(str) - the name of the key from key.py
    brave(True/False) - skipping Yes/No question before intrusive commands
    returns: dictionary with keys
       'batched': True/False (shows if all commands have been commited together
       'result': list of dictionaries per command or just one dictionary in case of batch
    '''
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
    '''
    Helps formatting the output of the command sent.
    Formatting strings differently. Needed mainly for get commands.
    args: command (str)  
    returns: result (dict)
    '''
    if isinstance(result['data'], str):
        outcome = result['data'].splitlines()
    else:
        outcome = result['data']
    return output.format(command,
                         result['success'],
                         result['error'],
                         pformat(outcome, width=120))


def save_config(target, port, api_key):
    '''
    Just saving the configuration.
    args: 
    target(str) - IP address or hostname
    port(str) - TCP port
    api_key(str) - the name of the key from key.py
    '''
    url = 'https://{}:{}/config-file'.format(target, port)
    data = {"op": "save"}
    to_push = prepare_data(data, api_key)
    result = requests.post(url, files=to_push, verify=False)
    return json.loads(result.text)
