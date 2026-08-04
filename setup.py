from setuptools import setup

# Runtime dependencies only. requirements.txt also carries the tooling needed
# to build the release binaries.
# pywin32 supplies pythoncom, which convert.py needs in order to drive Word
REQUIRES = [
	'requests',
	'pikepdf',
	'docx2pdf',
	'pywin32; sys_platform == "win32"'
]

setup(
	name='dvcurator',
	packages= ["dvcurator"],
	install_requires=REQUIRES,
	entry_points = {
		"console_scripts": ['dvcurator = dvcurator.gui:main']
	},
	version='0.1.2',
	author='Michael C. McCall',
	license='MIT',
	include_package_data=True,
	package_data = {'dvcurator': ['assets/*'] }
)
