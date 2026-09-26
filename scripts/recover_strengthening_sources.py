"""Recover official EPA source objects to private storage, without executing them."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import io
import json
from pathlib import Path
import urllib.request
from zipfile import ZipFile

MAX_DOWNLOAD = 25_000_000
MAX_MEMBER = 100_000_000
MAX_EXPANDED = 200_000_000
MAX_MEMBERS = 5000


def inventory_zip(data):
    """Bound expansion before reading; streaming also checks every member CRC."""
    with ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > MAX_MEMBERS:
            raise ValueError('too many ZIP members')
        if any(p.file_size > MAX_MEMBER for p in members):
            raise ValueError('ZIP member exceeds expansion limit')
        if sum(p.file_size for p in members) > MAX_EXPANDED:
            raise ValueError('ZIP total exceeds expansion limit')
        names = [p.filename for p in members]
        if len(names) != len(set(names)):
            raise ValueError('duplicate ZIP member names')
        records = []
        total = 0
        for member in members:
            if member.is_dir():
                continue
            digest = sha256()
            count = 0
            with archive.open(member) as stream:
                while chunk := stream.read(65536):
                    count += len(chunk)
                    total += len(chunk)
                    if count > MAX_MEMBER or total > MAX_EXPANDED:
                        raise ValueError('actual ZIP expansion exceeds limit')
                    digest.update(chunk)
            if count != member.file_size:
                raise ValueError('ZIP declared and actual sizes differ')
            records.append({'name': member.filename, 'bytes': count,
                            'sha256': digest.hexdigest()})
        return records

URLS = {
    'sjvf_data.zip':'https://www.epa.gov/sites/default/files/2020-10/sjvf_data.zip',
    'pacs_data.zip':'https://www.epa.gov/sites/default/files/2020-10/pacs_data.zip',
    'epa-cmb82test.zip':'https://www.epa.gov/sites/production/files/2020-10/epa-cmb82test.zip',
    'sourcecmb82.zip':'https://www.epa.gov/sites/production/files/2020-10/sourcecmb82.zip',
}

def recover(item, raw):
    name,url=item
    record={'name':name,'url':url,'landing_page':'https://www.epa.gov/scram/chemical-mass-balance-cmb-model'}
    try:
        request=urllib.request.Request(url,headers={'User-Agent':'PFFLS reproducibility audit'})
        with urllib.request.urlopen(request,timeout=40) as response:
            data=response.read(MAX_DOWNLOAD+1)
            record['http_status']=response.status
            record['final_url']=response.url
        if len(data)>MAX_DOWNLOAD: raise ValueError('source exceeds bounded download size')
        record['members'] = inventory_zip(data)
        target=raw/name
        if target.exists() and target.read_bytes()!=data: raise ValueError('different existing source bytes; refuse overwrite')
        target.write_bytes(data)
        record.update(status='RECOVERED',bytes=len(data),sha256=sha256(data).hexdigest(),raw_redistributed=False,executed=False)
    except Exception as e:
        record.update(status='NOT_RECOVERED',error_type=type(e).__name__,detail=str(e))
    return record

def main():
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    repo=Path(__file__).resolve().parents[1]
    raw=a.raw_dir.resolve()
    if raw.is_relative_to(repo) and not raw.is_relative_to(repo/'private'):
        raise SystemExit('Raw inputs must be outside the repository or under gitignored private/.')
    raw.mkdir(parents=True,exist_ok=True)
    records=list(ThreadPoolExecutor(max_workers=4).map(lambda item:recover(item,raw),URLS.items()))
    result={'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'purpose':'Source recovery and identity only; not an original-results reproduction','records':records}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{'name':r['name'],'status':r['status'],'sha256':r.get('sha256'),'members':len(r.get('members',[]))} for r in records],indent=2))
if __name__=='__main__':main()
