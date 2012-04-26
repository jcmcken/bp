import os
import sys
import optparse
import jinja2
from bp.core import create_environment, read_context

def create_cli():
    usage = 'usage: %prog [options] <template> <context>'
    cli = optparse.OptionParser(usage=usage)
    cli.add_option('-O', '--output', metavar='FILENAME',
        help="where to output the rendered template. Default is STDOUT")
    cli.add_option(
        '-d', '--template-dir', action='append', metavar='DIRECTORY', 
        help='add a directory to the templating environment'
    )
    cli.add_option(
        '-j', '--json', action='store_true',
        help='indicates that the context file should be parsed as json (default)'
    )
    cli.add_option(
        '-y', '--yaml', action='store_true',
        help='indicates that the context file should be parsed as yaml'
    )
    return cli

CTXTYPES = ['json', 'yaml']

def parse_datatypes(opts):
    datatypes = []
    for i in CTXTYPES:
        val = getattr(opts, i)
        if val is True: datatypes.append(i)
    return datatypes

def main():
    cli = create_cli()
    opts, args = cli.parse_args()

    if len(args) < 1:
        cli.error('requires a template file to render')
    elif len(args) < 2:
        cli.error('requires a context file to do the rendering')

    # decide which datatype user selected
    datatypes = parse_datatypes(opts)
    if len(datatypes) > 1:
        cli.error('can only specify one context file data type (one of %s)' % ', '.join(CTXTYPES))
    if not datatypes:
        datatype = 'json'
    else:
        datatype = datatypes[0]

    # set defaults
    if opts.output is None: 
        output_fd = sys.stdout
    else:
        output_fd = open(opts.output, 'rb')
    if not opts.template_dir:
        opts.template_dir = []

    # pop user args
    template_file = args.pop(0)
    context_file = args.pop(0)


    environ = create_environment(template_file, opts.template_dir)
    # create and initialize template
    template = environ.get_template(os.path.basename(template_file))
    # read the context file 
    context = read_context(context_file, datatype=datatype)

    try:
        rendered = template.render(context)
    except jinja2.exceptions.UndefinedError, e:
        cli.error('undefined context variable; ' + e.args[0])

    output_fd.write(rendered + '\n')

