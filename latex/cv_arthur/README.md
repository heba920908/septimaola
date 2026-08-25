# CV

Hipster CV source https://github.com/latex-ninja/hipster-cv/tree/master

## Build

### Prerequisites

Need to choose the `music_logo.jpg` from google.com or you can use multiple logos, check at the example.

Need to get the `arthur.jpg` from some image that really like you.

To resize images

```shell
magick arthur.jpg -resize 800x arthur.png
magick music_logo.jpg -resize 100x100! music_logo.png
```

### Building the CV

You can use the image from [../README.md](../README.md) to build the CV, all the pre-requisites are installed in the `latex-build` container.

```shell
cd latex/cv/
podman run --rm -v $(pwd):/data latex-build latexmk -pdf -interaction=nonstopmode main.tex
```
