# Latex Presentation for presskit

## Prerequisites

Download the assets from Google Drive: [Latex Assets](https://drive.google.com/file/d/1hYChucBrjdjkYjl1iyFMZohzh4mSEXAC/view?usp=sharing)

```shell
cd latex/
podman build -t latex-build .
podman run --rm -v $(pwd):/data latex-build latexmk -pdf -interaction=nonstopmode slides.tex
```

```shell
cd latex && latexmk -pdf -interaction=nonstopmode slides.tex
## Search for missing LaTeX packages:
dnf provides '*/multirow.sty' || true
## Build latex package
latexmk -pdf -interaction=nonstopmode slides.tex
```