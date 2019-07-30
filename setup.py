from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="easy_postgres",
    version="0.0.2",
    author="Ivo Meixner",
    author_email="natiwastaken@gmail.com",
    description="Lightweight psycopg2 wrapper focused on ease of use",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://github.com/natiiix/easy_postgres",
    keywords="postgresql postgres pgsql psql database psycopg2 easy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database"
    ],
    install_requires=[
        "psycopg2"
    ]
)
