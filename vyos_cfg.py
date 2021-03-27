import helpers 
from tabulate import tabulate
from pprint import pprint,pformat

output = '''
# COMMAND: {}
# SUCCESS: {}
# ERROR: {}
# RESULT: {}
'''

def border_print(something):
    print(tabulate([[something]], tablefmt = 'grid'))

def deploy(inventory_yaml, deployment_yaml):
    border_print('STARTING DEPLOYMENT')

    inventory = helpers.parse_yaml(inventory_yaml)
    print('Inventory in {} parsed'.format(inventory_yaml))

    deployment = helpers.parse_yaml(deployment_yaml)
    print('Deployment plan in {} parsed\n'.format(deployment_yaml))

    for device,data in inventory.items():
        border_print('Starting deployment for "{}"'.format(device.upper()))
        for stage,commands in deployment.items():
            print('# Starting "{}" phase'.format(stage.upper()))
            print('# Excecuting the following commands')
            pprint(commands)
            helpers.yes_or_no('Do you want to continue?')
            results = helpers.pusher(data['address'], commands, data['key_name'])
            zipped = zip(commands,results)
            for result in zipped:
                border_print(output.format(
                     result[0],
                     result[1]['success'],
                     result[1]['error'],
                     pformat(result[1]['data'])
                ))

if __name__ == '__main__':
    deploy('inventory.yaml','deployment.yaml')
