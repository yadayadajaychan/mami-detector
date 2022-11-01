from setuptools import find_packages, setup

setup(
    name='mami-detector',
    version=0.0,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'opencv-python',
        'pyzmq',
        'tensorflow',
        'keras',
    ],
)
