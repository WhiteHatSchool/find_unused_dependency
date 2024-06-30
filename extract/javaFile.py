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
