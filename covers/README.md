# Latex Music Examples sheets

## Prerequisites

```shell
cd covers/
podman build -t latex-build-covers .
podman run --rm -v $(pwd):/data:z latex-build-covers luatex --shell-escape -interaction=nonstopmode la_dosis_perfecta.tex
```

Note: This document uses `lyluatex` which requires:
- LuaTeX (lualatex) instead of pdfTeX
- `--shell-escape` flag to allow LilyPond execution
- LilyPond executable (included in the Docker image)

To search for specific package:

```shell
## Search for missing LaTeX packages:
podman run --rm latex-build dnf provides '*/package.sty' || true
```