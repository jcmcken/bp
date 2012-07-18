===============
BP (Blueprints)
===============

Intro
-----

BP is a simple CLI for populating Jinja2 templates using JSON or YAML config files for context. BP also accepts context settings passed from the command line.

Tour
----

Basic usage:

::

    bp <template_file> [context_file]

For example, suppose you have the following template called ``index.html``:

::

    <html>
     <head>
       <title>StartUp - {{ section|default('Home') }}</title>
     </head>
     <body>Welcome!</body>
    </html>

This template can (optionally) take a context variable called ``section``. If ``section`` is not supplied, it defaults to ``Home``. 

A demonstration:

::

    [jcmcken@localhost ~]$ bp index.html 
    <html>
    <head>
        <title>StartUp - Home</title>
    </head>
    <body>Welcome!</body>
    </html>

Passing in a custom ``section`` from the command line:

::

    [jcmcken@localhost ~]$ bp index.html -e section=Contact
    <html>
    <head>
        <title>StartUp - Contact</title>
    </head>
    <body>Welcome!</body>
    </html>

Passing in the context from a JSON file:

::

    [jcmcken@localhost ~]$ cat page.json
    {
      "section": "Contact"
    }
    [jcmcken@localhost ~]$ bp index.html page.json
    <html>
    <head>
        <title>StartUp - Contact</title>
    </head>
    <body>Welcome!</body>
    </html>

Passing in the context from the contents of a separate file:

::

    [jcmcken@localhost ~]$ cat contact_section.txt
    Contact
    [jcmcken@localhost ~]$ bp index.html -f section=contact_section.txt
    <html>
    <head>
        <title>StartUp - Contact</title>
    </head>
    <body>Welcome!</body>
    </html>

Obviously these examples are pretty contrived, but you can see how each of them
might be useful. If you have "pivot" data that is very simple, but changes depending
on some condition, you could use the ``-e``/``--expr`` option or pass in the appropriate
JSON or YAML config file. On the other hand, if you have dense content (paragraphs of text,
for example), you might prefer to keep that content in separate text files and just read
out of those files.

More on Contexts
----------------

Note that the root-level data structure in the JSON file is a hash (also called a dictionary, if you're a Python person). This is a hard requirement of the underlying templating engine. You're passing a namespace to the template -- in other words, data items are retrieved by their names. The internal structure of the hash can be arbitrarily complex, just so long as your template is expecting that structure.

If you prefer something a bit easier to read, you can use YAML files rather than JSON. To do this, just pass the ``-y``/``--yaml`` option flag along with the other arguments. (Remember, YAML is a superset of JSON, so passing ``-y`` will let you use either JSON or YAML).

Passing in the context from a YAML file:

::

    [jcmcken@localhost ~]$ cat page.yaml
    ---
    section: Contact
    [jcmcken@localhost ~]$ bp index.html page.yaml --yaml
    <html>
    <head>
        <title>StartUp - Contact</title>
    </head>
    <body>Welcome!</body>
    </html>

Since ``bp`` utilizes the Jinja2 templating engine, you can also use template inheritance. To make this easier ``bp`` provides an option for adding directories to the templating environment.

For example, suppose you have a template called ``customized.template`` which inherits from templates spread across multiple directories. Just include all the directories using the ``-d`` option flag:

::

    [jcmcken@localhost ~]$ bp customized.template -d templates/base/ -d templates/add-ons/

Without using the ``-d`` option, you'll likely get a ``TemplateNotFound`` exception for referencing a template that's not in your templating environment.

Built-In Context
----------------

For convenience, ``bp`` also includes some built-in context variables. These will automatically be injected into any templates ``bp`` renders.

* ``bp_datetime``: The ``datetime`` object created with ``datetime.datetime.now()``. 
  (You can either call ``{{ bp_datetime }}`` directly to print the full timestamp, or
  access the ``datetime`` attributes, e.g. ``{{ bp_datetime.year }}``).

  Note: When using the ``-p/--print-context`` option, ``bp_datetime`` will be printed as
  an ISO formatted timestamp (since ``datetime.datetime`` objects are not JSON-serializable)

* ``bp_euser``: The current effective user.
* ``bp_fqdn``: The fully-qualified domain name of the current host
* ``bp_hostname``: The short hostname of the current host
* ``bp_user``: The current login user.

Glueing your Blueprints Together
--------------------------------

Because it seemed to be more effort than it was worth, ``bp`` has no mechanism other than
the command line for rendering templates. I tossed around the idea of using a config file
of some kind, but figured it would be easier just to use simple shell scripts.

So, you need to generate a series of static web pages? Just write a script.

::

    #!/bin/bash

    DEPLOY="/var/www/html"

    bp index.html -f intro=content/index/intro.txt >> $DEPLOY/index.html
    bp contact.html contacts.json >> $DEPLOY/contacts.html
    bp about.html -f founder_txt=content/about/founder.txt \
                  -f employees=content/about/employees.txt >> $DEPLOY/about.html


 
