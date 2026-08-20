---
description: This file describes the LaTeX code style for the project.
applyTo: **/*.tex
---

# Building LaTeX Documents

## Constraints

* Do not focus on installing missing dependencies. The build process should be self-contained and not require additional packages to be installed on the system.
* If the build process fails due to missing dependencies stop and report the error. Do not attempt to fix the build process or install missing dependencies.

## Workaround

Podman is a containerization tool that can be used to run LaTeX builds in a controlled environment. The following commands can be used to build LaTeX documents using a pre-built podman image.

```shell
# For native linux systems
podman run --rm --userns keep-id -v .:/data:Z latex-build latexmk -pdf -interaction=nonstopmode letter.tex

# For wsl systems
podman run --rm -v $(pwd):/data latex-build latexmk -pdf -interaction=nonstopmode letter.tex
```

If podman it is installed try the podman image which should be pre-built
* DO NOT attempt to install podman or to build the image. Instead, report the error and ask for help.
