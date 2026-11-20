
import csv
import json
from pathlib import Path

from find_shared_dependencies import find_shared_dependencies
from find_references import find_references
from find_internal_components import find_internal_components


PROJECT_NAME = "exemplo"
PROJECT_PATH = "projects/exemplo"

SERVICES = [
    "projects/exemplo/service-a",
    "projects/exemplo/service-b",
    "projects/exemplo/service-c"
]

OUTPUT_DIR = Path("results") / PROJECT_NAME


def collect_results():
    shared = find_shared_dependencies(SERVICES)
    internal = find_internal_components(PROJECT_PATH, SERVICES)

    results = []

    # Componentes de dependências declaradas em comum
    for name, data in shared.items():
        # Evita duplicar pacotes internos
        if name in internal:
            continue

        references = []

        for service in SERVICES:
            references.extend(
                find_references(service, {name})
            )

        results.append({
            "project": PROJECT_NAME,
            "component": name,
            "origin": "unverified",
            "location": "",
            "declared_services": [
                usage["service"]
                for usage in data["usages"]
            ],
            "services_with_references": sorted({
                ref["service"]
                for ref in references
            }),
            "services_count": data["services_count"],
            "references": references,
            "status": "candidate"
        })

    # Possíveis pacotes internos
    for name, data in internal.items():
        references = []

        for usage in data["usages"]:
            references.extend(usage["references"])

        results.append({
            "project": PROJECT_NAME,
            "component": name,
            "origin": "internal_candidate",
            "location": "; ".join(data["locations"]),
            "declared_services": [],
            "services_with_references": sorted({
                ref["service"]
                for ref in references
            }),
            "services_count": data["services_count"],
            "references": references,
            "status": "candidate"
        })

    return results


def export_json(results):
    output = OUTPUT_DIR / "candidates.json"

    with output.open("w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"JSON gerado: {output}")


def export_csv(results):
    output = OUTPUT_DIR / "candidates.csv"

    fields = [
        "project",
        "component",
        "origin",
        "location",
        "declared_services",
        "services_with_references",
        "services_count",
        "evidence",
        "status",
        "validation_status",
        "component_type",
        "organization",
        "reuse_mechanism",
        "reviewer_notes"
    ]

    with output.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for result in results:
            evidence = " | ".join(
                f'{ref["file"]}:{ref["line"]} '
                f'{ref["evidence"]}'
                for ref in result["references"]
            )

            writer.writerow({
                "project": result["project"],
                "component": result["component"],
                "origin": result["origin"],
                "location": result["location"],
                "declared_services": "; ".join(
                    sorted(set(result["declared_services"]))
                ),
                "services_with_references": "; ".join(
                    result["services_with_references"]
                ),
                "services_count": result["services_count"],
                "evidence": evidence,
                "status": result["status"],
                "validation_status": "",
                "component_type": "",
                "organization": "",
                "reuse_mechanism": "",
                "reviewer_notes": ""
            })

    print(f"CSV gerado: {output}")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = collect_results()

    export_json(results)
    export_csv(results)

    print(f"\nTotal de candidatos: {len(results)}")
