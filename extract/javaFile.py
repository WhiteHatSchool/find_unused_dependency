from typing import Counter
import os
import re

def extract_imports_from_java_files(directory):
    # 정규 표현식 패턴: import 문을 추출하기 위한 패턴
    import_pattern = re.compile(r'^\s*import\s+([^;]+);')

    # 디렉토리 내의 모든 Java 파일 검색
    java_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))

    # 모든 import 문 추출
    imports = set()  # 중복을 제거하기 위해 set 사용
    for java_file in java_files:
        with open(java_file, 'r', encoding='utf-8') as f:
            for line in f:
                match = import_pattern.match(line)
                if match:
                    import_statement = match.group(1).strip()
                    if import_statement.endswith('.*'):
                        import_statement = import_statement[:-2].strip()
                    if import_statement.startswith('static '):
                        import_statement = import_statement.lstrip("static ")
                    imports.add(import_statement)


    return sorted(imports)

def find_root_package(imports):
    # com으로 시작하는 패키지들만 필터링
    com_imports = [imp for imp in imports if imp.startswith('com.')]

    # 최상위 패키지 부분만 추출하여 빈도 계산
    com_top_level_packages = [imp.split('.')[0:2] for imp in com_imports]
    com_top_level_packages = ['.'.join(pkg) for pkg in com_top_level_packages]
    package_counter = Counter(com_top_level_packages)

    # 가장 많이 사용된 패키지 찾기
    if package_counter:
        root_package, _ = package_counter.most_common(1)[0]
        return root_package
    return None
