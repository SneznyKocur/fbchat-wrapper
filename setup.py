from setuptools import setup, find_packages
import os
VERSION = '0.0.10'
DESCRIPTION = 'Wrapper for fbchat'
LONG_DESCRIPTION = 'Simple Wrapper Package to make Programming with fbchat easier and simpler to read.'

# Setting up
setup(
    name="fbchat_wrapper",
    version=VERSION,
    author="SneznyKocur",
    author_email="kocursnezny@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["py-fbchat","validators","pillow","ffmpeg-python","wget","pytube"],
    keywords=['python', 'messaging', 'wrapper'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)