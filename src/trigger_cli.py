import click
from src.commands import trigger

@click.group()
def cli():
    pass

cli.add_command(trigger.trigger)

if __name__ == "__main__":
    cli()
