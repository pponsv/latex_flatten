#!/usr/bin/env python

# A simple script for flattening LaTeX files by inlining included files.
#
# - Supports `\include` and `\input` commands.
# - Automatically adds extension `.tex` if the file does not have an extension.
# - Handles multiple include commands per line, comments.
# - Does not flatten recursively.

import re


def flatten_latex(main_name, output_name):
    """
    Flattens a LaTeX file by inlining included files.

    Args:
        main_name (str): Path to the main LaTeX file.
        output_name (str): Path to the output flattened file.
    """
    with open(main_name, "r") as main, open(output_name, "w") as output:
        for line in main.readlines():
            s = re.split("%", line, 2)
            tex = s[0]
            if len(s) > 1:
                comment = "%" + s[1]
            else:
                comment = ""

            chunks = re.split(r"\\(?:input|include)\{[^}]+\}", tex)

            if len(chunks) > 1:
                for c, t in zip(
                    chunks, re.finditer(r"\\(input|include)\{([^}]+)\}", tex)
                ):
                    cmd_name = t.group(1)
                    include_name = t.group(2)
                    if "." not in include_name:
                        include_name = include_name + ".tex"
                    if c.strip():
                        output.write(c + "\n")
                    output.write(f"% BEGIN \\{cmd_name}{{{include_name}}}\n")
                    with open(include_name, "r") as include:
                        output.write(include.read())
                    output.write(f"% END \\{cmd_name}{{{include_name}}}\n")
                tail = chunks[-1] + comment
                if tail.strip():
                    output.write(tail)
            else:
                output.write(line)


def main():
    import sys

    if len(sys.argv) != 3:
        sys.exit("USAGE: python3 -m latex_flatten.latex_flatten main.tex output.tex")

    main_name = sys.argv[1]
    output_name = sys.argv[2]
    flatten_latex(main_name, output_name)


if __name__ == "__main__":
    main()
