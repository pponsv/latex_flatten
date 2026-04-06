#!/usr/bin/env python

# A simple script for flattening LaTeX files by inlining included files.
#
# - Supports `\include` and `\input` commands.
# - Automatically adds extension `.tex` if the file does not have an extension.
# - Handles multiple include commands per line, comments.
# - Does not flatten recursively.
import os
import re
import shutil
from pathlib import Path


def move_imgs(set_imgs: set, main_path: Path, dest_path: Path):
    """
    Move all images, located at $initialdir/figs/dir/to/img.ext
    to $initialdir/flattened/img.ext
    Assume initialdir/flattened/ exists.
    """
    filetypes = ["pdf", "eps", "png", "svg", "jpg", "jpeg"]
    for img in set_imgs:
        if (img.split(".")[-1]).lower() not in filetypes:
            img += ".pdf"
        src = main_path / "figs" / img
        dst = dest_path / Path(img).name
        print(img, src, dest_path)
        if src.exists():
            shutil.copy(str(src), str(dst))
        else:
            raise ValueError(f"Source does not exist: {src}")
        # print(img, initialdir, initialdir / "figs" / img)


def extract_images_from_line(line):
    """
    Parses a single string/line for LaTeX \\includegraphics filenames,
    and removes any directory structure
    """
    # Pattern explanation:
    # \\includegraphics      -> Matches the command
    # (?:\[.*?\])?           -> Non-capturing group for optional [args], 0 or 1 times
    # \{                     -> Opening brace
    # ([^}]+)                -> Capturing group: everything that isn't a closing brace
    # \}                     -> Closing brace
    match_pattern = r"\\includegraphics(?:\[.*?\])?\{([^}]+)\}"
    patterns = []

    def modify(match: re.Match):
        original = match.group(1)
        patterns.append(original)
        new = Path(original).name
        return match.group(0).replace(original, new)

    # findall returns a list of all filenames found in the string
    newline = re.sub(match_pattern, modify, line)
    return patterns, newline


def process_line_include(line: str, main_dir: Path):
    new_lines = []
    imgs = []
    s = re.split("%", line, 2)
    tex = s[0]
    if len(s) > 1:
        comment = "%" + s[1]
    else:
        comment = ""

    chunks = re.split(r"\\(?:input|include)\{[^}]+\}", tex)

    if len(chunks) > 1:
        for c, t in zip(chunks, re.finditer(r"\\(input|include)\{([^}]+)\}", tex)):
            cmd_name = t.group(1)
            include_name = t.group(2)
            if "." not in include_name:
                include_name = include_name + ".tex"
            if c.strip():
                new_lines.append(c + "\n")
            new_lines.append(f"% BEGIN \\{cmd_name}{{{include_name}}}\n")
            with open(main_dir / include_name, "r") as include:
                temp_lines = include.readlines()
                for idx, line in enumerate(temp_lines):
                    figs, newline = extract_images_from_line(line)
                    if figs:
                        imgs.extend(figs)
                        temp_lines[idx] = newline
                new_lines.extend(temp_lines)
            new_lines.append(f"% END \\{cmd_name}{{{include_name}}}\n")
        tail = chunks[-1] + comment
        if tail.strip():
            new_lines.append(tail)
    else:
        new_lines.append(line)
    return new_lines, imgs


def _flatten_latex(main_name, output_name=""):
    """
    Flattens a LaTeX file by inlining included files.

    Args:
        main_name (str): Path to the main LaTeX file.
        output_name (str): Path to the output flattened file. If
    """
    if output_name == "":
        output_name = "flattened/output.tex"
        dest_dir = Path(output_name).resolve().parent
        print(dest_dir)
        if dest_dir.exists() and dest_dir.is_dir():
            shutil.rmtree(dest_dir)
        os.makedirs(dest_dir, exist_ok=True)

    main_dir = Path(main_name).resolve().parent
    print(main_dir)

    with open(main_name, "r") as main_file, open(output_name, "w") as output:
        all_imgs = []
        for line in main_file.readlines():
            # Check if there are \includegraphics
            imgs, line = extract_images_from_line(line)
            if imgs:
                all_imgs.extend(imgs)
            # Check if there are \input or \include
            new_lines, imgs = process_line_include(line, main_dir=main_dir)
            if imgs:
                all_imgs.extend(imgs)
            output.writelines(new_lines)
    print(all_imgs)
    set_imgs = set(all_imgs)
    move_imgs(set_imgs, main_dir, dest_dir)
    return main_dir, main_name, output_name


def flatten_latex():
    import sys

    if len(sys.argv) not in [2, 3]:
        sys.exit("USAGE: latex_flatten main.tex output.tex")

    main_name = sys.argv[1]
    if len(sys.argv) == 3:
        output_name = sys.argv[2]
    else:
        output_name = ""
    _flatten_latex(main_name, output_name)


if __name__ == "__main__":
    flatten_latex()
