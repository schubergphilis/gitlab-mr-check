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

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from functools import partial
from typing import Any

import gitlab
import gitlab.v4.objects

from gitlab_mr_check.helpers.config import Config

__author__ = 'gitlab-mr-check <yhoorneman@schubergphilis.com>'
__docformat__ = 'google'
__date__ = '23-04-2026'
__copyright__ = 'Copyright 2026, gitlab-mr-check'
__credits__ = ['gitlab-mr-check']
__license__ = 'Apache-2.0'
__maintainer__ = 'gitlab-mr-check'
__email__ = '<yhoorneman@schubergphilis.com>'
__status__ = 'Development'

LOGGER_BASENAME = 'gitlab-mr-check'
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


@dataclass
class MRApprovalResult:
    """Result of a 4-eyes approval check for a single merge request."""

    iid: int
    passed: bool
    reasoning: str
    title: str = ''
    web_url: str = ''
    state: str = ''
    created_at: str = ''
    updated_at: str = ''


@dataclass
class ProjectMRAuditResult:
    """Aggregated audit result for all merge requests in a project."""

    name: str
    mr_results: list[MRApprovalResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Return True if all MRs in this project passed the 4-eyes check."""
        return all(mr.passed for mr in self.mr_results) if self.mr_results else True

    @property
    def mrs_passed(self) -> list[MRApprovalResult]:
        """Return the list of MRs that passed."""
        return [mr for mr in self.mr_results if mr.passed]

    @property
    def mrs_failed(self) -> list[MRApprovalResult]:
        """Return the list of MRs that failed."""
        return [mr for mr in self.mr_results if not mr.passed]

    @property
    def percentage(self) -> float:
        """Return the pass percentage across all MRs."""
        total = len(self.mr_results)
        return (len(self.mrs_passed) / total * 100) if total else 0

    @property
    def summary(self) -> str:
        """Return a human-readable summary line."""
        return f'Passed: {len(self.mrs_passed)}, Failed: {len(self.mrs_failed)}, Percentage: {self.percentage:.2f}%'

    def to_dict(self) -> dict:
        """Serialise this result including all computed properties."""
        result = asdict(self)
        for attr in dir(self):
            if not attr.startswith('_') and attr not in result:
                value = getattr(self, attr)
                if not callable(value):
                    result[attr] = value
        return result


def get_groups_recursive(gl: gitlab.Gitlab, group_id_or_name: str | int) -> list[Any]:
    """Recursively collect a group and all of its subgroups."""
    group = gl.groups.get(group_id_or_name)
    result = [group]
    for subgroup in group.subgroups.list(all=True):
        result.extend(get_groups_recursive(gl, subgroup.id))
    return result


def has_4eyes_approval(mr: gitlab.v4.objects.ProjectMergeRequest) -> MRApprovalResult:
    """Check whether a merge request satisfies the 4-eyes approval requirement."""
    approvals = mr.approvals.get()
    approved_by = approvals.approved_by
    author = mr.author['username']
    approvers = {user['user']['username'] for user in approved_by}
    passed = bool(approvers - {author})
    reasoning = f'MR !{mr.iid} by {author} approved by {", ".join(approvers)} - 4-eyes approval: {passed}'
    return MRApprovalResult(
        iid=mr.iid,
        passed=passed,
        reasoning=reasoning,
        title=mr.title,
        web_url=mr.web_url,
        state=mr.state,
        created_at=mr.created_at,
        updated_at=mr.updated_at,
    )


def mr_is_merged(mr: gitlab.v4.objects.ProjectMergeRequest) -> bool:
    """Return True if the MR state is merged."""
    return mr.state == 'merged'


def mr_updated_in_years(mr: gitlab.v4.objects.ProjectMergeRequest, years: list[int]) -> bool:
    """Return True if the MR was last updated in one of the given calendar years."""
    return datetime.fromisoformat(mr.updated_at).year in years


def get_mrs_by_project(project: gitlab.v4.objects.Project, filters: list[Any]) -> list[Any]:
    """Return all MRs from a project that pass every filter predicate."""
    return [mr for mr in project.mergerequests.list(all=True) if all(f(mr) for f in filters)]


def get_mrs_by_projects(projects: list[Any], filters: list[Any]) -> dict[str, list[Any]]:
    """Return a mapping of project name to filtered MR list for each project."""
    return {project.name: get_mrs_by_project(project, filters) for project in projects}


def evaluate_mrs_4eyes_per_project(project_mrs: dict[str, list[Any]]) -> list[ProjectMRAuditResult]:
    """Evaluate 4-eyes approval for every MR in every project."""
    return [
        ProjectMRAuditResult(name=name, mr_results=[has_4eyes_approval(mr) for mr in mrs])
        for name, mrs in project_mrs.items()
    ]


def filter_empty_results_by_field(items: list[Any], field_name: str) -> list[Any]:
    """Return only items where the given field is truthy."""
    return [r for r in items if getattr(r, field_name)]


def sort_results_by_field(items: list[Any], field_name: str) -> list[Any]:
    """Return items sorted ascending by the given field."""
    return sorted(items, key=lambda r: getattr(r, field_name))


def audit(url: str, token: str, config: Config) -> list[ProjectMRAuditResult]:
    """Run the full GitLab MR 4-eyes audit and return the results.

    Args:
        url: GitLab instance URL.
        token: GitLab personal access token.
        config: Parsed configuration object.

    Returns:
        List of per-project audit results, sorted by pass status, with empty projects excluded.
    """
    LOGGER.info('Starting audit validation for GitLab Merge Requests 4-eyes approval')
    gl = gitlab.Gitlab(url, token)

    LOGGER.info('Getting the groups recursively')
    gl_groups = []
    for group_cfg in config.gitlab.groups:
        gl_groups.extend(get_groups_recursive(gl, group_cfg.name))
    for group in gl_groups:
        LOGGER.info('  Group: %s (path: %s)', group.name, group.full_path)

    LOGGER.info('Getting the projects under the groups')
    gl_projects = []
    for group in gl_groups:
        group_projects = group.projects.list(all=True)
        LOGGER.info('  Group %s: %d project(s)', group.full_path, len(group_projects))
        for project in group_projects:
            LOGGER.info('    Project: %s (archived: %s)', project.path_with_namespace, project.archived)
            gl_projects.append(gl.projects.get(project.id))
    LOGGER.info(
        'Found %d project(s) (%d after excluding archived)',
        len(gl_projects),
        sum(1 for p in gl_projects if not p.archived),
    )

    LOGGER.info('Getting the merge requests under the projects')
    gl_project_mrs = get_mrs_by_projects(
        projects=[p for p in gl_projects if not p.archived],
        filters=[mr_is_merged, partial(mr_updated_in_years, years=config.gitlab.audit.years)],
    )

    LOGGER.info('Evaluating merge requests for 4-eyes approval')
    results = evaluate_mrs_4eyes_per_project(gl_project_mrs)
    results = filter_empty_results_by_field(results, 'mr_results')
    return sort_results_by_field(results, 'passed')
