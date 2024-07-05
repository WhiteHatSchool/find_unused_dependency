import os
import subprocess
import sys

def create_and_install_venv():
    # 가상 환경 디렉토리 이름
    venv_dir = 'myenv'

    # 가상 환경 생성
    subprocess.run([sys.executable, '-m', 'venv', venv_dir])

    # 가상 환경의 pip 실행 경로
    pip_executable = os.path.join(venv_dir, 'bin', 'pip') if os.name != 'nt' else os.path.join(venv_dir, 'Scripts', 'pip')

    # 필요한 패키지 설치
    packages = ['boto3', 'chardet', 'requests']
    subprocess.run([pip_executable, 'install'] + packages)

    print(f"가상 환경 '{venv_dir}'이 생성되고 필요한 패키지들이 설치되었습니다.")

if __name__ == '__main__':
    create_and_install_venv()
