===============
BP (Blueprints)
===============

Intro
-----

BP is a simple CLI for populating Jinja2 templates using JSON or YAML config files for context. BP also accepts context settings passed from the command line.

Usage
-----

    Usage: bp [options] <template> [context_file]
    
    Options:
      -h, --help            show this help message and exit
      -O FILENAME, --output=FILENAME
                            where to output the rendered template. Default is
                            STDOUT
      -d DIRECTORY, --template-dir=DIRECTORY
                            add a directory to the templating environment
      -e EXPRESSION, --expression=EXPRESSION
                            inject key-value pairs into the template context
                            (after [context_file] is parsed)
      -j, --json            indicates that the context file should be parsed as
                            json (default)
      -y, --yaml            indicates that the context file should be parsed as
                            yaml
      -p, --print-context   print out the current context
