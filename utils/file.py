import os
import shutil

from os import listdir
from os.path import isfile
from os.path import join
from pathlib import Path
from typing import List, Tuple


def get_extension(file_path) -> Tuple[str, str]:
    return os.path.splitext(file_path)


def get_filename(file_path) -> str:
    return os.path.basename(file_path)


def get_files(folder_path: str) -> List[str]:
    """Lists all files in folder_path, folders will be excluded

    Args:
        folder_path (str): path of the folder

    Returns:
        List[str]: list of file paths in the folder
    """
    return [join(folder_path, f) for f in listdir(folder_path) if isfile(join(folder_path, f))]


def get_all(folder_path):
    return [join(folder_path, f) for f in listdir(folder_path)]


def get_parent_folder(folder_path):
    return Path(folder_path).parent


def clear(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)

            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def create_folder(dir, folder_name):
    folder_path = join(dir, folder_name)
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    return folder_path
