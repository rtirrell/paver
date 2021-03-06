"""Miscellaneous tasks that don't fit into one of the other groupings."""
import pkgutil
import zipfile
from StringIO import StringIO
from os.path import join, dirname, exists, abspath
from paver.easy import dry, task
from paver.tasks import VERSION

_docsdir = join(dirname(__file__), "docs")
if exists(_docsdir):
    @task
    def paverdocs():
        """Open your web browser and display Paver's documentation."""
        import webbrowser
        webbrowser.open("file://%s"  % join(abspath(_docsdir), 'index.html') )
        
@task
def minilib(options):
    """Create a Paver mini library that contains enough for a simple
    pavement.py to be installed using a generated setup.py. This
    is a good temporary measure until more people have deployed paver.
    The output file is 'paver-minilib.zip' in the current directory.
    
    Options:
    
    extra_files
        list of other paver modules to include (don't include the .py 
        extension). By default, the following modules are included:
        defaults, path, release, setuputils, misctasks, options,
        tasks, easy
    """
    filelist = ['__init__', 'defaults', 'path', 'path25', 'release',
                'setuputils', "misctasks", "options", "tasks", "easy"]
    filelist.extend(options.get('extra_files', []))
    output_file = 'paver-minilib-%s.zip' % VERSION

    def generate_zip():
        # Write the mini library to a buffer.
        buf = StringIO()
        destfile = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
        for filename in filelist:
            destfile.writestr(
                "paver/" + (filename + ".py"),
                pkgutil.get_data('paver', filename + ".py"))
        destfile.close()

        # Write the buffer to disk.
        f = open(output_file, "w")
        f.write(buf.getvalue())
        f.close()
    dry("Generate %s" % output_file, generate_zip)
    
@task
def generate_setup():
    """Generates a setup.py file that uses paver behind the scenes. This 
    setup.py file will look in the directory that the user is running it
    in for a paver-minilib.zip and will add that to sys.path if available.
    Otherwise, it will just assume that paver is available."""
    def write_setup():
        setup = open("setup.py", "w")
        setup.write("""try:
    import paver.tasks
except ImportError:
    import os
    if os.path.exists("paver-minilib-%(VERSION)s.zip"):
        import sys
        sys.path.insert(0, "paver-minilib-%(VERSION)s.zip")
    import paver.tasks

paver.tasks.main()
""" % {'VERSION': VERSION})
        setup.close()
        
    dry("Write setup.py", write_setup)
