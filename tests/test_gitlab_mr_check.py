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

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from gitlab_mr_check import mr_is_merged, mr_updated_in_years

if TYPE_CHECKING:
    import gitlab.v4.objects

__author__ = 'gitlab-mr-check <yhoorneman@schubergphilis.com>'
__docformat__ = 'google'
__date__ = '23-04-2026'
__copyright__ = 'Copyright 2026, gitlab-mr-check'
__credits__ = ['gitlab-mr-check']
__license__ = 'Apache-2.0'
__maintainer__ = 'gitlab-mr-check'
__email__ = '<yhoorneman@schubergphilis.com>'
__status__ = 'Development'


def test_sanity() -> None:
    """Sanity check."""
    assert True


def test_mr_is_merged() -> None:
    """mr_is_merged returns True only when state is merged."""
    mr_merged = cast('gitlab.v4.objects.ProjectMergeRequest', SimpleNamespace(state='merged'))
    mr_open = cast('gitlab.v4.objects.ProjectMergeRequest', SimpleNamespace(state='opened'))
    assert mr_is_merged(mr_merged) is True
    assert mr_is_merged(mr_open) is False


def test_mr_updated_in_years() -> None:
    """mr_updated_in_years matches the update year against the allowed list."""
    mr = cast('gitlab.v4.objects.ProjectMergeRequest', SimpleNamespace(updated_at='2024-06-15T10:00:00.000Z'))
    assert mr_updated_in_years(mr, [2024]) is True
    assert mr_updated_in_years(mr, [2023, 2025]) is False
