
import csv
import json
from pathlib import Path

from find_shared_dependencies import find_shared_dependencies
from find_references import find_references
from find_internal_components import discover_internal_packages, find_internal_components


PROJECT_NAME = "exemplo"
PROJECT_PATH = "projects/exemplo"

SERVICES = [
    str(manifest.parent)
    for manifest in sorted([
        *(Path(PROJECT_PATH) / "pods").glob("*/package.json"),
        *(Path(PROJECT_PATH) / "services").glob("*/package.json"),
        *(Path(PROJECT_PATH) / "services").glob("*/pod-*/package.json"),
        *(Path(PROJECT_PATH) / "services").glob("*/*-pod/package.json"),
        Path(PROJECT_PATH) / "services/ai-bot/love-agent/package.json",
    ])
    if manifest.is_file()
]

OUTPUT_DIR = Path("results") / PROJECT_NAME


def collect_results():
    print(f"Projeto: {PROJECT_NAME} ({len(SERVICES)} serviços)", flush=True)
    print("Lendo dependências declaradas...", flush=True)
    shared = find_shared_dependencies(SERVICES)
    print(f"Dependências compartilhadas: {len(shared)}", flush=True)

    print("Localizando pacotes internos...", flush=True)
    packages = discover_internal_packages(PROJECT_PATH)
    print(f"Pacotes internos encontrados: {len(packages)}", flush=True)

    names = set(shared) | set(packages)
    references_by_name = {name: [] for name in names}

    for index, service in enumerate(SERVICES, start=1):
        print(
            f"[{index}/{len(SERVICES)}] Buscando referências em {service}...",
            flush=True
        )
        references = find_references(
            service,
            names,
            progress_callback=lambda count: print(
                f"    {count} caminhos examinados em {service}...",
                flush=True
            )
        )
        for reference in references:
            references_by_name[reference["component"]].append(reference)
        print(f"    {len(references)} referências encontradas.", flush=True)

    print("Consolidando candidatos internos...", flush=True)
    internal = find_internal_components(
        PROJECT_PATH, SERVICES, packages, references_by_name
    )
    print(f"Candidatos internos: {len(internal)}", flush=True)

    results = []

    for name, data in shared.items():

        if name in internal:
            continue

        references = references_by_name[name]

        declared_services = sorted({
            usage["service"]
            for usage in data["usages"]
        })

        referenced_services = sorted({
            ref["service"]
            for ref in references
        })

        results.append({
            "project": PROJECT_NAME,
            "component": name,
            "origin": "unverified",
            "location": "",
            "declared_services": declared_services,
            "services_with_references": referenced_services,
            "declared_services_count": len(declared_services),
            "referenced_services_count": len(referenced_services),
            "references": references,
            "status": "candidate"
        })

    for name, data in internal.items():
        references = []

        for usage in data["usages"]:
            references.extend(usage["references"])

        referenced_services = sorted({
            ref["service"]
            for ref in references
        })

        results.append({
            "project": PROJECT_NAME,
            "component": name,
            "origin": "internal_candidate",
            "location": "; ".join(data["locations"]),
            "declared_services": [],
            "services_with_references": referenced_services,
            "declared_services_count": None,
            "referenced_services_count": len(referenced_services),
            "references": references,
            "status": "candidate"
        })

    return results


def export_json(results):
    output = OUTPUT_DIR / "candidates.json"

    with output.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"JSON gerado: {output}")


def export_csv(results):
    output = OUTPUT_DIR / "candidates.csv"

    columns = {
        "project": "Projeto",
        "component": "Componente",
        "origin": "Origem preliminar",
        "validated_origin": "Origem validada",
        "location": "Localização",
        "declared_services": "Serviços declarantes",
        "services_with_references": "Serviços com referências",
        "declared_services_count": "Qtd. serviços declarantes",
        "referenced_services_count": "Qtd. serviços com referências",
        "confirmed_services": "Serviços confirmados",
        "confirmed_services_count": "Qtd. serviços confirmados",
        "evidence": "Evidências",
        "status": "Situação da coleta",
        "validation_status": "Status da validação",
        "component_type": "Tipo do componente",
        "organization": "Organização",
        "reuse_mechanism": "Mecanismo de reutilização",
        "analyst": "Responsável pela análise",
        "reviewer": "Responsável pela revisão",
        "reviewer_notes": "Observações do revisor"
    }

    with output.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(columns.keys())
        )

        writer.writerow(columns)

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
                "validated_origin": "",
                "location": result["location"],
                "declared_services": "; ".join(
                    result["declared_services"]
                ),
                "services_with_references": "; ".join(
                    result["services_with_references"]
                ),
                "declared_services_count": (
                    result["declared_services_count"]
                    if result["declared_services_count"] is not None
                    else ""
                ),
                "referenced_services_count": result[
                    "referenced_services_count"
                ],
                "confirmed_services": "",
                "confirmed_services_count": "",
                "evidence": evidence,
                "status": result["status"],
                "validation_status": "",
                "component_type": "",
                "organization": "",
                "reuse_mechanism": "",
                "analyst": "",
                "reviewer": "",
                "reviewer_notes": ""
            })

    print(f"CSV gerado: {output}")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    results = collect_results()

    print(f"Exportando {len(results)} candidatos...", flush=True)
    export_json(results)
    export_csv(results)

    print(
        f"\nTotal de candidatos: {len(results)}"
    )
