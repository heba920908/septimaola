# Letter

Original source from https://www.overleaf.com/latex/templates/uioletter/gjjhmdqrxtvz.

You can use the image from [../README.md](../README.md) to build the CV, all the pre-requisites are installed in the `latex-build` container.

```shell
cd latex/letter_motivos/

podman run --rm -v .:/data latex-build latexmk -pdf -interaction=nonstopmode letter.tex
podman run --rm -v $(pwd):/data latex-build latexmk -pdf -interaction=nonstopmode letter.tex
```
