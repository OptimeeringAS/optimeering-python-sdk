python_sources()

#### CREATE OPENAPI SCHEMA ####
python_source(
    name = "fix-openapi-extensions",
    source = "fix_openapi_extensions.py",
)

# To get the SHA and the length, use the following command
# curl -L https://app.optimeering.com/api/docs/openapi.json | tee >(wc -c) >(shasum -a 256) >/dev/null
resource(
    name = "openapi-schema",
    source = http_source(
        len = 110241,
        sha256 = "d3a3c880b29e27d9a6e875ed07583889ff67f6f4522911025d5283ca53ac5452",
        url = "https://app.optimeering.com/api/docs/openapi.json",
    ),
)
# resource(name="openapi-schema", source="openapi.json")

adhoc_tool(
    name = "run-fix-openapi-extensions",
    args = [
        "-s",
        "openapi.json",
    ],
    execution_dependencies = [
        ":openapi-schema",
    ],
    root_output_directory = ".",
    runnable = ":fix-openapi-extensions",
    stdout = "generate/openapi.json",
)

#### CREATE GENERATOR CONFIG ####
python_source(
    name = "create-config",
    dependencies = ["//:pyproject"],
    source = "create_config.py",
)

adhoc_tool(
    name = "run-create-config",
    root_output_directory = ".",
    runnable = ":create-config",
    stdout = "generate/config.json",
)

#### GENERATE CLIENT ####
files(
    name = "generator-files",
    sources = ["python_templates/**"],
)

# Specify JAR dependencies
jvm_artifact(
    name = "openapi-generator",
    artifact = "openapi-generator-cli",
    group = "org.openapitools",
    version = "7.10.0",
)

adhoc_tool(
    name = "generator",
    args = [
        "generate",
        "-i",
        "openapi.json",
        "--template-dir",
        "python_templates",
        "--config",
        "config.json",
        "--skip-validate-spec",
        "-g",
        "python",
        "-o",
        "./",
    ],
    execution_dependencies = [
        ":run-fix-openapi-extensions",
        ":run-create-config",
        ":generator-files",
        "//generate/additional_python_files:additional-python-files",
    ],
    output_directories = [
        "./optimeering",
    ],
    root_output_directory = ".",
    runnable = ":openapi-generator",
    workdir = ".",
)

shell_command(
    name = "run-generator",
    command = "echo Generated client",
    execution_dependencies = [":generator"],
    output_directories = [
        "./optimeering",
    ],
)

run_shell_command(
    name = "generate-client",
    command = """rm -rf ../optimeering
        mkdir ../optimeering
        cp -r {chroot}/optimeering ../
        rm -rf ../optimeering/docs ../optimeering/test
    """,
    execution_dependencies = [":generator"],
)
