from setuptools import setup


with open('README.rst') as f:
    readme = f.read()


setup(
     name="pytest-interactive",
     version='0.1.3',
     description='A pytest plugin for console based interactive test selection'
                 ' just after the collection phase',
     long_description=readme,
     license='MIT',
     author='Tyler Goodlet',
     author_email='tgoodlet@gmail.com',
     url='https://github.com/tgoodlet/pytest-interactive',
     download_url='https://github.com/tgoodlet/pytest-interactive/tarball/0.1',
     platforms=['linux'],
     packages=['interactive'],
     entry_points={'pytest11': [
         'interactive = interactive.plugin'
     ]},
     zip_safe=False,
     install_requires=['pytest>=2.4.2', 'ipython>=5.0'],
     classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
     ],
)
