import os
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
    for lib in ['json', 'simplejson', 'cjson']:
        try:
            json = __import__(lib)
        except ImportError:
            continue
    return json

def get_reader(datatype):
    if datatype == 'json':
        lib = get_json_lib()
        lib_name = lib.__name__
        if not lib_name: 
            raise ImportError('cannot find a suitable json library')
        elif lib_name in ['json', 'simplejson']:
            reader = lib.load
        elif lib_name == 'cjson':
            reader = lambda x: lib.decode(open(x, 'rb').read())
    elif datatype == 'yaml':
        import yaml
        reader = lambda x: yaml.load(open(x, 'rb').read())
    else:
        raise TypeError("invalid type '%s', no backends available" % datatype)
    return reader

def read_context(context_file, datatype):
    read = get_reader(datatype)
    data = read(context_file)
    return data

def parse_expressions(exprs):
    ctx = {}
    for expr in exprs:
        try:
            key, val = expr.split('=', 1)
        except ValueError:
            raise SyntaxError('could not parse expression "%s"' % expr)
        ctx[key] = val
    return ctx

def sys_context():
    ctx = {}
    now = datetime.datetime.now()
    ctx['bp.date'] = "%s/%s/%s" % (now.month, now.day, now.year)
    ctx['bp.time'] = "%s:%s:%s" % (now.hour, now.minute, now.second)
    ctx['bp.hostname'] = socket.gethostname()
    ctx['bp.fqdn'] = socket.getfqdn()
    return ctx

