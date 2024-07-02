import shutil
from extract.pom import get_latest_version
import zipfile
import requests
import os

def retry(groupId, artifactId, version, download_dir):
    # Maven Central Repository URL
    base_url = "https://repo.maven.apache.org/maven2/"
    
    # Construct artifact path
    artifact_path = groupId.replace('.', '/') + '/' + artifactId + '/' + version + '/' + artifactId + '-' + version + '.jar'
    
    # Construct full download URL
    download_url = base_url + artifact_path
    
    # Create download directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Filename for saving
    filename = artifactId + '-' + version + '.jar'
    file_path = os.path.join(download_dir, filename)

    # Download the file from URL
    try:
        # Check if the URL exists
        response = requests.head(download_url)
        if response.status_code != 200:
            print(f"URL {download_url} does not exist.\n")
            return

        # Download the file from URL
        print(f"Downloading {artifactId}-{version}.jar...")
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(f"{filename} downloaded successfully to {download_dir}\n")
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {artifactId}-{version}.jar: {e}")

def download_jar(groupId, artifactId, version, download_dir):
    # Maven Central Repository URL
    base_url = "https://repo.maven.apache.org/maven2/"
    
    # Construct artifact path
    artifact_path = groupId.replace('.', '/') + '/' + artifactId + '/' + version + '/' + artifactId + '-' + version + '.jar'
    
    # Construct full download URL
    download_url = base_url + artifact_path
    
    # Create download directory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Filename for saving
    filename = artifactId + '-' + version + '.jar'
    file_path = os.path.join(download_dir, filename)
    
    # Download the file from URL
    try:
        # Check if the URL exists
        response = requests.head(download_url)
        if response.status_code != 200:
            print(f"URL {download_url} does not exist. download latest version.")
            version = get_latest_version(groupId, artifactId)
            if version:
                retry(groupId, artifactId, version, download_dir)
            else:
                print("Latest version is not available.\n")
            return

        # Download the file from URL
        print(f"\nDownloading {artifactId}-{version}.jar...")
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print(f"{filename} downloaded successfully to {download_dir}\n")
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {artifactId}-{version}.jar: {e}")

def extract_class_names(jar_file):
    class_names = []

    try:
        with zipfile.ZipFile(jar_file, 'r') as zf:
            for file_info in zf.infolist():
                if file_info.filename.endswith('.class'):
                    class_file = file_info.filename
                    # Remove .class extension
                    class_name = class_file[:-6].replace('/', '.')
                    # Replace $ with .
                    class_name = class_name.replace('$', '.')
                    class_names.append(class_name)
        
        return class_names
    
    except zipfile.BadZipFile:
        print(f"{jar_file} is not a valid jar file.")
        return []
    except Exception as e:
        print(f"Error extracting class names from {jar_file}: {e}")
        return []

def extract_classes_from_directory(groupId, artifactId, version, directory):
    # jar 파일 다운
    if version:
        download_jar(groupId, artifactId, version, directory)
    else:
        print("version is not available\n")
        return

    all_class_names = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.jar'):
                jar_file_path = os.path.join(root, file)
                class_names = extract_class_names(jar_file_path)
                all_class_names.extend(class_names)
    
    return all_class_names

def delete_jar(jar_dir):
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

def mapping_dependencies(dependency, imports, uimports, directory):
    groupId = dependency['groupId']
    artifactId = dependency['artifactId']
    version = dependency['version']
    
    classes = []
    classes = extract_classes_from_directory(groupId, artifactId, version, directory)
    classes_set = set(classes)

    for imp in imports:
        if imp in classes_set:
            print("[used import]: " + imp)
            return 1
    for imp in uimports:
        if imp in classes_set:
            print("[unused import]: " + imp)
            return -1
    return 0
    