import os
import sys

##########################
# SoC Builder Utils File #
##########################

def get_resource_path(relative_path, caller_file=None):
    """ Get the absolute path to the resource, works for development and PyInstaller.
    
    Parameters:
    - relative_path: str, path to the resource relative to the caller.
    - caller_file: str, optional, path to the calling file to base the resource path on.
    """
    if caller_file is None:
        # Use the current file's location if no caller_file is provided
        caller_file = os.path.abspath(__file__)
    
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(caller_file))
    return os.path.join(base_path, relative_path)

def is_running_as_executable():
    """Check if the application is running as a bundled executable."""
    return getattr(sys, 'frozen', False)

