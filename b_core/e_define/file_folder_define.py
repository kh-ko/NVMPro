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