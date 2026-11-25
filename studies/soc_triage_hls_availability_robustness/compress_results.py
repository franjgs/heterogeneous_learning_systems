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
            if args.delete_originals: source.unlink()
    for d in args.directories:
        for path in sorted(d.rglob("*")):
            if not path.is_file() or path.name=="artifact_manifest.json" or path.suffix==".csv":
                continue
            if any(part.startswith("shard") for part in path.relative_to(d).parts):
                continue
            if path.suffix not in {".gz",".json",".png",".svg"}:
                continue
            h=hashlib.sha256()
            with path.open("rb") as stream:
                for block in iter(lambda:stream.read(1024*1024),b""): h.update(block)
            entries.append({"path":str(path),"sha256":h.hexdigest(),"bytes":path.stat().st_size})
    manifest={"format":"gzip CSV, deterministic mtime=0","code_commit":args.code_commit,"files":entries}
    for d in args.directories:
        (d/"artifact_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(f"compressed {len(entries)} CSV files; manifest written")

if __name__=="__main__": main()
