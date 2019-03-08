from setuptools import setup


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(name='liberty-parser',
      version='0.0.3',
      description='Liberty format parser.',
      long_description=readme(),
      long_description_content_type="text/markdown",
      keywords='liberty',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Topic :: Scientific/Engineering',
          'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
          'Programming Language :: Python :: 3'
      ],
      url='https://codeberg.org/tok/liberty-parser',
      author='T. Kramer',
      author_email='dont@spam.me',
      license='GPLv3',
      install_requires=[
          'numpy',
          'lark-parser'
      ],
      zip_safe=False)
