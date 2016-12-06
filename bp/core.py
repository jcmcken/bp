import os
import pwd
import jinja2
import datetime
import socket
from copy import deepcopy

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
            writer = lambda x: lib.dumps(x, sort_keys=False, indent=4)
    elif datatype == 'yaml':
        import yaml
        writer = lambda x: "---\n" + yaml.dump(x, default_flow_style=False)
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

def context_from_opts(opt, datatype):
    if '=' in opt:
        ctx = {}
        key, filename = parse_expression(opt)
        data = read_context(filename, datatype)
        ctx[key] = data
    else:
        ctx = read_context(opt, datatype)
    return ctx

class Blueprint(object):
    def __init__(self, template_file, template_dirs=None, context=None, **kwargs):
        self.template_file = template_file
        self.template_dirs = template_dirs or []
        self.context = context or {}
        self.jinja_environment_kwargs = kwargs

    def _create_environ(self):
        loader = jinja2.FileSystemLoader(
            [ os.path.dirname(self.template_file) ] + self.template_dirs
        )
        kwargs = {}
        kwargs.update(self.jinja_environment_kwargs)
        kwargs['loader'] = loader
        kwargs['undefined'] = jinja2.StrictUndefined

        filters = kwargs.pop('filters', {})
        globals = kwargs.pop('globals', {})

        environ = jinja2.Environment(**kwargs)
        environ.filters.update(filters)
        environ.globals.update(globals)
        return environ

    def _create_template(self):
        env = self._create_environ()
        return env.get_template(os.path.basename(self.template_file))

    def _sys_context(self):
        try:
          bp_user = os.getlogin()
        except OSError:
          bp_user = None
        return {
            'bp_datetime': datetime.datetime.now(),
            'bp_hostname': socket.gethostname(),
            'bp_fqdn': socket.getfqdn(),
            'bp_user': bp_user,
            'bp_euser': pwd.getpwuid(os.getuid())[0],
        }

    def _preprocess_ctx_for_writing(self, ctx):
        ctx['bp_datetime'] = ctx['bp_datetime'].isoformat()
        return ctx

    def serialize_context(self, format='json'):
        ctx = self._build_context()
        self._preprocess_ctx_for_writing(ctx)
        write = get_writer(format)
        return write(ctx)

    def _build_context(self, context=None):
        ctx = deepcopy(context or {})
        ctx.update(self.context)
        ctx.update(self._sys_context())
        return ctx

    def render(self, *args, **kwargs):
        full_ctx = self._build_context(dict(*args, **kwargs))
        template = self._create_template()
        return template.render(full_ctx)
