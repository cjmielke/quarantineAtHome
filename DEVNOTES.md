### Windows development

#### environment setup (how Cosmo does it at least)

* On a windows computer, install pycharm community
* When it starts, click "get from version control" and clone this git repository
	* if git for windows isn't installed, [get it here](https://www.jetbrains.com/help/pycharm/using-git-integration.html#)
* install python for windows : https://www.python.org/downloads/release/python-2717/
	* add a virtualenv
		* pip install pyinstaller
		* pip install numpy==1.8
			* this requires a download of visual C runtime - pip will provide a download link
			* worked on win10, but so far not straightforward on win8 https://github.com/numpy/numpy/issues/9783
			* after might fighting, used a normal CMD terminal and used pip at c:\Python27\scripts\pip.exe to install numpy
				* running this system-level pip prompts a window which forces a .NET install ....
				* finally appears to be building! Consider skipping the Visual Studio install above



