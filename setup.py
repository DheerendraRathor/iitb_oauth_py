"""
Python implementation of IIT OAuth
"""
from setuptools import setup


dependencies = ['django>1.8', 'requests']

setup(
    name='iitb_oauth',
    version='0.0.6',
    url='https://github.com/DheerendraRathor/iitb_oauth_py',
    packages=['oauth'],
    include_package_data=True,
    license='BSD',
    author='Dheerendra Rathor',
    author_email='dheeru.rathor14@gmail.com',
    description='Python implementation of IIT OAuth',
    long_description=__doc__,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)