import os
import sys
import optparse
import jinja2
from bp.core import (
    create_environment, read_context, context_from_expressions, sys_context,
    get_writer, context_from_files, prepare_context_for_writing,
    context_from_opts
)

def create_cli():
    usage = 'usage: %prog <template> [options]'
    cli = optparse.OptionParser(usage=usage)
    cli.add_option(
        '-c', '--context', action='append',
        help='specify either a context file or an expression of the form'
             ' KEY=FILE, where KEY is the name of a variable to inject into'
             ' the template context and FILE is a path to a context file.'
             ' The data structure in FILE will be set as the value of KEY.'
    )
    cli.add_option(
        '-d', '--template-dir', action='append', metavar='DIRECTORY', 
        help='add a directory to the templating environment'
    )
    cli.add_option(
        '-e', '--expr', metavar='KEY=VAL', action='append', dest='expressions',
        help='inject key-value pairs of the form KEY=VAL into the template context, '
             'where the value of KEY in the template will be set to VAL'
    )
    cli.add_option(
        '-f', '--file-expr', metavar='KEY=VAL', action='append', dest='file_expressions',
        help='similar to -e/--expr, except that VAL is treated as a file. The '
             'contents of VAL will be read and set as the value of KEY in the final '
             'template'
    )
    cli.add_option(
        '-j', '--json', action='store_true',
        help='indicates that the context file should be parsed as JSON (default)'
    )
    cli.add_option(
        '-y', '--yaml', action='store_true',
        help='indicates that the context file should be parsed as YAML'
    )
    cli.add_option(
        '-p', '--print-context', action='store_true',
        help='print out the context that will be applied to <template> and exit'
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

    if len(args) != 1:
        cli.error('requires a template file to render')

    template_file = args[0]

    if opts.context is None:
        opts.context = [] 

    if opts.expressions is None:
        opts.expressions = []

    if opts.file_expressions is None:
        opts.file_expressions = []

    if not opts.template_dir:
        opts.template_dir = []

    ctx_data = []

    for expr in opts.context:
        ctx_data.append(context_from_opts(expr, datatype))
    
    try:
        extra_context = context_from_expressions(opts.expressions)
    except SyntaxError, e:
        cli.error(e.args[0])
    ctx_data.append(extra_context)

    try:
        extra_context = context_from_files(opts.file_expressions)
    except (IOError, SyntaxError), e:
        cli.error(e.args[0])
    ctx_data.append(extra_context)

    # now add built-in context
    ctx_data.append(sys_context())

    # validate no duplicate keys
    keys = []
    for data in ctx_data:
        for key in data.keys():
            if key in keys:
                cli.error("duplicate key '%s' in template context" % key)
            else:
                keys.append(key)

    # populate total context
    context = {}
    [ context.update(i) for i in ctx_data ]

    if opts.print_context:
        context = prepare_context_for_writing(context)
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

    sys.stdout.write(rendered + '\n')

