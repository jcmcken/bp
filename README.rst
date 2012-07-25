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

    bp <template_file> [options]

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
    [jcmcken@localhost ~]$ bp index.html -c page.json
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

Advanced Usage
--------------

While not really "advanced" per se, there's an additional feature of the ``-c/--context``
option which provides an even finer level control over contexts.

You can pass an expression of the form ``<key>=<filename>`` to ``-c``, where ``<key>``
is the name of a variable to inject into the template context and ``<filename>`` is
a serialized data structure (JSON or YAML) just like before.

Using this syntax, the template context will contain a variable ``<key>`` set equal
to the data structure loaded from ``<filename>``.

This has two useful benefits:

* Context files that are not hashes can be named and turned into hashes. 
  For example, if you have a JSON file with a list of data items, you can
  assign a name to that list using ``-c`` without having to rewrite the JSON
  file as a hash map.

* You can use it to deconflict data structures with common keys. For example,
  if you have data about employees, ``salaries.json`` and ``ranks.json``, but 
  the data in each file is keyed off of employees names, e.g. 
  ``{ "Bob": 65000 }`` and ``{ "Bob": "Engineer" }`` (respectively), then
  you can simply pass ``-c salaries=salaries.json`` and ``-c ranks=ranks.json``
  to create the following merged context:

  ::

      { 
        "salaries": {
          "Bob": 65000
        },
        "ranks": {
          "Bob": "Engineer"
        }
      }

   This means that you can (if need be) decouple your data into separate files
   rather than keeping very large, aggregated files.

More on Contexts
----------------

Note that the root-level data structure in the JSON file is always a hash (also called a dictionary, if you're a Python person). This is a hard requirement of the underlying templating engine. You're passing a namespace to the template -- in other words, data items are retrieved by their names. The internal structure of the hash can be arbitrarily complex, just so long as your template is expecting that structure.

If you prefer something a bit easier to read, you can use YAML files rather than JSON. To do this, just pass the ``-y``/``--yaml`` option flag along with the other arguments. (Remember, YAML is a superset of JSON, so passing ``-y`` will let you use either JSON or YAML).

Passing in the context from a YAML file:

::

    [jcmcken@localhost ~]$ cat page.yaml
    ---
    section: Contact
    [jcmcken@localhost ~]$ bp index.html -c page.yaml --yaml
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
    bp contact.html -c contacts.json >> $DEPLOY/contacts.html
    bp about.html -f founder_txt=content/about/founder.txt \
                  -f employees=content/about/employees.txt >> $DEPLOY/about.html


 
