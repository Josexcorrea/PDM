import click 
from hardware.commands import Commands
from api.route  import run_server
@click.command()
@click.option(
    '--baud_rate',
    default=9600, 
    help='Baud rate for communication'
)
@click.option(
        '--find_devices',
        default=False,  
        help='List of COM devices'
)
@click.option(
        '--device',
        default="",  
        help='COM port for the device.'
)
@click.option(
        '--add_channel',
        is_flag=True,  
        help='Adds a new channel.'
)
@click.option(
        '--set_channel',
        is_flag=True,  
        help='Sets a channel ON or OFF.'
)
@click.option(
        '--set_current',
        is_flag=True,  
        help='Sets a channel ON or OFF.'
)
@click.option(
    '--start_server',
    is_flag=True,
    help='Flag to start the server'
)
@click.option(
    '--get_params',
    is_flag=True,
    help='Flag to get channel parameter details.',
)
@click.option(
        '--channel_number',
        default=-1,  
        help='Channel number for power output.'
)
@click.option(
        '--status',
        default=False,  
        help='Status dictates ON or OFF option.'
)
@click.option(
        '--current_limit',
        default=0.00,  
        help='Status dictates ON or OFF option.'
)
def pdm_cli(
    find_devices: bool, 
    baud_rate: int, 
    device: str, 
    current_limit: float,
    add_channel: bool,
    set_channel: bool,
    set_current: bool,
    get_params: bool,
    start_server: bool,
    channel_number: int,
    status: bool
) -> None:
    if add_channel:
        if(device != ""):
            print("IN HERE")
            Commands.command_add_channel(device)
    elif set_channel: 
        if (channel_number != -1):
            Commands.command_set_channel(device, channel_number, status)
    elif get_params:
        if (channel_number != -1):
            Commands.command_get_param(device, channel_number)
    elif set_current:
        if (channel_number != -1):
            Commands.command_set_current(device, channel_number, current_limit)
    elif start_server:
        run_server()
if __name__ == '__main__':
    pdm_cli()
