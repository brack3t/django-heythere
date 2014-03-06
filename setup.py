from setuptools import setup

import heythere

setup(
    name="django-heythere",
    version=heythere.__version__,
    description="Convient notifications for users.",
    long_description="",
    keywords="django, notifications",
    author=("Kenneth Love <kenneth@brack3t.com>, "
            "Chris Jones <chris@brack3t.com>"),
    author_email="devs@brack3t.com",
    url="https://github.com/brack3t/django-heythere/",
    license="BSD",
    packages=["heythere"],
    zip_safe=False,
    install_requires=[],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3"
    ],
)
