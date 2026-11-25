"""Create deterministic gzip CSV artifacts and a SHA-256 manifest."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, shutil
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("directories",nargs="+",type=Path)
    p.add_argument("--delete-originals",action="store_true")
    p.add_argument("--code-commit",default="")
    args=p.parse_args()
    entries=[]
    for d in args.directories:
        if not d.exists(): raise FileNotFoundError(d)
        for source in sorted(d.glob("*.csv")):
            target=source.with_suffix(source.suffix+".gz")
            with source.open("rb") as inp, target.open("wb") as raw:
                with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0,compresslevel=9) as out:
                    shutil.copyfileobj(inp,out)
            digest=hashlib.sha256(target.read_bytes()).hexdigest()
            entries.append({"path":str(target),"sha256":digest,"bytes":target.stat().st_size,
                            "uncompressed_bytes":source.stat().st_size})
            if args.delete_originals: source.unlink()
    manifest={"format":"gzip CSV, deterministic mtime=0","code_commit":args.code_commit,"files":entries}
    for d in args.directories:
        (d/"artifact_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(f"compressed {len(entries)} CSV files; manifest written")

if __name__=="__main__": main()
