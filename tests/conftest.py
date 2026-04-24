#
# Copyright 2026 gitlab-mr-check
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
"""gitlab-mr-check."""

__author__ = 'gitlab-mr-check <yhoorneman@schubergphilis.com>'
__docformat__ = 'google'
__date__ = '23-04-2026'
__copyright__ = 'Copyright 2026, gitlab-mr-check'
__credits__ = ['gitlab-mr-check']
__license__ = 'Apache-2.0'
__maintainer__ = 'gitlab-mr-check'
__email__ = '<yhoorneman@schubergphilis.com>'
__status__ = 'Development'

from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def test_data(project_root: Path) -> Path:  # pylint: disable=redefined-outer-name
    """Return the test data directory, creating it if needed."""
    data_dir = project_root / 'tests' / 'data'
    data_dir.mkdir(exist_ok=True)
    return data_dir
