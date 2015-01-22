from setuptools import setup, find_packages

setup(
    name='rainbow-cfn',
    version='1.0',
    description='Rainbow is AWS Cloudformation on steroids',
    author='EverythingMe',
    author_email='omrib@everything.me',
    url='http://github.com/EverythingMe/rainbow',
    packages=find_packages(),
    install_requires=['boto', 'PyYAML'],

    extras_require={
        'test': ['nose', 'coverage', 'mock']
    },

    entry_points={
        'console_scripts': [
            'rainbow = rainbow.main:main'
        ]
    },

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Clustering',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ]
)

