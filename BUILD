poetry_requirements(
    name="root",
)

python_distribution(
    name="optimeering",
    dependencies=[
        "//optimeering:optimeering",
        ":root#orjson",
    ],
    long_description_path="README.md",
    output_path="optimeering-python-sdk",
    provides=python_artifact(
        name="optimeering",
        author="Optimeering",
        classifiers=[
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
        ],
        description="Optimeering Python Client",
        long_description_content_type="text/markdown",
        version="0.0.5",
    ),
    wheel_config_settings={
        "--global-option": [
            "--python-tag",
            "py310.py311",
        ]
    },
)

file(
    name="pyproject",
    source="pyproject.toml",
)
