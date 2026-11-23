
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
        r'\bimport\s+(?:[^;"\']*?\s+from\s+)?["\']([^"\']+)["\']'
    ),

    # require("express")
    re.compile(
        r'\brequire\s*\(\s*["\']([^"\']+)["\']\s*\)'
    ),

    # import("express")
    re.compile(
        r'\bimport\s*\(\s*["\']([^"\']+)["\']\s*\)'
    ),

    # export { something } from "package"
    re.compile(
        r'\bexport\s+[^;"\']*?\s+from\s+["\']([^"\']+)["\']'
    )
]

TOKEN_PATTERN = re.compile(
    r'(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)'
    r'|(?P<string>"(?:\\.|[^"\\])*"|'
    r"'(?:\\.|[^'\\])*')"
    r'|(?P<template>`(?:\\.|[^`\\])*`)',
    re.DOTALL
)


def mask_text(text):
    return "".join(
        "\n" if char == "\n" else " "
        for char in text
    )


def clean_source_code(content):
    result = []
    last_position = 0

    for match in TOKEN_PATTERN.finditer(content):
        start, end = match.span()

        result.append(content[last_position:start])

        token = match.group(0)

        if match.group("comment") or match.group("template"):
            result.append(mask_text(token))

        else:
            previous_code = "".join(result)

            is_module_reference = re.search(
                r'\b(?:from|import|require)\s*'
                r'(?:\(\s*)?$',
                previous_code
            )

            if is_module_reference:
                result.append(token)
            else:
                result.append(mask_text(token))

        last_position = end

    result.append(content[last_position:])

    return "".join(result)


def get_package_name(module_path):
    if module_path.startswith(".") or module_path.startswith("/"):
        return None

    parts = module_path.split("/")

    if module_path.startswith("@"):
        return "/".join(parts[:2])

    return parts[0]


def find_references(service_path, dependencies, progress_callback=None):
    service_path = Path(service_path)
    references = []
    seen = set()

    for paths_seen, file_path in enumerate(service_path.rglob("*"), start=1):
        if progress_callback is not None and paths_seen % 1000 == 0:
            progress_callback(paths_seen)

        if not file_path.is_file():
            continue

        if file_path.suffix not in EXTENSIONS:
            continue

        if any(
            part in IGNORED_DIRECTORIES
            for part in file_path.relative_to(service_path).parts
        ):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue

        cleaned_content = clean_source_code(content)

        for pattern in IMPORT_PATTERNS:
            for match in pattern.finditer(cleaned_content):
                module_path = match.group(1)
                package_name = get_package_name(module_path)

                if package_name not in dependencies:
                    continue

                line_number = content.count(
                    "\n", 0, match.start()
                ) + 1

                reference_key = (
                    str(file_path),
                    match.start(),
                    module_path
                )

                if reference_key in seen:
                    continue

                seen.add(reference_key)

                # Recupera a evidência do código original
                original_evidence = content[
                    match.start():match.end()
                ]

                references.append({
                    "component": package_name,
                    "service": service_path.name,
                    "file": str(file_path),
                    "line": line_number,
                    "reference": module_path,
                    "evidence": original_evidence.strip()
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
        all_references.extend(
            find_references(service, dependency_names)
        )

    print(json.dumps(
        all_references,
        indent=2,
        ensure_ascii=False
    ))
