
import json
from pathlib import Path

from find_references import (
    find_references,
    EXTENSIONS,
    IGNORED_DIRECTORIES
)


def discover_internal_packages(project_path):
    project_path = Path(project_path)
    packages = {}

    for manifest in project_path.rglob("package.json"):
        if any(
            part in IGNORED_DIRECTORIES
            for part in manifest.parts
        ):
            continue

        try:
            data = json.loads(
                manifest.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, ValueError):
            continue

        name = data.get("name")

        if not isinstance(name, str) or not name:
            continue

        packages.setdefault(name, []).append(
            str(manifest.parent)
        )

    return packages


def find_internal_components(
    project_path, services, packages=None, references_by_name=None
):
    if packages is None:
        packages = discover_internal_packages(project_path)

    if references_by_name is None:
        references_by_name = {name: [] for name in packages}
        for service in services:
            for reference in find_references(service, set(packages)):
                references_by_name[reference["component"]].append(reference)

    shared = {}

    for package_name, locations in packages.items():
        usages = []

        for service in services:
            references = [
                reference
                for reference in references_by_name[package_name]
                if reference["service"] == Path(service).name
            ]

            if references:
                usages.append({
                    "service": Path(service).name,
                    "references": references
                })

        if len(usages) >= 2:
            shared[package_name] = {
                "origin": "internal_candidate",
                "locations": locations,
                "services_count": len(usages),
                "usages": usages,
                "status": "candidate"
            }

    return shared


if __name__ == "__main__":
    project = "projects/exemplo"

    services = [
        "projects/exemplo/service-a",
        "projects/exemplo/service-b",
        "projects/exemplo/service-c"
    ]

    results = find_internal_components(
        project,
        services
    )

    print(json.dumps(
        results,
        indent=2,
        ensure_ascii=False
    ))
