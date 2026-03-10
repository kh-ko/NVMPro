import os
import sys

# Qt 리소스 시스템 베이스 경로 (qrc 파일에 설정된 prefix/폴더 구조에 맞춤)
# OS에 상관없이 무조건 슬래시(/)를 사용합니다.
ASSET_BASE = ":/a_assets"

# 하위 폴더 경로
CONFIG_DIR = f"{ASSET_BASE}/config"
IMAGE_DIR = f"{ASSET_BASE}/images"
UI_DIR = f"{ASSET_BASE}/ui"
SCHEMA_DIR = f"{ASSET_BASE}/schema"

# 주요 파일 경로
TAG_SCHEMA_FILE = f"{SCHEMA_DIR}/base/tag_scheme.json"
APP_ICON_FILE = f"{IMAGE_DIR}/app_icon.png"

if getattr(sys, 'frozen', False):
    # exe 파일로 실행될 때의 디렉토리
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    # 파이썬 스크립트로 실행될 때의 최상위 디렉토리
    # (주의: 현재 이 경로 관리 파일이 최상단 폴더에 있다고 가정합니다. 
    # 만약 a_global 같은 하위 폴더에 있다면 os.path.join(..., "..", "..") 등으로 루트를 맞춰주세요)
    ROOT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))
    # ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) # 하위 폴더일 경우 예시

# 로컬 베이스 폴더
LOCAL_RESOURCE_DIR = os.path.join(ROOT_DIR, "2_resource")
LOCAL_CONFIG_DIR = os.path.join(LOCAL_RESOURCE_DIR, "config")

# 주요 로컬 파일 경로 모음
CONNECTIONS_JSON_FILE = os.path.join(LOCAL_CONFIG_DIR, "connections.json")