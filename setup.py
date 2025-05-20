from setuptools import setup, find_packages

setup(
    name="web-ui",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "gradio==5.27.0",
        "python-dotenv",
    ],
) 