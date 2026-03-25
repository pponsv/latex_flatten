# latex-flatten

A simple Python script for flattening LaTeX files by inlining included files. Forked from <https://github.com/rekka/latex-flatten>

  - Supports `\include` and `\input` commands.
  - Automatically adds extension `.tex` if the file does not have an extension.
  - Handles multiple include commands per line, comments.
  - Does not flatten recursively.


## Installation and usage

1. Clone this repository

2. Install using pip

        pip install .

4. The installation provides a script, `latex_flatten`:
        
        latex_flatten input.tex output.tex

## License

See UNLICENSE file.
