import json
import os
from setuptools import setup
from pathlib import Path

here = Path(os.path.dirname(os.path.abspath(__file__)))

def readme():
    with open(here / "README.md", "rt") as f:
        return f.read()

with open('package.json') as f:
    package = json.load(f)

package_name = package["name"].replace(" ", "_").replace("-", "_")

setup(
    name=package_name,
    version=package["version"],
    author=package['author'],
    packages=[package_name],
    url="https://github.com/BSd3v/dash-chart-editor",
    project_urls={"Github": "https://github.com/BSd3v/dash-chart-editor"},
    include_package_data=True,
    license=package['license'],
    description=package.get('description', package_name),
    long_description=readme(),
    long_description_content_type="text/markdown",
    install_requires=[],
    classifiers = [
        'Framework :: Dash',
    ],    
)
