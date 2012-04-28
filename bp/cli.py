import os
import sys
import optparse
import jinja2
from bp.core import (
    create_environment, read_context, parse_expressions, sys_context,
    get_writer
)

def create_cli():
    usage = 'usage: %prog [options] <template> [context_file]'
    cli = optparse.OptionParser(usage=usage)
    cli.add_option('-O', '--output', metavar='FILENAME',
        help="where to output the rendered template. Default is STDOUT")
    cli.add_option(
        '-d', '--template-dir', action='append', metavar='DIRECTORY', 
        help='add a directory to the templating environment'
    )
    cli.add_option(
        '-e', '--expression', action='append',
        help='inject key-value pairs into the template context '
             '(after [context_file] is parsed)'
    )
    cli.add_option(
        '-j', '--json', action='store_true',
        help='indicates that the context file should be parsed as json (default)'
    )
    cli.add_option(
        '-y', '--yaml', action='store_true',
        help='indicates that the context file should be parsed as yaml'
    )
    cli.add_option(
        '-p', '--print-context', action='store_true',
        help='print out the current context'
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
    
    # decide which datatype user selected
    datatypes = parse_datatypes(opts)
    if len(datatypes) > 1:
        cli.error('can only specify one context file data type (one of %s)' % ', '.join(CTXTYPES))
    if not datatypes:
        datatype = 'json'
    else:
        datatype = datatypes[0]

    if len(args) < 1:
        cli.error('requires a template file to render')

    template_file = args[0]

    if len(args) < 2:
        context = {}    
    else:
        context_file = args[1]
        context = read_context(context_file, datatype=datatype)
    
    if opts.expression is None:
        opts.expression = []

    if opts.output is None: 
        output_fd = sys.stdout
    else:
        output_fd = open(opts.output, 'rb')
    if not opts.template_dir:
        opts.template_dir = []
    
    try:
        extra_context = parse_expressions(opts.expression)
    except SyntaxError, e:
        cli.error(e.args[0])
    context.update(extra_context)
    context.update(sys_context())

    if opts.print_context:
        write = get_writer(datatype)
        print write(context)
        raise SystemExit

    environ = create_environment(template_file, opts.template_dir)
    # create and initialize template
    template = environ.get_template(os.path.basename(template_file))

    try:
        rendered = template.render(context)
    except jinja2.exceptions.UndefinedError, e:
        cli.error('undefined context variable; ' + e.args[0])

    output_fd.write(rendered + '\n')

