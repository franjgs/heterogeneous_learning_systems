"""Verified CSV publication: private staging, closed files, atomic rename.

Do not hold writable descriptors to public files inside a synchronized tree
while scientific computation is in progress. No model/analysis logic here.
"""
from contextlib import ExitStack
import csv
import gzip
import hashlib
import io
import os
from pathlib import Path
import shutil
import tempfile


def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()


def inspect_csv(path):
    if path.stat().st_size==0:raise IOError(f"empty artifact: {path}")
    opener=gzip.open if path.name.endswith(".gz") else open
    with opener(path,"rt",encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        fields=reader.fieldnames
        if not fields:raise IOError(f"missing CSV header: {path}")
        count=0
        for row in reader:
            if None in row:raise IOError(f"CSV schema mismatch: {path}")
            count+=1
    if count==0:raise IOError(f"no data rows: {path}")
    return dict(rows=count,sha256=sha256(path),bytes=path.stat().st_size,fields=fields)


def persist_tables(batches,destination,filenames):
    """Consume unchanged row dictionaries, verify locally, then publish/reload.

    Full private paths are outside the mirrored workspace. Public paths are
    never opened for a long-running write. A post-publication rewrite/truncation
    is a hard I/O failure, never a successful completion based on counters.
    """
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    for filename in filenames.values():
        if (destination/filename).exists():raise FileExistsError(destination/filename)
    counts=dict.fromkeys(filenames,0)
    with tempfile.TemporaryDirectory(prefix="hls-c2-io-",dir="/private/tmp") as directory:
        staging=Path(directory)
        with ExitStack() as stack:
            writers={}
            for name,filename in filenames.items():
                raw=stack.enter_context((staging/filename).open("wb"))
                binary=stack.enter_context(gzip.GzipFile(fileobj=raw,mode="wb",mtime=0,filename="")) if filename.endswith(".gz") else raw
                handle=stack.enter_context(io.TextIOWrapper(binary,encoding="utf-8",newline=""))
                writers[name]=(handle,None)
            for batch in batches:
                if set(batch)!=set(filenames):raise ValueError("unexpected output tables")
                for name,rows in batch.items():
                    if not rows:continue
                    handle,writer=writers[name]
                    if writer is None:
                        fields=list(dict.fromkeys(key for row in rows for key in row))
                        writer=csv.DictWriter(handle,fieldnames=fields,lineterminator="\n")
                        writer.writeheader();writers[name]=(handle,writer)
                    writer.writerows(rows);counts[name]+=len(rows)
        metadata={}
        for name,filename in filenames.items():
            source=staging/filename
            with source.open("rb") as f:os.fsync(f.fileno())
            checked=inspect_csv(source)
            if checked["rows"]!=counts[name]:raise IOError(f"row-count mismatch: {filename}")
            metadata[name]=checked
        for name,filename in filenames.items():
            # This brief copy closes and fsyncs before exposing the final path.
            with tempfile.NamedTemporaryFile(prefix=".hls-publish-",dir=destination,delete=False) as f:
                temp=Path(f.name)
                try:
                    with (staging/filename).open("rb") as source:shutil.copyfileobj(source,f)
                    f.flush();os.fsync(f.fileno())
                except BaseException:
                    temp.unlink(missing_ok=True);raise
            try:
                if sha256(temp)!=metadata[name]["sha256"]:raise IOError("publication copy corrupted")
                os.replace(temp,destination/filename)
            finally:temp.unlink(missing_ok=True)
        # Read every published path, not the old open descriptor or just counters.
        for name,filename in filenames.items():
            if inspect_csv(destination/filename)!=metadata[name]:raise IOError(f"publication changed: {filename}")
    return counts,metadata
