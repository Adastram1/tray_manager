from setuptools import setup, find_packages
import requests


response = requests.get("https://pypi.org/pypi/tray-manager/json")
new_version = ""

if response.status_code == 200:
    version: str = response.json()['info']['version']
    last_digit = version.split('.')[-1]
    new_version = version.removesuffix(last_digit) + f"{int(last_digit) + 1}"

VERSION = new_version
DESCRITPION = 'An "easier" version of the pystray package'
LONG_DESCRIPTION = 'A package for adding a system tray icon, based on pystray, this package is an "easier" version of pystray to manipulate'

# Setting up
setup(
    name="tray_manager",
    version=VERSION,
    author="Adastram (Github : Adastram1)",
    author_email="",
    description=DESCRITPION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    requires=['pystray',
             'pillow',
             'enum',
             'typing',
             'types'
             ],
    keywords=['python', 'manager', 'system tray', 'pystray'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
