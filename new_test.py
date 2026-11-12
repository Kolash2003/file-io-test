from pathlib import Path

folder = Path("my_folder")
folder.mkdir(exist_ok=True)

with open(folder / "hello.txt", "w", encoding="utf-8") as f:
    f.write("Hello this is a file inside my_folder\n")

with open(folder / "hello.txt", "a", encoding="utf-8") as f:
    f.write("this is a new line\n")

try:
    with open(folder / "hello.txt", "a", encoding="utf-8") as f:
        f.write("this is new line 2\n")
except FileNotFoundError:
    print("file not found error")
except OSError as error:
    print("oserror occured", error)


def copy():
    with open(folder / "hell_copy.txt", "wb") as d, open(folder / "hello.txt", "rb", size=1024 * 1024) as s:
        while chunk := s.read(size):
            d.write(chunk)

