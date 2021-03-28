import helpers 
from pprint import pprint,pformat

output = '''
# COMMAND: {}
# SUCCESS: {}
# ERROR: {}
# RESULT: {}
'''
def hasher(your_text, align='^'):
    if align == '^':
        print('{:#^70s}'.format('  '+your_text+'  '))
    elif align == '<':
        print('{:#<70s}'.format('# '+your_text+'  '))
    else:
        raise ValueError ('Only ^ and < are supported')

def deploy(inventory_yaml, deployment_yaml):
    hasher('DEPLOYMENT STARTED')
    inventory = helpers.parse_yaml(inventory_yaml)
    deployment = helpers.parse_yaml(deployment_yaml)

    for device,data in inventory.items():
        hasher('Starting "{}"'.format(device.upper()))
        for stage,commands in deployment.items():
            hasher('{} PHASE'.format(stage.upper()), align='<')
            pprint(commands)
            results = helpers.pusher(data['address'], commands, data['key_name'])
            zipped = zip(commands,results)
            hasher('RESULTS', align = '<')
            for result in zipped:
                print(output.format(
                     result[0],
                     result[1]['success'],
                     result[1]['error'],
                     pformat(result[1]['data'])
                ))

if __name__ == '__main__':
    deploy('inventory.yaml','deployment.yaml')
