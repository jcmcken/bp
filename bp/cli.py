import os
import sys
import optparse
import jinja2
from bp.core import (
    read_context, context_from_expressions, get_writer, context_from_files,
    context_from_opts, context_from_env, Blueprint
)

def create_cli():
    usage = 'usage: %prog <template> [<template> ...] [options]'
    cli = optparse.OptionParser(usage=usage)
    cli.add_option(
        '-c', '--context', action='append', default=[],
        help='specify either a context file or an expression of the form'
             ' KEY=FILE, where KEY is the name of a variable to inject into'
             ' the template context and FILE is a path to a context file.'
             ' The data structure in FILE will be set as the value of KEY.'
    )
    cli.add_option(
        '-d', '--template-dir', action='append', metavar='DIRECTORY',
        default=[],
        help='add a directory to the templating environment'
    )
    cli.add_option(
        '-E', '--extension', action='append', default=[],
        help='add a Jinja2 extension to the rendering environment (can specify '
             'multiple times). This must be an import path string.',
    )
    cli.add_option(
        '-e', '--expr', metavar='KEY=VAL', action='append', dest='expressions',
        default=[],
        help='inject key-value pairs of the form KEY=VAL into the template context, '
             'where the value of KEY in the template will be set to VAL'
    )
    cli.add_option(
        '-f', '--file-expr', metavar='KEY=VAL', action='append', dest='file_expressions',
        default=[],
        help='similar to -e/--expr, except that VAL is treated as a file. The '
             'contents of VAL will be read and set as the value of KEY in the final '
             'template'
    )
    cli.add_option(
        '-I', '--env-expr', metavar='KEY=VAL', action='append',
        dest='env_expressions', default=[],
        help='similar to -e/--expr, except that VAL is treated as the name of '
             'an environment variable. The value of the env var VAL will be'
             ' set as the value of KEY in the final template'
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
    cli.add_option(
        '-n', '--no-sys-context', action='store_false', dest='sys_context',
        help="don't inject built-in `bp' context (e.g. `bp_fqdn') into the template"
             " context"
    )
    cli.add_option(
        '-R', '--recursive', action='store_true', dest='recursive',
        help="if any of <template> arguments are directories, recursively"
             " traverse those directories to find templates to render"
    )
    return cli

CTXTYPES = ['json', 'yaml']

def parse_datatypes(opts):
    datatypes = []
    for i in CTXTYPES:
        val = getattr(opts, i)
        if val is True: datatypes.append(i)
    return datatypes

def find_files(directory):
    files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
             files.append(os.path.join(dirpath, filename))
        for dirname in dirnames:
            files.extend(find_files(os.path.join(dirpath, dirname)))
    return files

def resolve_files(candidates):
    files = []
    for candidate in candidates:
        if os.path.isfile(candidate):
            files.append(candidate)
        elif os.path.isdir(candidate):
            files.extend(find_files(candidate))
    return files

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
        cli.error('requires one or more template files to render')

    for candidate in args:
        if not (os.path.isfile(candidate) or os.path.isdir(candidate)):
            cli.error('no such file or directory: %s' % candidate)
        if os.path.isdir(candidate) and not opts.recursive:
            cli.error('pass the -R/--recursive option to traverse directories')

    template_files = resolve_files(args)

    ctx_data = []

    for expr in opts.context:
        ctx_data.append(context_from_opts(expr, datatype))

    try:
        extra_context = context_from_expressions(opts.expressions)
    except SyntaxError as e:
        cli.error(e.args[0])
    ctx_data.append(extra_context)

    try:
        extra_context = context_from_files(opts.file_expressions)
    except (IOError, SyntaxError) as e:
        cli.error(e.args[0])
    ctx_data.append(extra_context)

    try:
        extra_context = context_from_env(opts.env_expressions)
    except KeyError as e:
        cli.error('environment variable "%s" is not set' % e.args[0])
    ctx_data.append(extra_context)

    # validate no duplicate keys
    keys = []
    for data in ctx_data:
        for key in list(data.keys()):
            if key in keys:
                cli.error("duplicate key '%s' in template context" % key)
            else:
                keys.append(key)

    # populate total context
    context = {}
    [ context.update(i) for i in ctx_data ]

    blueprints = Blueprint.load(
        template_files=template_files,
        template_dirs=opts.template_dir,
        context=context,
        extensions=opts.extension,
        sys_context=opts.sys_context,
    )

    if opts.print_context:
        print(blueprints[0].serialize_context(format=datatype))
        raise SystemExit

    output = ''

    try:
        for b in blueprints:
            output += b.render() + '\n'
    except jinja2.exceptions.UndefinedError as e:
        cli.error('undefined context variable; ' + e.args[0])

    sys.stdout.write(output)
