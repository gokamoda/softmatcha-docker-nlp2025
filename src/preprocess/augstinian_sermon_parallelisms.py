import re
from glob import glob
from pathlib import Path


def main():
    """run
    git clone https://github.com/Mythologos/Augustinian-Sermon-Parallelisms.git
    before running this function
    """

    save_path = Path("corpora/augustinian-sermon-parallelisms.txt")
    if save_path.exists():
        return

    files = glob("Augustinian-Sermon-Parallelisms/data/original/*.txt")

    def extract_number(filename):
        return int(Path(filename).stem)

    files = sorted([f for f in files], key=extract_number)
    pattern_remove_header = re.compile(r"<\d+ \d+>\n")
    with open(save_path, "w") as fo:
        for file in files:
            with open(file) as fi:
                text = fi.read()
                text = pattern_remove_header.sub("\n", text)
                fo.write(text)
                fo.write("\n")


if __name__ == "__main__":
    main()
    print("Done")
