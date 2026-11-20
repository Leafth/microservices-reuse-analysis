
import json
import re
from pathlib import Path

from find_shared_dependencies import find_shared_dependencies


EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}

IGNORED_DIRECTORIES = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "coverage",
    ".next"
}

IMPORT_PATTERNS = [
    # import express from "express"
    # import { Router } from "express"
    # import "express"
    re.compile(
        r'\bimport\s+(?:[^;]*?\s+from\s+)?["\']([^"\']+)["\']',
        re.MULTILINE
    ),

    # const express = require("express")
    re.compile(
        r'\brequire\s*\(\s*["\']([^"\']+)["\']\s*\)'
    ),

    # const module = await import("express")
    re.compile(
        r'\bimport\s*\(\s*["\']([^"\']+)["\']\s*\)'
    ),

    # export { something } from "package"
    re.compile(
        r'\bexport\s+[^;]*?\s+from\s+["\']([^"\']+)["\']',
        re.MULTILINE
    )
]


def get_package_name(module_path):
    if module_path.startswith(".") or module_path.startswith("/"):
        return None

    parts = module_path.split("/")

    if module_path.startswith("@"):
        return "/".join(parts[:2])

    return parts[0]


def find_references(service_path, dependencies):
    service_path = Path(service_path)
    references = []

    for file_path in service_path.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix not in EXTENSIONS:
            continue

        if any(
            part in IGNORED_DIRECTORIES
            for part in file_path.parts
        ):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue

        for pattern in IMPORT_PATTERNS:
            for match in pattern.finditer(content):
                module_path = match.group(1)
                package_name = get_package_name(module_path)

                if package_name not in dependencies:
                    continue

                line_number = content.count(
                    "\n", 0, match.start()
                ) + 1

                references.append({
                    "component": package_name,
                    "service": service_path.name,
                    "file": str(file_path),
                    "line": line_number,
                    "reference": module_path,
                    "evidence": match.group(0).strip()
                })

    return references


if __name__ == "__main__":
    services = [
        "projects/exemplo/service-a",
        "projects/exemplo/service-b",
        "projects/exemplo/service-c"
    ]

    shared = find_shared_dependencies(services)

    dependency_names = set(shared.keys())

    all_references = []

    for service in services:
        results = find_references(
            service,
            dependency_names
        )

        all_references.extend(results)

    print(json.dumps(
        all_references,
        indent=2,
        ensure_ascii=False
    ))
