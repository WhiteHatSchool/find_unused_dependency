from find_unused_dependencies.dependency_analyzer import pom_project_process
from extract.javaFile import extract_imports_from_java_files, find_root_package
from extract.jar import mapping_dependencies
from extract.pom import extract_from_all_poms
import subprocess
import argparse
import shutil
import os

if __name__ == "__main__":
    # Argument 추가
    parser = argparse.ArgumentParser(description='Download Jar and Find Package')
    parser.add_argument('-p', '--project', dest="project" , action="store", type=str, default=None, help="프로젝트 경로")
    args = parser.parse_args()
    project_dir = args.project
    formatter_dir = './find_unused_dependencies/google-java-format-1.22.0-all-deps.jar'
    jar_dir = './jar'

    ## Unused Imports 추출
    unused_imports = pom_project_process(project_dir, formatter_dir)
    with open('unused_imports.txt', 'w') as import_file:
        for imp in unused_imports:
            import_file.write(f"{imp}\n")

    # Imports 추출
    unsorted_imports = extract_imports_from_java_files(project_dir)
    root_package = find_root_package(unsorted_imports)
    root_package_lower = root_package.lower()
    imports = [imp for imp in unsorted_imports if not imp.startswith(root_package_lower)]
    imports = [imp for imp in imports if not (root_package and imp.startswith(root_package)) and not imp.startswith('java.')]
    imports = [imp for imp in imports if not imp.startswith('net.sf.json.') and not imp.startswith('javax.')]
    with open('imports.txt', 'w') as import_file:
        for imp in imports:
            import_file.write(f"{imp}\n")

    ## Dependencies 추출
    dependencies = extract_from_all_poms(project_dir, root_package)
    with open('dependecies.txt', 'w') as import_file:
        for dependency in dependencies:
            import_file.write(f"{dependency}\n")

    # Import와 패키지 매핑
    used_dependencies = []
    unused_dependencies = []
    for dependency in dependencies:
        if mapping_dependencies(dependency, imports, unused_imports, jar_dir) == True:
            used_dependencies.append(dependency)
        else:
            unused_dependencies.append(dependency)
    
    # 의존성 사용 여부 결과 출력
    with open('used_dependency.txt', 'w') as import_file:
        for dependency in used_dependencies:
            import_file.write(f"{dependency['groupId']}:{dependency['artifactId']}:{dependency['version']}\n")

    with open('unused_dependency.txt', 'w') as import_file:
        for dependency in unused_dependencies:
            import_file.write(f"{dependency['groupId']}:{dependency['artifactId']}:{dependency['version']}\n")



    # Jar 삭제
    if os.path.exists(jar_dir) and os.path.isdir(jar_dir):
        for filename in os.listdir(jar_dir):
            file_path = os.path.join(jar_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    
    # Repository 변경사항 삭제
    command = 'cd ' + project_dir + '&& git reset --hard HEAD && git clean -fd'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return Code:", result.returncode)
