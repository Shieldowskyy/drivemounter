from setuptools import setup, find_packages

setup(
    name="drivemounter",
    version="1.0.0",
    description="1:1 Windows Map Network Drive clone for KDE Plasma (SMB, NFS, WebDAV)",
    author="Krzysztof (Shieldziak) Tarczyński",
    author_email="32707076+Shieldowskyy@users.noreply.github.com",
    url="https://github.com/Shieldowskyy/drivemounter",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.9",
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Topic :: Desktop Environment :: K Desktop Environment (KDE)",
        "Topic :: System :: Networking",
    ],
)
