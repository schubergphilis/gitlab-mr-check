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

from .gitlab_mr_check import (
    MRApprovalResult,
    ProjectMRAuditResult,
    audit,
    evaluate_mrs_4eyes_per_project,
    filter_empty_results_by_field,
    get_groups_recursive,
    get_mrs_by_project,
    get_mrs_by_projects,
    has_4eyes_approval,
    mr_is_merged,
    mr_updated_in_years,
    sort_results_by_field,
)
from .helpers.config import (
    Config,
    GitlabAuditConfig,
    GitlabConfig,
    GitlabGroupConfig,
    LoggingConfig,
    parse_config_file,
)

__all__ = [
    'Config',
    'GitlabAuditConfig',
    'GitlabConfig',
    'GitlabGroupConfig',
    'LoggingConfig',
    'MRApprovalResult',
    'ProjectMRAuditResult',
    'audit',
    'evaluate_mrs_4eyes_per_project',
    'filter_empty_results_by_field',
    'get_groups_recursive',
    'get_mrs_by_project',
    'get_mrs_by_projects',
    'has_4eyes_approval',
    'mr_is_merged',
    'mr_updated_in_years',
    'parse_config_file',
    'sort_results_by_field',
]
