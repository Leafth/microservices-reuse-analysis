
from collections import defaultdict
from extract_dependencies import extract_dependencies


def find_shared_dependencies(services):
    dependencies = defaultdict(list)

    for service_path in services:
        data = extract_dependencies(service_path)

        if data is None:
            continue

        service_name = data["service"]

        for dependency, version in data["dependencies"].items():
            dependencies[dependency].append({
                "service": service_name,
                "version": version,
                "type": "production"
            })

        for dependency, version in data["devDependencies"].items():
            dependencies[dependency].append({
                "service": service_name,
                "version": version,
                "type": "development"
            })

    shared_dependencies = {}

    for dependency, usages in dependencies.items():
        unique_services = {usage["service"] for usage in usages}

        if len(unique_services) >= 2:
            shared_dependencies[dependency] = {
                "services_count": len(unique_services),
                "usages": usages,
                "status": "candidate"
            }

    return shared_dependencies


if __name__ == "__main__":
    import json

    services = [
        "projects/exemplo/service-a",
        "projects/exemplo/service-b",
        "projects/exemplo/service-c"
    ]

    results = find_shared_dependencies(services)

    print(json.dumps(results, indent=2, ensure_ascii=False))
