import os
import subprocess

from app_utils import max_file_size


# Returns False if viruses are detected on the path or results could not be determined
def scan_path(path):
    args = ['clamscan', f'--max-filesize={max_file_size / 1024 / 1024}m', f'{os.path.abspath(path)}']
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.returncode != 0:
        return False

    return True


def update_signatures():
    args = ['freshclam']
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
