files(
    name="source",
    sources=["source/**"],
)

pex_binary(
    name="sphinx",
    dependencies=[
        "//:root#orjson",
        "//:root#sphinx",
        "//:root#pandas",
        "//:root#pydantic",
        "//:root#python-dateutil",
        "//:root#azure-identity",
        "//:root#sphinx-rtd-theme",
        "//:root#setuptools",
        "//:root#toml",
        "//:root#urllib3",
        "//:root#typing-extensions",
        "//:root#types-python-dateutil",
        "//:root#sphinx-autodoc-typehints",
        "//optimeering:optimeering",
    ],
    script="sphinx-build",
)

adhoc_tool(
    name="gen-tool",
    args=[
        "-M",
        "html",
        "source",
        "generated-site",
    ],
    execution_dependencies=[
        ":source",
        "//:pyproject",
        "//optimeering:optimeering",
    ],
    output_directories=[""],
    output_files=["generated-site/**"],
    runnable=":sphinx",
)

run_shell_command(
    name="build-docs",
    command="""rm -rf docs/site
    mkdir docs/site
    cp -r {chroot}/docs/generated-site/html/. docs/site
    """,
    execution_dependencies=[":gen-tool"],
    workdir="",
)
