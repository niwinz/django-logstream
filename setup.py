from setuptools import setup, find_packages

description="""
Multiprocess log collector for python/django-logging
"""

long_description = """
* **Documentation**: http://readthedocs.org/docs/django-logstream/en/latest/
"""


setup(
    name="django-logstream",
    version=':versiontools:django_logstream:',
    url='https://github.com/niwibe/django-logstream',
    license='BSD',
    platforms=['OS Independent'],
    description = description.strip(),
    long_description = long_description.strip(),
    author = 'Andrei Antoukh',
    author_email = 'niwi@niwi.be',
    maintainer = 'Andrei Antoukh',
    maintainer_email = 'niwi@niwi.be',
    packages = find_packages(),
    include_package_data = True,
    install_requires=[
        'distribute',
        'pyzmq>=2.1.10',
        'pycrypto>=2.4.1',
    ],
    setup_requires = [
        'versiontools >= 1.8',
    ],
    zip_safe = False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
