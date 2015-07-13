try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='mhef',
    version='1.0.0b6',
    description='Monster Hunter Encryption Functions',
    url='https://github.com/svanheulen/mhef',
    author='Seth VanHeulen',
    author_email='svanheulen@gmail.com',
    license='GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Security :: Cryptography'
    ],
    packages=['mhef'],
    install_requires=['pycrypto']
)

