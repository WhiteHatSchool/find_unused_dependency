import requests

def search_maven_repository(groupId, artifactId, version):
    url = f"https://search.maven.org/solrsearch/select?q=g:\"{groupId}\"+AND+a:\"{artifactId}\"+AND+v:\"{version}\"&core=gav&rows=20&wt=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        num_found = data.get('response', {}).get('numFound', 0)
        if num_found > 0:
            docs = data.get('response', {}).get('docs', [])
            for doc in docs:
                print(f"Package: {doc.get('id')}, Latest Version: {doc.get('v')}")
                print(f"   GroupId: {doc.get('g')}, ArtifactId: {doc.get('a')}")
                print(f"   Packaging: {doc.get('p')}, Timestamp: {doc.get('timestamp')}")
                print(f"   Extra Classifiers: {doc.get('ec')}")
                print(f"   Tags: {doc.get('tags')}")
        else:
            print(f"No package found for groupId: {groupId}, artifactId: {artifactId}, version: {version}")
    else:
        print(f"Failed to fetch data from Maven Central. Status code: {response.status_code}")

# 사용 예시: com.fasterxml.jackson.core:jackson-databind:2.13.0 정보 찾기
search_maven_repository("com.fasterxml.jackson.core", "jackson-databind", "2.13.0")
