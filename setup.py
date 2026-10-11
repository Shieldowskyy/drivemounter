from setuptools import setup, find_packages

setup(
    name="drivemounter",
    version="1.0.0",
    description="Klon 1:1 kreatora mapowania dysków Windows dla KDE Plasma (SMB, NFS, WebDAV)",
    author="Antigravity",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.5.0",
    ],
    entry_points={
        "console_scripts": [
            "drivemounter=drivemounter.app:main",
        ],
    },
    classifiers=[
        "Environment :: X11 Applications :: Qt",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Desktop Environment :: K Desktop Environment (KDE)",
        "Topic :: System :: Networking",
    ],
)
