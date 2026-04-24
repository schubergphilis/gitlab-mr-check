"""Configuration loading and parsing for gitlab-mr-check."""

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class GitlabGroupConfig:
    """Configuration for a single GitLab group."""

    name: str = ''

    def __bool__(self) -> bool:
        """Return True if the group name is set."""
        return bool(self.name)


@dataclass
class GitlabAuditConfig:
    """Configuration for the audit scope (which years to include)."""

    years: list[int] = field(default_factory=list)

    def __bool__(self) -> bool:
        """Return True if at least one audit year is configured."""
        return bool(self.years)


class GitlabConfig:
    """Configuration for the GitLab connection and audit scope."""

    def __init__(self, groups: list[dict], audit: dict) -> None:
        """Initialise GitLab config from raw dicts."""
        self.groups = [GitlabGroupConfig(**group) for group in groups]
        self.audit = GitlabAuditConfig(**audit)

    def __bool__(self) -> bool:
        """Return True if both groups and audit scope are configured."""
        return all([self.groups, self.audit])


@dataclass
class LoggingConfig:
    """Configuration for the optional MDR log handler."""

    host: str = ''
    token: str = ''
    ssl_verify: bool = True

    def __post_init__(self) -> None:
        """Override host and token from environment variables when not set explicitly."""
        self.host = self.host or os.getenv('LOGGING_HOST', '')
        self.token = self.token or os.getenv('LOGGING_TOKEN', '')


@dataclass
class Config:
    """Root configuration object."""

    gitlab: GitlabConfig
    logging: LoggingConfig

    def __bool__(self) -> bool:
        """Return True if the GitLab config is populated."""
        return bool(self.gitlab)


def _read_config_file(config_path: str) -> str:
    """Read a config file and return its raw contents."""
    try:
        with Path(config_path).open(encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError as exc:
        msg = f'Configuration file not found: {config_path}'
        raise FileNotFoundError(msg) from exc
    if not content.strip():
        msg = f"Configuration file '{config_path}' is empty."
        raise ValueError(msg)
    return content


def _parse_config_data(content: str) -> dict:
    """Parse a YAML string and return the result as a dict."""
    try:
        config_data = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        msg = f'Error parsing configuration file as YAML: {exc}'
        raise ValueError(msg) from exc

    if not isinstance(config_data, dict):
        msg = 'Parsed YAML is not a dict'
        raise TypeError(msg)

    return config_data


def build_config(config_data: dict) -> Config:
    """Build a Config object from a raw config dict."""
    try:
        gitlab_config = GitlabConfig(**config_data.get('gitlab', {}))
        logging_config = LoggingConfig(**config_data.get('logging', {}))
    except (KeyError, TypeError) as exc:
        msg = f'Missing required configuration key: {exc}'
        raise ValueError(msg) from exc

    config = Config(gitlab=gitlab_config, logging=logging_config)

    if not config:
        msg = 'Incomplete configuration data.'
        raise ValueError(msg)

    return config


def parse_config_file(config_path: str) -> Config:
    """Read, parse, and validate a YAML config file into a Config object."""
    content = _read_config_file(config_path)
    config_data = _parse_config_data(content)
    return build_config(config_data)
