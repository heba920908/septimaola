# Latex Presentation for presskit

## Prerequisites

Download the assets from Google Drive: [Latex Assets](https://drive.google.com/file/d/1hYChucBrjdjkYjl1iyFMZohzh4mSEXAC/view?usp=sharing) or [Mega.nz](https://mega.nz/folder/CkAVkayT#zJW87QfsZSpPPf0MSAbvSg)

```shell
# IF you have everything installed in your system
latexmk -pdf -interaction=nonstopmode slides.tex

# Either the presskit
podman run --rm -v $(pwd):/data latex-build latexmk -pdf -interaction=nonstopmode slides.tex
# in fedora
podman run --rm -it --user root:root -v .:/data:z latex-build latexmk -pdf -interaction=nonstopmode slides.tex
```
