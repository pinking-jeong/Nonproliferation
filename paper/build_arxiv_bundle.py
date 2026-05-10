"""Build a clean arXiv submission tarball from the paper directory.

arXiv accepts either a tarball (preferred) or a zip. We produce both,
along with a compiled PDF for cross-checking, in a sibling
``arxiv_submission/`` directory.

Usage (from ``ospm/paper/`` or repo root):

    python build_arxiv_bundle.py

Output:

    arxiv_submission/
        os-pm-arxiv-v1.tar.gz       # canonical submission
        os-pm-arxiv-v1.zip          # portable alternative
        os-pm-arxiv-v1.pdf          # compiled cross-check
        manifest.txt                # listed files
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import tarfile
import zipfile
from datetime import date
from pathlib import Path

# Files that arXiv expects in the bundle. Anything else is excluded.
INCLUDE_GLOBS = (
    "main.tex",
    "references.bib",
)
INCLUDE_DIRS_OPTIONAL = (
    "figures",   # optional; produced if any
)
# Files that must NOT end up in the bundle even if present.
EXCLUDE_PATTERNS = (
    "main.aux", "main.log", "main.out", "main.toc",
    "main.bbl", "main.blg", "main.fls", "main.fdb_latexmk",
    "main.synctex.gz", "main.xdv", "main.pdf",
    "Makefile", "README.md", "ARXIV_METADATA.md", "build_arxiv_bundle.py",
)


def _project_root() -> Path:
    here = Path(__file__).resolve().parent
    if here.name == "paper":
        return here
    # If invoked from repo root, find paper dir
    candidate = here / "paper"
    if candidate.exists():
        return candidate
    raise RuntimeError("Could not locate paper directory")


def _compile_pdf(paper_dir: Path) -> Path | None:
    """Run latexmk to ensure the final PDF compiles before bundling."""
    try:
        subprocess.run(
            ["latexmk", "-pdf", "-xelatex", "-interaction=nonstopmode",
             "-halt-on-error", "main.tex"],
            cwd=paper_dir,
            check=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"[warn] latexmk did not produce PDF: {e}")
        return None
    pdf = paper_dir / "main.pdf"
    return pdf if pdf.exists() else None


def _files_to_include(paper_dir: Path) -> list[Path]:
    """Resolve the explicit include list; ignore anything in EXCLUDE_PATTERNS."""
    out: list[Path] = []
    for name in INCLUDE_GLOBS:
        p = paper_dir / name
        if p.exists() and p.name not in EXCLUDE_PATTERNS:
            out.append(p)
    for d in INCLUDE_DIRS_OPTIONAL:
        dir_path = paper_dir / d
        if dir_path.is_dir():
            for f in sorted(dir_path.rglob("*")):
                if f.is_file() and f.name not in EXCLUDE_PATTERNS:
                    out.append(f)
    return out


def build(out_dir: Path, version: str = "v1") -> dict[str, Path]:
    paper_dir = _project_root()
    print(f"[info] paper dir: {paper_dir}")
    pdf = _compile_pdf(paper_dir)

    files = _files_to_include(paper_dir)
    if not files:
        raise RuntimeError("No files matched the include list — nothing to bundle.")

    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    base = f"os-pm-arxiv-{version}-{today}"
    tar_path = out_dir / f"{base}.tar.gz"
    zip_path = out_dir / f"{base}.zip"
    manifest_path = out_dir / "manifest.txt"

    with tarfile.open(tar_path, "w:gz") as tf:
        for f in files:
            arcname = f.relative_to(paper_dir).as_posix()
            tf.add(f, arcname=arcname)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            arcname = f.relative_to(paper_dir).as_posix()
            zf.write(f, arcname=arcname)

    manifest_lines: list[str] = []
    manifest_lines.append(f"# OS-PM arXiv bundle manifest — {today}")
    manifest_lines.append(f"# Version: {version}")
    manifest_lines.append(f"# Source dir: {paper_dir}")
    manifest_lines.append(f"# Files included: {len(files)}")
    for f in files:
        manifest_lines.append(f.relative_to(paper_dir).as_posix())
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    if pdf is not None:
        shutil.copy2(pdf, out_dir / f"{base}.pdf")

    print(f"[info] wrote {tar_path.name}, {zip_path.name}, manifest.txt")
    if pdf is not None:
        print(f"[info] cross-check PDF: {base}.pdf")
    return {"tar": tar_path, "zip": zip_path, "manifest": manifest_path}


def main():
    p = argparse.ArgumentParser(description="Build arXiv submission bundle")
    p.add_argument("--out", default="arxiv_submission",
                   help="Output directory (default: arxiv_submission/)")
    p.add_argument("--version", default="v1", help="Version tag")
    args = p.parse_args()
    paper_dir = _project_root()
    out = (paper_dir.parent / args.out).resolve()
    build(out, version=args.version)
    print("[done] bundle ready under:", out)


if __name__ == "__main__":
    main()
