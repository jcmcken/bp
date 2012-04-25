import optparse

def create_cli():
    cli = optparse.OptionParser()
    cli.add_option(
        '-f', '--template-file', action='append', metavar='TEMPLATE',
        help='Add a template file to the templating environment'
    )
    cli.add_option(
        '-d', '--template-dir', action='append', metavar='DIRECTORY', 
        help='Add a directory to the templating environment'
    )
    return cli

def main():
    cli = create_cli()
    opts, args = cli.parse_args()
