FROM fedora:latest

## For all dependencies to be installed without complications:
## RUN dnf install -y textlive-*
## I tend to believe the textlive-scheme-full is doing the sameas textlive-*
RUN dnf install -y --skip-unavailable \
    texlive-scheme-full \
    texlive-collection-fontsrecommended \
    texlive-collection-latexextra \
    texlive-chktex \
    texlive-latex \
    texlive-schemabloc \
    texlive-multirow \
    texlive-wrapfig \
    texlive-biblatex-apa \
    texlive-pgfplots \
    texlive-adjustbox \
    texlive-environ \
    latexmk \
    biber

RUN useradd -m latexuser --shell /bin/bash --uid 1000 && \
    mkdir /data && \
    chown latexuser:latexuser /data

USER latexuser
WORKDIR /data
