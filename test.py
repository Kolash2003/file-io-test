from pathlib import Path

BASE = Path("io_demo")


with open(BASE / "notes.txt", "w", encoding="utf-8") as f:
    f.write("Line 1\n")
    f.write("Line 2\n")
    f.writelines(["Line 3\n", "Line 4\n"])

with open(BASE / "notes.txt", "a", encoding="utf-8") as f:
    f.write("Line 5\n")

try:
    with open(BASE / "notes.txt", "x", encoding="utf-8") as f:
        pass
except FileExistsError:
    print("'x' mode: file already exists -> fileExistsError")

## one crazy thing is that even print can write to a file too
with open(BASE / "write_with_print.txt", "a") as f:
    print("hello via print", file=f)


with open(BASE/ "notes.txt", encoding="utf-8")

