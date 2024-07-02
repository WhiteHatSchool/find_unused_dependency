from xml.etree import ElementTree as ET
import requests
import os


#############################
def xml_to_dict(element, xmlns=""):
    node = {}
    if element.attrib:
        node.update(('@' + k, v) for k, v in element.attrib.items())
    
    children = list(element)
    if children:
        dd = {}
        for dc in map(lambda e: xml_to_dict(e, xmlns), children):
            for k, v in dc.items():
                if k in dd:
                    if not isinstance(dd[k], list):
                        dd[k] = [dd[k]]
                    dd[k].append(v)
                else:
                    dd[k] = v
        node.update(dd)
    
    if element.text and element.text.strip():
        if node:
            node[element.tag.replace(xmlns, "")] = element.text.strip()
        else:
            node = element.text.strip()

    return {element.tag.replace(xmlns, ""): node}
#############################

## 네임스페이스 찾기
def find_pom_namespace(pom_file):
    try:
        tree = ET.parse(pom_file)
        root = tree.getroot()

        # Extract the default namespace URI from the root element
        namespace = root.tag.split('}')[0][1:]
        return namespace
    except Exception as e:
        print(f"Error occurred while parsing {pom_file}: {e}")
        return None

## 최신 버전 찾기
def get_latest_version(groupId, artifactId):
    url = f"https://search.maven.org/solrsearch/select?q=g:{groupId}%20AND%20a:{artifactId}&start=0&rows=1"
    response = requests.get(url)
        
    if response.status_code == 200:
        data = response.json()
        num_found = data.get('response', {}).get('numFound', 0)
        if num_found > 0:
            latest_version = data.get('response', {}).get('docs', [])[0].get('latestVersion', '')
            if latest_version:
                return latest_version
    else:
        print(f"Maven Central에서 데이터를 가져오는 데 실패했습니다.\n{groupId}.{artifactId} 상태 코드: {response.status_code}\n")

## Properties 추출하기
def extract_properties(pom_file, ns):
    tree = ET.parse(pom_file)
    root = tree.getroot()

    properties = {}

    for prop in root.findall('.//m:properties/*', ns):
        properties[prop.tag.split('}')[1]] = prop.text

    return properties

## 버전 추출하기
def resolve_version(version, properties):
    if version and version.startswith('${') and version.endswith('}'):
        prop_key = version[2:-1]
        return properties.get(prop_key, False)
    return version if version else False

## 의존성 추출하기
def extract_dependencies(pom_file):
    tree = ET.parse(pom_file)
    root = tree.getroot()

    # 네임스페이스
    ns = {'m': find_pom_namespace(pom_file)}

    # properties
    properties = extract_properties(pom_file, ns)


    # parents
    isParent = root.find('m:parent', ns)
    if isParent:
        parent_info = {
            'groupId': root.find('.//m:parent/m:groupId', ns).text,
            'artifactId': root.find('.//m:parent/m:artifactId', ns).text,
            'version': root.find('.//m:parent/m:version', ns).text
        }

        prefix = parent_info['artifactId'].split('-')[0]
    
    # dependencies
    dependencies = []

    for dependency in root.findall('.//m:dependency', ns):
        group_id = dependency.find('m:groupId', ns).text if dependency.find('m:groupId', ns) is not None else ''
        artifact_id = dependency.find('m:artifactId', ns).text if dependency.find('m:artifactId', ns) is not None else ''
        version = dependency.find('m:version', ns).text if dependency.find('m:version', ns) is not None else 'LATEST'

        if group_id == '' or artifact_id == '': continue

        if isParent:
            if group_id == parent_info['groupId'] and artifact_id.startswith(prefix):
                resolved_version = parent_info['version']
            else :
                resolved = resolve_version(version, properties) if version != 'LATEST' else get_latest_version(group_id, artifact_id)
                resolved_version = get_latest_version(group_id, artifact_id) if resolved == False else resolved
        else :
            resolved = resolve_version(version, properties) if version != 'LATEST' else get_latest_version(group_id, artifact_id)
            resolved_version = get_latest_version(group_id, artifact_id) if resolved == False else resolved

        dependency_info = {
            'groupId': group_id,
            'artifactId': artifact_id,
            'version': resolved_version
        }
        dependencies.append(dependency_info)

    # plugins
    plugins = []

    for plugin in root.findall('.//m:plugin', ns):
        group_id = plugin.find('m:groupId', ns).text if plugin.find('m:groupId', ns) is not None else ''
        artifact_id = plugin.find('m:artifactId', ns).text if plugin.find('m:artifactId', ns) is not None else ''
        version = plugin.find('m:version', ns).text if plugin.find('m:version', ns) is not None else 'LATEST'

        if group_id == '' or artifact_id == '': continue

        if isParent:
            if group_id == parent_info['groupId'] and artifact_id.startswith(prefix):
                resolved_version = parent_info['version']
            else :
                resolved = resolve_version(version, properties) if version != 'LATEST' else get_latest_version(group_id, artifact_id)
                resolved_version = get_latest_version(group_id, artifact_id) if resolved == False else resolved
        else :
            resolved = resolve_version(version, properties) if version != 'LATEST' else get_latest_version(group_id, artifact_id)
            resolved_version = get_latest_version(group_id, artifact_id) if resolved == False else resolved

        plugin_info = {
            'groupId': group_id,
            'artifactId': artifact_id,
            'version': resolved_version
        }
        plugins.append(plugin_info)

    combined = []
    combined.extend(dependencies)
    combined.extend(plugins)

    return combined

# 모든 pom.xml 추출
def extract_from_all_poms(directory):
    all_dependencies = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file == "pom.xml":
                pom_file_path = os.path.join(root, file)
                print(f"\nProcessing {pom_file_path}...")
                dependencies = extract_dependencies(pom_file_path)
                all_dependencies.extend(dependencies)
    
    # 중복 제거 및 정렬
    seen = set()
    unique_dependencies = []
    for dep in all_dependencies:
        key = (dep['groupId'], dep['artifactId'], dep['version'])
        if key not in seen:
            seen.add(key)
            unique_dependencies.append(dep)

    # None 값을 필터링하고 정렬
    sorted_dependencies = sorted(unique_dependencies, key=lambda x: (
        x['groupId'] if x['groupId'] else '',
        x['artifactId'] if x['artifactId'] else '',
        x['version'] if x['version'] else ''
    ))

    return sorted_dependencies
