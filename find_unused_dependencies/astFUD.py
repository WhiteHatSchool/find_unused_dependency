import os
import subprocess
import javalang

def find_java_files(root_dir):
    java_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files

def find_unused_imports(formatter_jar, java_files):
    unused_imports = {}

    for java_file in java_files:
        try:
            # Run Google Java Formatter to check for unused imports
            cmd = ["java", "-jar", formatter_jar, "--dry-run", "--aosp", java_file]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)  # Timeout 설정 추가

            # Parse output to find unused imports
            output_lines = result.stdout.splitlines()
            unused_found = False
            current_unused = []

            for line in output_lines:
                if line.startswith("Unnecessary import"):
                    unused_found = True
                    current_unused.append(line.strip().split()[-1])

            if unused_found:
                unused_imports[java_file] = current_unused
                print(f"Unused imports found in {java_file}:")
                for unused in current_unused:
                    print(unused)
                print()

        except subprocess.CalledProcessError as e:
            print(f"Error checking {java_file}: {e}")

        except subprocess.TimeoutExpired as e:
            print(f"Timeout expired while checking {java_file}: {e}")

    return unused_imports

def filter_unused_imports(unused_imports):
    pure_unused_imports = {}

    for java_file, unused_list in unused_imports.items():
        with open(java_file, 'r', encoding='utf-8') as file:
            java_code = file.read()

        tree = javalang.parse.parse(java_code)

        used_imports = set()
        for path, node in tree.filter(javalang.tree.ImportDeclaration):
            used_imports.add(node.path)

        pure_unused_list = []
        for unused_import in unused_list:
            if unused_import not in used_imports:
                pure_unused_list.append(unused_import)

        if pure_unused_list:
            pure_unused_imports[java_file] = pure_unused_list
            print(f"Pure unused imports in {java_file}:")
            for unused in pure_unused_list:
                print(unused)
            print()
        else:
            print(f"No pure unused imports in {java_file}")

    return pure_unused_imports

if __name__ == "__main__":
    formatter_jar = "demonstrate/find_unused_dependencies/google-java-format-1.22.0-all-deps.jar"
    root_dir = "/root/incubator-xtable"

    java_files = find_java_files(root_dir)
    unused_imports = find_unused_imports(formatter_jar, java_files)
    pure_unused_imports = filter_unused_imports(unused_imports)

    print("\nSummary:")
    for java_file, pure_unused_list in pure_unused_imports.items():
        print(f"{java_file}: {len(pure_unused_list)} pure unused import(s) found")
