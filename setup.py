'''setup.py'''

"""
This code should only be executed by developers, not users.

The main purpose of this script is to create the build for pip. It also runs some
automated docs updating.
"""

import os
import sys
from setuptools import setup, find_packages

def pip_version():
    # pip doesn't allow us to use standard version format (20w10a), so we have to
    # comform it to look like Semantic Versioning even though auto-editor does not
    # use that format.
    return '20.33.1.0'


def changes():
    text = '''
    * the default for `--sample_rate` is now the same as the input.
    * the default `--video_codec` is now the same as the video.
    * the `--hardware_accel` option has been removed because it is not used anywhere in the program.
    '''

    text = text.replace('\n', '')
    text = text.replace('    ', '')
    text = text.replace('*', '\n*')
    return text

def numToNormal(text):
    """
    convert semantic versioning to our prefered version format.
    20.10.1.0 -> 20w10a
    """
    import string
    alphabet = list(string.ascii_lowercase)
    nums = text.split('.')
    return nums[0] + 'w' + nums[1] + alphabet[int(nums[2]) - 1]

# Automatically replace outdated docs with correct one.
if(sys.argv[-1] == 'makedocs'):
    vr = numToNormal(pip_version()) # proper version for docs

    lines = open('README.md').read().splitlines()
    newDoc = ''
    for line in lines:
        if(line.startswith('<img src="https://img.shields.io/badge/version-')):
            newDoc += '<img src="https://img.shields.io/badge/version-' + vr + '-blue.svg">\n'
            continue
        if(line.startswith('## New in ')):
            newDoc += '## New in ' + vr + changes() + '\n'
            continue
        if(not line.startswith('* ')):
            newDoc += line + '\n'

    with open('README.md', 'w') as file:
        file.write(newDoc.rstrip('\n'))

    lines = open('resources/CHANGELOG.md').read().splitlines()
    newDoc = ''
    checkNext = False
    for line in lines:
        if(checkNext):
            if(line.startswith('## Version')):
                checkNext = False
                if(not line.startswith(f'## Version {vr}')):
                    newDoc += f'## Version {vr}' + changes() + '\n\n'
        newDoc += line + '\n'
        if(line.startswith('# Auto-Editor Change Log')):
            checkNext = True

    with open('resources/CHANGELOG.md', 'w') as file:
        file.write(newDoc.rstrip('\n'))

    print(f'Done, rewrited docs to {vr}')
    sys.exit()

if(sys.argv[-1] == 'publish'):
    os.system('rm -rf build')
    os.system('rm -rf dist')
    os.system('python3 setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='auto-editor',
    version=pip_version(),
    description='Auto-Editor: Effort free video editing!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/WyattBlue/auto-editor',
    author='WyattBlue',
    author_email='wyattbluesandbox@gmail.com',
    keywords='video editing editor audio processing nonlinear',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'audiotsm2',
        'opencv-python',
        'youtube-dl',
    ],
    classifiers=[
        'Topic :: Multimedia :: Video',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: IronPython',
        'Programming Language :: Python :: Implementation :: Jython',
    ],
    entry_points={
        "console_scripts": ["auto-editor=auto_editor.__main__:main"]
    }
)