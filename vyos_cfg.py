import helpers
from pprint import pprint, pformat

output = '''
# COMMAND: {}
# SUCCESS: {}
# ERROR: {}
# RESULT: {}
'''


def deploy(inventory_yaml, deployment_yaml, save_config=True, brave_mode=False):
    helpers.hasher('DEPLOYMENT STARTED')
    inventory = helpers.parse_yaml(inventory_yaml)
    deployment = helpers.parse_yaml(deployment_yaml)

    for device, data in inventory.items():
        helpers.hasher('Starting "{}"'.format(device.upper()))
        for stage, commands in deployment.items():
            helpers.hasher('{} PHASE'.format(stage.upper()), align='<')
            pprint(commands)

            results = helpers.pusher(
                data['address'], commands, data['key_name'], brave=brave_mode)
            zipped = zip(commands, results)
            helpers.hasher('RESULTS', align='<')
            for result in zipped:
                print(output.format(
                    result[0],
                    result[1]['success'],
                    result[1]['error'],
                    pformat(result[1]['data'])
                ))

        if save_config:
            helpers.hasher('SAVING CONFIGURATION')
            result = helpers.save_config(data['address'], data['key_name'])
            print(output.format('Save config',
                  result['success'], result['error'], result['data']))


if __name__ == '__main__':
    deploy('inventory.yaml', 'deployment.yaml', brave_mode=False)
