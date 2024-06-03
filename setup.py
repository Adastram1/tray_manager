from setuptools import setup, find_packages

# Setting up
setup(
    name="tray_manager",
    version="1.0.0",
    url="https://github.com/Adastram1/tray_manager",
    license="GNU Lesser General Public License v3 (LGPLv3)",

    author="Adastram",
    author_email="",
    
    description='An "easier" version to use of the pystray librairy (https://github.com/moses-palmer/pystray by Moses Palmér)',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",

    packages=find_packages(),
    include_package_data=True,
    requires=['pystray', 'pillow', 'enum', 'typing', 'types', 'threading'],

    keywords=['python', 'manager', 'system tray', 'pystray'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"
    ]
)
