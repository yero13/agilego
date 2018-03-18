from distutils.core import setup
from setuptools import find_packages

setup(name='agilego',
      version='0.1.1',
      description='Scrum sprint planner',
      author='Roman Yepifanov',
      url='https://github.com/yero13/agilego.be',
      license='GNU GPL v2.0',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Programming Language :: Python :: 3.6'],
      packages=find_packages(),
      package_data = {'agilego': ['./*.bat', './log/log.txt', './cfg/*.json', './cfg/dependency/*.json', './cfg/jira/*.json', './cfg/log/*.json', './cfg/scrum/*.json', './cfg/validation/*.json']},
      package_dir={'.':'agilego'},
      python_requires= '~=3.6',
      install_requires=['flask', 'flask-cors', 'flask_cache', 'flask_restful', 'networkx', 'na3x']
)
