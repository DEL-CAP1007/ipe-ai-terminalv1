import click
from src.commands import obs

@click.group()
def cli():
    pass

cli.add_command(obs.obs)

if __name__ == "__main__":
    cli()
