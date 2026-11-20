
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


def find_internal_components(project_path, services):
    packages = discover_internal_packages(project_path)

    shared = {}

    for package_name, locations in packages.items():
        usages = []

        for service in services:
            references = find_references(
                service,
                {package_name}
            )

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
