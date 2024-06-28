import os
import sys
import re
import glob
import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Correctly import the module based on the structure
from find_unused_dependencies.FUD import find_unused_dependencies
from find_unused_dependencies.remove_deadcode import handle_deadcode

def progress_callback(idx, cnt, file, step_name):
    progress_percent = round((idx / cnt) * 100, 2)
    print(f"[{step_name}] {progress_percent}% ({idx} / {cnt}) - {file}...")


def del_dead_code(project_path):
    handle_deadcode(project_path)


def get_unused_import(project_path, formatter_path, callback = progress_callback):
    return find_unused_dependencies(project_path, formatter_path, callback=callback)


def pom_path_lists(pom_path_lists: list):
    group_id = set()
    for file in pom_path_lists:
        tree = ET.parse(file)
        root = tree.getroot()

        xmlns = ''

        m = re.search('{.*}', root.tag)
        if m:
            xmlns = m.group(0)

        tag = root.find(xmlns + 'groupId')
        if tag is not None:
            group_id.add(tag.text)

    return list(group_id)


def remove_elements_containing_substring(lst, substring):
    return [element for element in lst if substring not in element]


def del_local_dependency(unused_imports, project_group_id):
    for group_id in project_group_id:
        unused_imports = remove_elements_containing_substring(unused_imports, group_id)

    return unused_imports

def pom_project_process(project_dir_path: str, formatter_jar_path: str):
    del_dead_code(project_dir_path)
    unused_data = get_unused_import(project_dir_path, formatter_jar_path, callback=progress_callback)
    pom_files = glob.glob(f"{os.path.expanduser(project_dir_path)}/**/pom.xml", recursive=True)
    try:
        project_group_id = pom_path_lists(pom_files)
    except:
        project_group_id = []

    return del_local_dependency(unused_data, project_group_id)