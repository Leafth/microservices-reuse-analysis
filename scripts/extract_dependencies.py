import json
from pathlib import Path


def extract_dependencies(service_path):
    package_json_path = Path(service_path) / "package.json"

    if not package_json_path.is_file():
        print(f"package.json não encontrado: {service_path}")
        return None

    with package_json_path.open("r", encoding="utf-8") as file:
        package_data = json.load(file)

    return {
        "service": Path(service_path).name,
        "path": str(package_json_path),
        "dependencies": package_data.get("dependencies", {}),
        "devDependencies": package_data.get("devDependencies", {})
    }


if __name__ == "__main__":
    services = [
        "projects/exemplo/service-a",
        "projects/exemplo/service-b",
        "projects/exemplo/service-c"
    ]

    results = []

    for service in services:
        data = extract_dependencies(service)

        if data is not None:
            results.append(data)

    print(json.dumps(results, indent=2, ensure_ascii=False))
