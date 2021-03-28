import helpers
import click
from pprint import pprint, pformat

output = '''
# COMMAND: {}
# SUCCESS: {}
# ERROR: {}
# RESULT: {}
'''


@click.command()
@click.option('--inventory', '-i', required=True, help='Inventory YAML')
@click.option('--deployment', '-d', required=True, help='Deployment file (YAML)')
@click.option('--no-save', '-ns', is_flag=True, default=False, help='Whether to save config or not')
@click.option('--brave', '-b', is_flag=True, default=False, help='No "Are you sure?" prompt. For brave hearts only')
def deploy(inventory, deployment, no_save, brave):
    helpers.hasher('DEPLOYMENT STARTED')
    inventory = helpers.parse_yaml(inventory)
    deployment = helpers.parse_yaml(deployment)

    for device, data in inventory.items():
        helpers.hasher('Starting "{}"'.format(device.upper()))
        for stage, commands in deployment.items():
            helpers.hasher('{} PHASE'.format(stage.upper()), align='<')
            pprint(commands)

            results = helpers.pusher(
                data['address'], commands, data['key_name'], brave)
            zipped = zip(commands, results)
            helpers.hasher('RESULTS', align='<')
            for result in zipped:
                print(output.format(
                    result[0],
                    result[1]['success'],
                    result[1]['error'],
                    pformat(result[1]['data'])
                ))

        if not no_save:
            helpers.hasher('SAVING CONFIGURATION')
            result = helpers.save_config(data['address'], data['key_name'])
            print(output.format('Save config',
                  result['success'], result['error'], result['data']))


if __name__ == '__main__':
    deploy()
