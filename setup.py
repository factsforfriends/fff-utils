from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='fff-utils',
      version='0.11',
      description='Utilities for FactsForFriends',
      long_description=readme(),
      url='https://github.com/factsforfriends/fff-utils',
      author='Jens Preussner',
      author_email='jens@factsforfriends.de',
      license='MIT',
      packages=['fffutils'],
      entry_points = {
        'console_scripts': ['fff-utils = fffutils.fffutils:main']
      },
      scripts = [],
      install_requires=[
        'boto3',
        'python-slugify',
        'py-trello',
        'urllib3'
      ],
      classifiers = [
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3'
      ],
      zip_safe=False,
      include_package_data=True)