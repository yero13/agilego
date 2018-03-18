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
      packages=find_packages(),
      package_data = {'agilego': ['./log/log.txt', './cfg/*.json', './cfg/log/*.json', './cfg/jira/*.json', './cfg/scrum/*.json', '.LICENSE', './README.rst']},
      package_dir={'.':'agilego'},
      python_requires= '~=3.6',
      install_requires=['flask', 'flask-cors', 'flask_cache', 'flask_restful', 'networkx', 'na3x']
)
