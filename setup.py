import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="resourcemanager",
    version="0.0.2",
    author="Brandon M. Pace",
    author_email="brandonmpace@gmail.com",
    description="A resource manager for Python programs",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    keywords="resource file update manager",
    license="GNU Lesser General Public License v3 or later",
    platforms=['any'],
    python_requires=">=3.6.5",
    url="https://github.com/brandonmpace/resourcemanager",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
    ]
)
