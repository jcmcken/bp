import os
import pwd
import jinja2
import datetime
import socket

def create_environment(template_file, env_dirs):
    loader = jinja2.FileSystemLoader(
        [ os.path.dirname(template_file) ] + env_dirs
    )
    env = jinja2.Environment(loader=loader, undefined=jinja2.StrictUndefined)
    return env

def get_json_lib():
    json = None
    for lib in ['json', 'simplejson']:
        try:
            json = __import__(lib)
            break
        except ImportError:
            continue
    return json

def get_reader(datatype):
    if datatype == 'json':
        lib = get_json_lib()
        if not lib: 
            raise ImportError('cannot find a suitable json library')
        else:
            reader = lambda x: lib.load(open(x))
    elif datatype == 'yaml':
        import yaml
        reader = lambda x: yaml.load(open(x, 'rb').read())
    else:
        raise TypeError("invalid type '%s', no backends available" % datatype)
    return reader

def get_writer(datatype):
    if datatype == 'json':
        lib = get_json_lib()
        if not lib: 
            raise ImportError('cannot find a suitable json library')
        else:
            writer = lib.dumps
    elif datatype == 'yaml':
        import yaml
        writer = yaml.dump
    else:
        raise TypeError("invalid type '%s', no backends available" % datatype)
    return writer

def read_context(context_file, datatype):
    read = get_reader(datatype)
    data = read(context_file)
    return data

def parse_expression(expr):
    try:
        key, val = expr.split('=', 1)
    except ValueError:
        raise SyntaxError('could not parse expression "%s"' % expr)
    return key, val

def context_from_files(exprs):
    ctx = {}
    for expr in exprs:
        key, val = parse_expression(expr)
        val = open(val).read()
        ctx[key] = val
    return ctx

def context_from_expressions(exprs):
    ctx = {}
    for expr in exprs:
        key, val = parse_expression(expr)
        ctx[key] = val
    return ctx

def sys_context():
    ctx = {}
    ctx['bp_datetime'] = datetime.datetime.now()
    ctx['bp_hostname'] = socket.gethostname()
    ctx['bp_fqdn'] = socket.getfqdn()
    ctx['bp_user'] = os.getlogin()
    ctx['bp_euser'] = pwd.getpwuid(os.getuid())[0]
    return ctx

