"""Centralized constants for CI task definitions."""

import re
from pathlib import Path

PATHS = 'src/ _CI/tasks/ tests/'
SECURITY_OVERRIDE_ENV = 'GITLAB-MR-CHECK_SECURITY_OVERRIDE'
SECURITY_OVERRIDES_FILE = Path('.security-overrides')

PYSCN_REPORTS_DIR = Path('.pyscn/reports')

IGNORE_PATTERN = re.compile(
    r'(?P<vulnerability_id>[A-Za-z0-9\-_]+)'
    r'(::(?P<expiration_date>\d{4}-\d{2}-\d{2}))?'
)

IMAGE_NAME = 'gitlab-mr-check-deps'
ACT_IMAGE_NAME = 'gitlab-mr-check-act'
QA_WORKFLOW = '.github/workflows/continuous-integration.yaml'

PROJECT_NAME = 'gitlab-mr-check'
OWASP_DTRACK_SETTINGS = ('OWASP_DTRACK_URL', 'OWASP_DTRACK_API_KEY')
UV_PUBLISH_SETTINGS = ('UV_PUBLISH_URL', 'UV_PUBLISH_PASSWORD', 'UV_PUBLISH_USERNAME')

SENTINEL = Path('_CI/.bootstrapped')
