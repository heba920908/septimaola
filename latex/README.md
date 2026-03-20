# Latex Presentation for presskit

## Prerequisites

Download the assets from Google Drive: [Latex Assets](https://drive.google.com/file/d/1hYChucBrjdjkYjl1iyFMZohzh4mSEXAC/view?usp=sharing) or [Mega.nz](https://mega.nz/folder/CkAVkayT#zJW87QfsZSpPPf0MSAbvSg)

```shell
cd latex/
podman build -t latex-build .
podman run --rm -v $(pwd):/data latex-build latexmk -pdf -interaction=nonstopmode slides.tex
# in fedora
podman run --rm -it --user root:root -v .:/data:z latex-build latexmk -pdf -interaction=nonstopmode slides.tex
```

## To find the values

```shell
## Search for missing LaTeX packages:
dnf provides '*/multirow.sty' || true
## Build latex package
latexmk -pdf -interaction=nonstopmode slides.tex
```
