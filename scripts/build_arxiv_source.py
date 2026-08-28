from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "physical_source_submission_source"
OUT = ROOT / "arxiv_submission_source.zip"


def main():
    members = [SOURCE / "main.tex", SOURCE / "refs.bib"]
    members.extend(sorted((SOURCE / "figures").glob("*.pdf")))
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in members:
            zf.write(path, path.relative_to(SOURCE))
    print(f"WROTE {OUT}")


if __name__ == "__main__":
    main()
