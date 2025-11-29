import click
from dotenv import load_dotenv

load_dotenv()

@click.command()
@click.option('--name', default='world', help='Name to greet')
def main(name):
    """Simple starter CLI."""
    click.echo(f'Hello, {name}!')

if __name__ == '__main__':
    main()
