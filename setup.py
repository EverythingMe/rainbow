from setuptools import setup, find_packages

setup(
    name='rainbow-cfn',
    version='0.4',
    description='Rainbow is Amazon Cloudformation on steroids',
    author='EverythingMe',
    author_email='omrib@everything.me',
    url='http://github.com/EverythingMe/rainbow',
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=['nose', 'coverage', 'mock'],
    install_requires=['boto>=2', 'PyYAML>=3'],
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

