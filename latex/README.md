# Latex Presentation for presskit

```shell
cd latex && latexmk -pdf -interaction=nonstopmode slides.tex
## Search for missing LaTeX packages:
dnf provides '*/multirow.sty' || true
## Build latex package
latexmk -pdf -interaction=nonstopmode slides.tex
```