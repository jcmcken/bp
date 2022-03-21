import unittest
import os
from bp import Blueprint
import jinja2
from bp.core import read_context

def fixture_path(name):
    return os.path.join(os.path.dirname(__file__), 'fixtures', name) 

class BlueprintTestCase(unittest.TestCase):
    def test_jinja_extension_not_loaded(self):
        blueprint = Blueprint(fixture_path('do.txt'), context={'foo': 'bar'}) 
        self.assertRaises(jinja2.TemplateSyntaxError, blueprint.render)

    def test_jinja_extension_loaded(self):
        blueprint = Blueprint(fixture_path('do.txt'), context={'foo': 'bar'},
          extensions=['jinja2.ext.do']) 
        blueprint.render()

    def test_jinja_unset_var(self):
        blueprint = Blueprint(fixture_path('simple.txt'))
        self.assertRaises(jinja2.UndefinedError, blueprint.render)

    def test_jinja_globals(self):
        blueprint = Blueprint(fixture_path('simple.txt'), globals={'foo': 'bar'})
        blueprint.render()

    def test_sys_context(self):
        blueprint = Blueprint(fixture_path('builtin_context.txt'))
        self.assertTrue(bool(blueprint.render().strip()))

    def test_disable_sys_context(self):
        blueprint = Blueprint(fixture_path('builtin_context.txt'), sys_context=False)
        self.assertRaises(jinja2.UndefinedError, blueprint.render)

class UtilTestCase(unittest.TestCase):
    def test_json_reader(self):
        self.assertEqual(
          read_context(fixture_path('simple.json'), datatype='json'),
          {"foo": "bar"}
        )
