from distutils.core import setup
from setuptools import find_packages

setup(name='agilego',
      version='0.1',
      description='Scrum sprint planner',
      author='Roman Yepifanov',
      url='https://github.com/yero13/',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Programming Language :: Python :: 3.6'],
      #py_modules=['import', 'transform', 'api', 'export'],
      packages=find_packages(),
      package_dir={'.':'agilego'},
      python_requires= '~=3.6',
      install_requires=['pandas', 'jsonschema', 'requests', 'pymongo', 'flask', 'flask-cors', 'flask_cache']
      )