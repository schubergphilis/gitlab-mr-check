"""Command-line interface for gitlab-mr-check."""

import argparse
import csv
import logging
import os
import sys
from functools import partial
from pathlib import Path
from typing import Any

from tabulate import tabulate

from gitlab_mr_check.gitlab_mr_check import audit
from gitlab_mr_check.helpers.config import parse_config_file

LOGGER = logging.getLogger('gitlab-mr-check')


def parse_args() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(description='Validate that all MRs have 4-eyes approval')
    parser.add_argument('--url', default=os.environ.get('URL', ''), help='GitLab host URL')
    parser.add_argument('--token', default=os.environ.get('TOKEN', ''), help='GitLab access token')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    parser.add_argument('--output', choices=['table', 'csv'], default='table', help='Output format')
    parser.add_argument('--output-file', help='Output file for CSV (default: stdout)')
    parser.add_argument('--fields', help='Comma-separated list of fields to include')
    args = parser.parse_args()
    if not args.url or not args.token:
        parser.error('--url and --token are required (or set URL and TOKEN env vars)')
    if args.output == 'csv' and not args.output_file:
        parser.error('--output-file is required when --output is csv')
    args.url = args.url.rstrip('/')
    args.fields = [f.strip() for f in args.fields.split(',') if f.strip()] if args.fields else None
    return args


def output_table(results: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    """Print results as a formatted table to stdout."""
    if fields:
        results = [{k: row.get(k, '') for k in fields} for row in results]
    print(tabulate(results, headers='keys'))  # noqa: T201


def output_csv(
    results: list[dict[str, Any]],
    output_file: str | None = None,
    fields: list[str] | None = None,
) -> None:
    """Write results as CSV to a file or stdout."""
    if fields:
        results = [{k: row.get(k, '') for k in fields} for row in results]
    fieldnames = list(results[0].keys()) if results else []
    if output_file:
        with Path(output_file).open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def show_results(
    results: list[dict[str, Any]],
    output_format: str,
    output_file: str | None = None,
    fields: list[str] | None = None,
) -> None:
    """Dispatch results to the appropriate output function."""
    output_funcs: dict[str, Any] = {
        'table': partial(output_table, fields=fields),
        'csv': partial(output_csv, output_file=output_file, fields=fields),
    }
    try:
        output_funcs[output_format](results)
    except KeyError as exc:
        msg = f'Unknown output format: {output_format}'
        raise ValueError(msg) from exc


def main() -> None:
    """Entry point for the gitlab-mr-check CLI."""
    args = parse_args()
    logging.basicConfig(level=args.log_level.upper())
    try:
        config = parse_config_file(args.config)
    except FileNotFoundError:
        sys.exit(f'Config file not found: {args.config}')
    except ValueError as exc:
        sys.exit(f'Invalid config: {exc}')
    results = audit(url=args.url, token=args.token, config=config)
    rows = [
        {'project': r.name, 'iid': mr.iid, 'passed': mr.passed, 'reasoning': mr.reasoning}
        for r in results
        for mr in r.mr_results
    ]
    show_results(rows, args.output, output_file=args.output_file, fields=args.fields)
