"""
Essential File I/O operations in Python.
Run this file: it creates a scratch folder "io_demo" and demonstrates each topic.
"""

import os
import csv
import json
import pickle
import shutil
import tempfile
import zipfile
from pathlib import Path

BASE = Path("io_demo")
BASE.mkdir(exist_ok=True)


def section(title):
    print(f"\n=== {title} ===")


# 1. WRITING TEXT ('w' overwrites, 'a' appends, 'x' fails if file exists)
section("1. Writing text")
with open(BASE / "notes.txt", "w", encoding="utf-8") as f:
    f.write("Line 1\n")
    f.write("Line 2\n")
    f.writelines(["Line 3\n", "Line 4\n"])

with open(BASE / "notes.txt", "a", encoding="utf-8") as f:   # append
    f.write("Line 5 (appended)\n")

try:
    with open(BASE / "notes.txt", "x") as f:                 # exclusive create
        pass
except FileExistsError:
    print("'x' mode: fiDependency-free RAG over le already exists -> FileExistsError")

# print() can write to a file too
with open(BASE / "print_out.txt", "w") as f:
    print("hello via print", file=f)


# 2. READING TEXT
section("2. Reading text")
with open(BASE / "notes.txt", encoding="utf-8") as f:
    print("read():", repr(f.read()))                 # whole file as one string

with open(BASE / "notes.txt", encoding="utf-8") as f:
    print("readline():", repr(f.readline()))         # one line
    print("readlines():", f.readlines())             # remaining lines as list

with open(BASE / "notes.txt", encoding="utf-8") as f:
    for line in f:                                   # best for big files (lazy)
        print("iter:", line.rstrip())

with open(BASE / "notes.txt", encoding="utf-8") as f:
    print("read(6):", repr(f.read(6)))               # fixed number of chars


# 3. FILE POINTER: tell / seek
section("3. tell() and seek()")
with open(BASE / "notes.txt", "r+", encoding="utf-8") as f:   # r+ = read & write
    f.read(4)
    print("position:", f.tell())
    f.seek(0)                                        # back to start
    print("after seek(0):", repr(f.readline()))
    f.seek(0, os.SEEK_END)                           # jump to end
    f.write("Line 6 (r+ at end)\n")


# 4. BINARY FILES
section("4. Binary I/O")
data = bytes([0, 1, 2, 255, 128])
with open(BASE / "data.bin", "wb") as f:
    f.write(data)
with open(BASE / "data.bin", "rb") as f:
    print("bytes:", list(f.read()))

# copy a big file in chunks
def copy_chunks(src, dst, size=1024 * 1024):
    with open(src, "rb") as s, open(dst, "wb") as d:
        while chunk := s.read(size):
            d.write(chunk)

copy_chunks(BASE / "data.bin", BASE / "data_copy.bin")


# 5. pathlib shortcuts
section("5. pathlib")
p = BASE / "pathlib.txt"
p.write_text("written with pathlib\n", encoding="utf-8")
print(p.read_text(encoding="utf-8").strip())
p.write_bytes(b"\x00\x01")
print(p.read_bytes())
print("exists:", p.exists(), "| is_file:", p.is_file(), "| size:", p.stat().st_size)
print("name:", p.name, "| stem:", p.stem, "| suffix:", p.suffix, "| parent:", p.parent)


# 6. CSV
section("6. CSV")
rows = [["name", "age"], ["Alice", 30], ["Bob", 25]]
with open(BASE / "people.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows)

with open(BASE / "people.csv", newline="", encoding="utf-8") as f:
    for row in csv.reader(f):
        print(row)

with open(BASE / "people2.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["name", "age"])
    w.writeheader()
    w.writerow({"name": "Carol", "age": 41})

with open(BASE / "people2.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(dict(row))


# 7. JSON
section("7. JSON")
obj = {"name": "Alice", "skills": ["python", "sql"], "active": True}
with open(BASE / "data.json", "w", encoding="utf-8") as f:
    json.dump(obj, f, indent=2)
with open(BASE / "data.json", encoding="utf-8") as f:
    print(json.load(f))
print(json.dumps(obj))                 # to string
print(json.loads('{"a": 1}'))          # from string


# 8. PICKLE (only unpickle data you trust!)
section("8. Pickle")
with open(BASE / "obj.pkl", "wb") as f:
    pickle.dump({"set": {1, 2, 3}, "tuple": (1, 2)}, f)
with open(BASE / "obj.pkl", "rb") as f:
    print(pickle.load(f))


# 9. FILE & DIRECTORY MANAGEMENT (os / shutil / pathlib)
section("9. File & directory management")
(BASE / "sub" / "deep").mkdir(parents=True, exist_ok=True)
shutil.copy(BASE / "notes.txt", BASE / "sub" / "notes_copy.txt")     # copy
shutil.copy2(BASE / "notes.txt", BASE / "sub" / "notes_meta.txt")    # copy + metadata
shutil.move(BASE / "sub" / "notes_copy.txt", BASE / "sub" / "deep" / "moved.txt")
os.rename(BASE / "sub" / "notes_meta.txt", BASE / "sub" / "renamed.txt")
print("listdir:", sorted(os.listdir(BASE / "sub")))
print("glob *.txt:", sorted(x.name for x in BASE.glob("*.txt")))
print("rglob *.txt:", sorted(str(x) for x in BASE.rglob("*.txt")))

for root, dirs, files in os.walk(BASE):                              # recursive walk
    print(root, dirs, files)

with os.scandir(BASE) as it:                                         # fast listing w/ metadata
    for entry in it:
        print("scandir:", entry.name, "dir" if entry.is_dir() else "file")

(BASE / "print_out.txt").unlink()                # delete file (os.remove also works)
(BASE / "sub" / "deep" / "moved.txt").unlink()
(BASE / "sub" / "deep").rmdir()                  # remove EMPTY dir
shutil.rmtree(BASE / "sub")                      # remove dir tree


# 10. FILE METADATA
section("10. Metadata")
st = os.stat(BASE / "notes.txt")
print("size:", st.st_size, "bytes | modified:", st.st_mtime)
print("exists:", os.path.exists(BASE / "notes.txt"),
      "| isfile:", os.path.isfile(BASE / "notes.txt"),
      "| isdir:", os.path.isdir(BASE))
print("abspath:", os.path.abspath(BASE / "notes.txt"))
print("split ext:", os.path.splitext("report.final.pdf"))
print("shutil.disk_usage:", shutil.disk_usage("."))


# 11. TEMPORARY FILES
section("11. Temp files")
with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=True) as tmp:
    tmp.write("temporary")
    tmp.seek(0)
    print(tmp.read(), "->", tmp.name)
with tempfile.TemporaryDirectory() as tmpdir:
    print("temp dir:", tmpdir)


# 12. ZIP ARCHIVES
section("12. Zip")
with zipfile.ZipFile(BASE / "archive.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(BASE / "notes.txt", arcname="notes.txt")
    z.writestr("inline.txt", "created inside zip")
with zipfile.ZipFile(BASE / "archive.zip") as z:
    print(z.namelist())
    z.extractall(BASE / "unzipped")
shutil.make_archive(str(BASE / "backup"), "zip", BASE / "unzipped")  # whole folder


# 13. ERROR HANDLING
section("13. Error handling")
for path in ["missing.txt", BASE]:
    try:
        with open(path) as f:
            f.read()
    except FileNotFoundError:
        print(f"{path}: not found")
    except IsADirectoryError:
        print(f"{path}: is a directory")
    except PermissionError:
        print(f"{path}: permission denied")
    except OSError as e:
        print("other OS error:", e)


# 14. ENCODING
section("14. Encoding")
with open(BASE / "utf8.txt", "w", encoding="utf-8") as f:
    f.write("héllo – 你好 ✓")
with open(BASE / "utf8.txt", encoding="utf-8") as f:
    print(f.read())
with open(BASE / "bad.txt", "wb") as f:
    f.write(b"caf\xe9")                                   # latin-1 bytes, invalid utf-8
with open(BASE / "bad.txt", encoding="utf-8", errors="replace") as f:
    print(f.read())                                       # errors: strict/ignore/replace


# 15. MISC
section("15. Misc: flush, in-memory files, atomic write")
import io
buf = io.StringIO()                  # file-like object in memory
buf.write("in memory")
print(buf.getvalue())
bio = io.BytesIO(b"bytes in memory")
print(bio.read())

def atomic_write(path, text):
    """Write to temp file then rename, so readers never see half-written data."""
    path = Path(path)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as tmp:
        tmp.write(text)
        tmp.flush()
        os.fsync(tmp.fileno())       # force to disk
    os.replace(tmp.name, path)       # atomic on same filesystem

atomic_write(BASE / "atomic.txt", "safe write\n")

with open(BASE / "buffered.txt", "w") as f:
    f.write("flush me")
    f.flush()                        # push Python buffer to OS

print("\nDone. Delete the demo folder with: shutil.rmtree('io_demo')")
