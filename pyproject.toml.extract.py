import toml

# Must install toml
# ```pip install toml```


def convert_version_constraints(dependency: str) -> str:
    if dependency.startswith("^"):
        # Convert caret (^) constraints
        major_version = dependency[1:].split(".", maxsplit=1)[0]
        return f">={dependency[1:]},<{int(major_version) + 1}.0"
    if dependency.startswith("~"):
        # Convert tilde (~) constraints
        parts = dependency[1:].split(".")
        if len(parts) > 1:
            minor_version = int(parts[1]) + 1
            return f">={dependency[1:]},<{parts[0]}.{minor_version}"
        return f">={dependency[1:]},<{int(parts[0]) + 1}.0"
    # Return as-is for other constraints
    return dependency


def extract_dependencies(toml_filaname: str, output_files: dict[str, str]) -> None:
    with open(toml_filaname, encoding="utf-8") as file:
        pyproject = toml.load(file)

    # Get dependencies and optional dependencies
    project = pyproject.get("project", {})
    dependencies = project.get("dependencies", [])
    optional_dependencies = project.get("optional-dependencies", {})

    # Add primary dependencies to the optional_dependencies dictionary under the "" key
    optional_dependencies[""] = dependencies

    # Extract and write dependencies for each group
    for group, output_file in output_files.items():
        group_dependencies = optional_dependencies.get(group, [])
        formatted_dependencies = []

        for dep in group_dependencies:
            if isinstance(dep, str):
                # If dependency is a simple string (e.g., "pytest")
                formatted_dependencies.append(dep)
            elif isinstance(dep, dict):
                # If dependency has version constraints (e.g., {"pytest": "^7.0"})
                for package, version in dep.items():
                    formatted_dependencies.append(f"{package}{convert_version_constraints(version)}")
            else:
                formatted_dependencies.append(dep)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write("\n".join(formatted_dependencies))


toml_file = "pyproject.toml"
output_files = {
    "dev": "dev-requirements.txt",
    "test": "test-requirements.txt",
    "docs": "docs-requirements.txt",
    "": "requirements.txt",  # Primary dependencies
}

extract_dependencies(toml_file, output_files)
