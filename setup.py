from setuptools import setup

setup(
     name="pytest-interactive",
     version='0.1',
     description='pytest plugin for console based interactive test selection'
                 ' just after the collection phase',
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
     install_requires=['pytest>=2.4.2', 'ipython<5.0'],
     classifiers=[
         'Development Status :: 3 - Alpha',
         'Intended Audience :: Developers',
         'License :: OSI Approved :: MIT License',
         'Operating System :: POSIX',
         'Operating System :: Microsoft :: Windows',
         'Operating System :: MacOS :: MacOS X',
         'Topic :: Software Development :: Testing',
         'Topic :: Software Development :: Quality Assurance',
         'Topic :: Utilities',
         'Programming Language :: Python',
         'Programming Language :: Python :: 3',
     ],
)
