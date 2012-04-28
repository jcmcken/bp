import os
import jinja2

def create_environment(template_file, env_dirs):
    loader = jinja2.FileSystemLoader(
        [ os.path.dirname(template_file) ] + env_dirs
    )
    env = jinja2.Environment(loader=loader, undefined=jinja2.StrictUndefined)
    return env

def get_reader(datatype):
    if datatype == 'json':
        selected_lib = None
        for lib in ['json', 'simplejson', 'cjson']:
            try:
                json = __import__(lib)
                selected_lib = lib
            except ImportError:
                continue
        if not selected_lib: 
            raise ImportError('cannot find a suitable json library')
        elif selected_lib in ['json', 'simplejson']:
            reader = json.load
        elif selected_lib == 'cjson':
            reader = lambda x: json.decode(open(x, 'rb').read())
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

