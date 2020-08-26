import os
import setuptools

basepath = os.path.dirname(__file__)
basepath += '/' if basepath != '' else ''

with open(basepath + "README.md", "r") as fh:
    long_description = fh.read()

with open(basepath + 'requirements.txt', 'r') as fh:
    requirements = fh.readlines()

setuptools.setup(
    name='localhero',
    version='0.1.0',
    packages=setuptools.find_packages(basepath + 'src'),
    package_dir={'': basepath + 'src'},
    classifiers=[
        'Development Status :: 3 - Beta',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    url='https://github.com/smertiens/localhero',
    project_urls={
        'Github': 'https://github.com/smertiens/localhero',
    },
    keywords='server manager developer tools local development',
    license='AGPL-3.0',
    author='Sean Mertiens',
    author_email='sean@atraxi-flow.com',
    description='Manage your local server instances in one place',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    python_requires='>=3.5',

    package_data={
        'localhero': ['config/*', 'style/*', 'fonts/*'],
    },

    entry_points={
        'console_scripts': [
            'localhero=localhero.ui:main',
        ]
    }
)