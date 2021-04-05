import helpers
import click
from pprint import pprint


@click.command()
@click.option('--inventory', '-i', required=True, help='Inventory YAML')
@click.option('--deployment', '-d', required=True, help='Deployment file (YAML)')
@click.option('--skip-save', '-s', is_flag=True, default=False, help='Whether to skip save config or not')
@click.option('--brave', '-b', is_flag=True, default=False, help='No "Are you sure?" prompt. For brave hearts only')
def deploy(inventory, deployment, skip_save, brave):
    print(helpers.hasher('DEPLOYMENT STARTED'))
    inventory = helpers.parse_yaml(inventory)
    deployment = helpers.parse_yaml(deployment)

    for device, data in inventory.items():
        save_needed = False
        print(helpers.hasher('Starting "{}"'.format(device.upper())))
        for stage, commands in deployment.items():
            print(helpers.hasher('{} PHASE'.format(stage.upper()), align='<'))
            pprint(commands)

            results = helpers.pusher(
                data['address'], data['port'], commands, data['key_name'], brave)
            print(helpers.hasher('RESULTS', align='<'))
            if results['batched']:
                print(helpers.show_result(
                    'Batched push of commands above', results['result']))
            else:
                zipped = zip(commands, results['result'])
                for result in zipped:
                    print(helpers.show_result(result[0], result[1]))
            if not save_needed:
                save_needed = helpers.save_needed(commands)
        if not skip_save:
            if save_needed:
                print(helpers.hasher('SAVING CONFIGURATION'))
                result = helpers.save_config(
                    data['address'], data['port'], data['key_name'])
                print(helpers.show_result('Save config', result))


if __name__ == '__main__':
    deploy()
