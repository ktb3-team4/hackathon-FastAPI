# FastAPI CI/CD 프로젝트

FastAPI 애플리케이션을 위한 CI/CD 파이프라인이 구성된 프로젝트입니다.

## 🚀 기능

- **자동화된 테스트**: Python 3.9, 3.10, 3.11, 3.12 버전에서 테스트 실행
- **코드 품질 검사**: Black, Flake8, isort, mypy를 통한 린팅 및 포맷팅
- **Docker 빌드**: 자동 Docker 이미지 빌드 및 푸시
- **커버리지 리포트**: Codecov를 통한 테스트 커버리지 추적

## 📋 사전 요구사항

- Python 3.9 이상
- Docker (선택사항)
- GitHub Actions 활성화

## 🛠️ 설정

### 1. GitHub Secrets 설정

Docker Hub에 이미지를 푸시하려면 다음 secrets를 설정하세요:

- `DOCKER_USERNAME`: Docker Hub 사용자명
- `DOCKER_PASSWORD`: Docker Hub 비밀번호

GitHub 저장소 → Settings → Secrets and variables → Actions에서 설정할 수 있습니다.

### 2. 환경 변수 설정

`.env` 파일을 생성하고 필요한 환경 변수를 설정하세요:

```env
ENV=development
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 📦 설치

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 🧪 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 커버리지 포함 테스트
pytest --cov=.

# 특정 테스트 파일 실행
pytest tests/test_main.py
```

## 🐳 Docker 사용

### 빌드

```bash
docker build -t fastapi-app .
```

### 실행

```bash
docker run -p 8000:8000 fastapi-app
```

### Docker Compose 사용

```bash
docker-compose up -d
```

## 🔄 CI/CD 워크플로우

### CI (Continuous Integration)

- `ci.yml`: 모든 푸시 및 PR에 대해 테스트 및 린팅 실행
- `lint.yml`: 코드 품질 검사 전용 워크플로우

### CD (Continuous Deployment)

- `cd.yml`: main 브랜치에 푸시 시 자동 배포 (수동 트리거 가능)

## 📝 코드 품질 도구

- **Black**: 코드 포맷팅
- **Flake8**: 린팅
- **isort**: import 정렬
- **mypy**: 타입 체킹

### 사용법

```bash
# 코드 포맷팅
black .

# 린팅
flake8 .

# import 정렬
isort .

# 타입 체킹
mypy .
```

## 📁 프로젝트 구조

```
.
├── .github
│   └── workflows
│       ├── ci.yml          # CI 파이프라인
│       ├── cd.yml          # CD 파이프라인
│       └── lint.yml        # 린팅 전용
├── tests                   # 테스트 파일
├── Dockerfile              # Docker 이미지 빌드
├── docker-compose.yml      # Docker Compose 설정
├── requirements.txt        # 프로덕션 의존성
├── requirements-dev.txt    # 개발 의존성
├── pytest.ini             # pytest 설정
└── pyproject.toml          # 도구 설정
```

## 🔧 커스터마이징

### 배포 설정 수정

`.github/workflows/cd.yml` 파일에서 배포 스크립트를 수정하세요.

### Docker 이미지 태그 변경

`.github/workflows/ci.yml`의 `docker-build` job에서 이미지 태그를 수정하세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

# hackathon-FastAPI
