from find_unused_dependencies.dependency_analyzer import pom_project_process
from extract.javaFile import extract_imports_from_java_files
from extract.jar import mapping_dependencies, delete_jar
from extract.pom import extract_from_all_poms
import argparse

if __name__ == "__main__":
    # Argument 추가
    parser = argparse.ArgumentParser(description='Download Jar and Find Package')
    parser.add_argument('-p', '--project', dest="project" , action="store", type=str, default=None, help="프로젝트 경로")
    args = parser.parse_args()
    project_dir = args.project
    formatter_dir = './find_unused_dependencies/google-java-format-1.22.0-all-deps.jar'
    jar_dir = './jar'

    ## Unused Imports 추출
    unused_imports = set(pom_project_process(project_dir, formatter_dir))
    with open('unused_imports.txt', 'w') as import_file:
        for imp in unused_imports:
            import_file.write(f"{imp}\n")

    # Imports 추출
    unsorted_imports = set(extract_imports_from_java_files(project_dir))
    imports = unsorted_imports - unused_imports
    with open('imports.txt', 'w') as import_file:
        for imp in imports:
            import_file.write(f"{imp}\n")

    ## Dependencies 추출
    dependencies = extract_from_all_poms(project_dir)
    with open('dependecies.txt', 'w') as import_file:
        for dependency in dependencies:
            import_file.write(f"{dependency}\n")

    # Import와 패키지 매핑
    used_dependencies = []
    unused_dependencies = []
    for dependency in dependencies:
        val = mapping_dependencies(dependency, imports, unused_imports, jar_dir)
        if val == 1:
            used_dependencies.append(dependency)
        elif val == -1:
            unused_dependencies.append(dependency)
    
    # 의존성 사용 여부 결과 출력
    with open('used_dependency.txt', 'w') as import_file:
        for dependency in used_dependencies:
            import_file.write(f"{dependency['groupId']}:{dependency['artifactId']}:{dependency['version']}\n")

    with open('unused_dependency.txt', 'w') as import_file:
        for dependency in unused_dependencies:
            import_file.write(f"{dependency['groupId']}:{dependency['artifactId']}:{dependency['version']}\n")
    
    # Git Repository 변경사항 삭제
    # command = 'cd ' + project_dir + '&& git reset --hard HEAD && git clean -fd'
    # result = subprocess.run(command, capture_output=True, text=True, shell=True)
    # print("STDOUT:", result.stdout)
    # print("STDERR:", result.stderr)
    # print("Return Code:", result.returncode)
