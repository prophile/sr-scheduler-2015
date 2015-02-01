sys.path.insert(0, os.path.abspath('..'))

# Sphinx configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinxarg.ext'
]

source_suffix = '.rst'
master_doc = 'index'

project = 'Student Robotics match scheduler'
copyright = '2015, Student Robotics'

from sr.comp.scheduler.metadata import VERSION as version
release = version

html_theme = 'default'

