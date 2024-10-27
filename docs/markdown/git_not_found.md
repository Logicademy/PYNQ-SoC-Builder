## "Could not auto-update project"

This message appears when the PYNQ SoC Builder could not find a valid Git repository in the current working directory. This can happen for two primary reasons:

 - User downloaded project using "Download ZIP" option - Whilst this is OK and you could ignore this message, you will not be prompt if the project receives updates! The PYNQ SoC Builder project is a work in progress and changing every day. It is recommended to use Git so that the application can automatically check and install updates for you :D
 - Project is not being executed from ./PYNQ-SoC-Builder/ directory using ```python main.py```. Launching the SoC Builder from another directory such as ```python repo\PYNQ-SoC-Builder\main.py``` will cause issues unfortunately.

If you are seeing this error for another reason, please [open an issue on GitHub](https://github.com/Logicademy/PYNQ-SoC-Builder/issues) or even better, email me here [lcanny8@gmail.com](mailto:lcanny8@gmail.com).

Thanks
