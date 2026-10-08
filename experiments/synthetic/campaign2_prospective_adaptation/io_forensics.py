"""Read-only, scope-filtered decoding of local Drive structured I/O records.

No HLS state, seed, physics, inference or scientific analysis is involved.
Only generic protobuf wire fields are decoded; no event-name schema is guessed.
"""
import struct
import argparse
from datetime import datetime, timezone
from pathlib import Path
import zipfile


def varint(data, offset):
    value=0; shift=0
    while offset<len(data) and shift<70:
        byte=data[offset];offset+=1;value|=(byte&127)<<shift
        if byte<128:return value,offset
        shift+=7
    raise ValueError("invalid varint")


def fields(data):
    result=[];offset=0
    while offset<len(data):
        key,offset=varint(data,offset);number,wire=key>>3,key&7
        if number==0:raise ValueError("invalid protobuf field")
        if wire==0:value,offset=varint(data,offset)
        elif wire==2:
            length,offset=varint(data,offset)
            value=data[offset:offset+length];offset+=length
        elif wire in (1,5):
            length=8 if wire==1 else 4
            value=data[offset:offset+length];offset+=length
        else:raise ValueError("unsupported protobuf wire type")
        if offset>len(data):raise ValueError("truncated protobuf field")
        result.append((number,wire,value))
    return result


def records(data):
    offset=0
    while offset<len(data):
        if offset+4>len(data):raise ValueError("truncated frame")
        length=struct.unpack_from("<I",data,offset)[0]
        start=offset+4;end=start+length
        if end>len(data):raise ValueError("truncated record")
        yield start,data[start:end]
        offset=end


def describe(data,depth=0):
    for number,wire,value in fields(data):
        prefix="  "*depth+f"field={number} wire={wire}"
        if wire==0:
            suffix=""
            if 1700000000000000<value<1900000000000000:
                suffix=" UTC="+datetime.fromtimestamp(value/1e6,timezone.utc).isoformat()
            print(prefix,value,suffix)
        elif wire==2:
            if b"campaign2_prospective_adaptation" in value or b".tmp.drivedownload" in value:
                if value.startswith(b"/"):
                    print(prefix,value.decode("utf-8","replace"))
                elif depth<3:
                    print(prefix,"nested",len(value));describe(value,depth+1)
            elif depth<2:
                try:nested=fields(value)
                except ValueError:continue
                if nested:
                    print(prefix,"nested",len(value));describe(value,depth+1)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("source",type=Path,help="local structured-log ZIP; never copied into repository")
    source=parser.parse_args().source
    with zipfile.ZipFile(source) as z:data=z.read(z.namelist()[0])
    for offset,record in records(data):
        if b"results/campaigns/campaign2_prospective_adaptation/" in record:
            print("RECORD",offset,"bytes",len(record))
            describe(record)
