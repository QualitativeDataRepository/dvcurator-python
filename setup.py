from setuptools import setup

REQUIRES = [
	'pdfrw',
	'requests',
	'typing'
]

setup(
	name='dvcurator',
	packages= ["dvcurator"],
	entry_points = {
		"console_scripts": ['dvcurator = dvcurator.cli:main']
	},
	version='0.1.2',
	author='Michael C. McCall',
	license='MIT',
	include_package_data=True,
	package_data = {'': ['issues/*.md'] }
)
