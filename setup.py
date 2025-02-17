from setuptools import setup, find_packages

# Setting up
setup(
    name="tray_manager",
    version="1.0.5",
    url="https://github.com/Adastram1/tray_manager",
    license="GNU Lesser General Public License v3 (LGPLv3)",
    author="Adastram",
    author_email="",
    description='An "easier" version to use of the pystray library (https://github.com/moses-palmer/pystray by Moses Palmér)',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pystray', 'pillow'],
    setup_requires=['setuptools>=42.0.0'],
    keywords=['python', 'manager', 'system tray', 'pystray'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Topic :: Desktop Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3"
    ]
)

