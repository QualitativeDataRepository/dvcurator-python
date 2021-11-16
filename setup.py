from setuptools import setup, find_packages

REQUIRES = [
	'pdfrw',
	'requests',
	'typing'
]

setup(
	name='dvcurator',
	packages=find_packages(),
	version='0.1.0',
	author='Michael McCall',
	license='MIT',
	include_package_data=True,
	package_data = {'': ['*.md'] }
)
