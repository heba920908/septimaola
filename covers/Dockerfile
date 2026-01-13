FROM fedora:latest

# Install only the packages needed for la_dosis_perfecta.tex:
# - texlive-latex: provides lualatex command and article document class
# - texlive-musicography: for \usepackage{musicography}
# - texlive-songbook: for \usepackage{songbook}
# - texlive-lyluatex: for \usepackage{lyluatex} and lilypond environment
# - lilypond: executable required by lyluatex to compile music scores
RUN dnf install -y --skip-unavailable \
    texlive-latex \
    texlive-musicography \
    texlive-songbook \
    texlive-lyluatex \
    lilypond

WORKDIR /data
