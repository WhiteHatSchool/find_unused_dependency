from find_unused_dependencies.dependency_analyzer import pom_project_process
from extract.javaFile import extract_imports_from_java_files
from extract.pom import extract_from_all_poms
from extract.jar import mapping_dependencies
from result.upload import upload_to_s3
from sbom.create import create_sbom
import subprocess
import argparse
import shutil
import json
import os

def delete(dir):
    if os.path.exists(dir) and os.path.isdir(dir):
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

if __name__ == "__main__":
    # Argument 추가
    parser = argparse.ArgumentParser(description='Download Jar and Find Package')
    parser.add_argument('-p', '--project', dest="project" , action="store", type=str, default=None, help="프로젝트 경로")
    args = parser.parse_args()
    formatter_dir = './find_unused_dependencies/google-java-format-1.22.0-all-deps.jar'
    unused_dir = './result/unused_dependency.json'
    sbom_dir = './result/sbom.json'
    project_dir = args.project
    jar_dir = './jar'
    pom_dir = './pom'

    # SBOM 생성
    create_sbom(project_dir, sbom_dir)

    ## Unused Imports 추출
    unused_imports = set(pom_project_process(project_dir, formatter_dir))
    with open('./debug/unused_imports.txt', 'w') as import_file:
        for imp in unused_imports:
            import_file.write(f"{imp}\n")

    # Imports 추출
    unsorted_imports = set(extract_imports_from_java_files(project_dir))
    imports = unsorted_imports - unused_imports
    with open('./debug/imports.txt', 'w') as import_file:
        for imp in imports:
            import_file.write(f"{imp}\n")

    ## Dependencies 추출
    dependencies = extract_from_all_poms(project_dir)
    with open('./debug/dependecies.txt', 'w') as import_file:
        for dependency in dependencies:
            import_file.write(f"{dependency}\n")
    original_dependencies = []
    original_dependencies.extend(dependencies)

    # Import와 패키지 매핑
    used_dependencies = []
    unused_dependencies = []
    for dependency in dependencies:
        val = mapping_dependencies(dependency, imports, unused_imports, jar_dir)
        if val == 1:
            used_dependencies.append(dependency)
        elif val == -1:
            unused_dependencies.append(dependency)
        delete(jar_dir)
    delete(pom_dir)
    
    # 의존성 사용 여부 결과 출력
    with open('./debug/used_dependency.txt', 'w') as import_file:
        for dependency in used_dependencies:
            import_file.write(f"{dependency['groupId']}:{dependency['artifactId']}:{dependency['version']}\n")

    with open('./debug/unused_dependency.txt', 'w') as import_file:
        for dependency in unused_dependencies:
            import_file.write(f"{dependency['groupId']}:{dependency['artifactId']}:{dependency['version']}\n")
    
    with open('./result/unused_dependency.json', 'w') as import_file:
        json.dump(unused_dependencies, import_file, indent=4)
    upload_to_s3(unused_dir, sbom_dir)

    # Git Repository 변경사항 삭제 (필요한 경우에 주석 해제)
    command = 'cd ' + project_dir + '&& git reset --hard HEAD && git clean -fd'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return Code:", result.returncode)

