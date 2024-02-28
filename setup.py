from setuptools import setup, find_packages


VERSION = '0.1.4'
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
    requires=['pystray', 'typing', 'types', 'threading', 'pillow', 'enum'],
    keywords=['python', 'manager', 'system tray', 'pystray'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
