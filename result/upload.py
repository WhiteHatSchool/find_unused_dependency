import boto3

def upload_to_s3(unused_dependency_path, sbom_path):
    # S3 클라이언트 생성 (EC2 인스턴스의 IAM 역할을 사용)
    s3_client = boto3.client('s3')

    # 업로드할 파일 경로와 S3 버킷 이름 설정
    bucket_name = 'sspringbucket'  # S3 버킷 이름
    unused_dependency_key = 'unused_dependency.json'  # S3에 저장될 파일 키(이름)
    sbom_key = 'sbom.json'  # S3에 저장될 파일 키(이름)

    # S3에 파일 업로드
    try:
        with open(unused_dependency_path, 'rb') as unused_dependency_file:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=unused_dependency_key,
                Body=unused_dependency_file
            )
        print(f"{unused_dependency_key} 파일이 {bucket_name} 버킷에 업로드되었습니다.")
        
        with open(sbom_path, 'rb') as sbom_file:
            s3_client.put_object(
                Bucket=bucket_name,
                Key=sbom_key,
                Body=sbom_file
            )
        print(f"{sbom_key} 파일이 {bucket_name} 버킷에 업로드되었습니다.")
        
    except Exception as e:
        print(f"파일 업로드 중 오류 발생: {e}")