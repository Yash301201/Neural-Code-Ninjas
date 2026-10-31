"""Download and validate the public Kaggle OULAD archive; never execute archive files."""
import argparse,urllib.request,zipfile
from pathlib import Path
from .import_oulad import csv_members

URL='https://www.kaggle.com/api/v1/datasets/download/rocki37/open-university-learning-analytics-dataset'
def main():
    p=argparse.ArgumentParser();p.add_argument('--force',action='store_true');args=p.parse_args()
    target=Path(__file__).resolve().parents[1]/'data/oulad/raw/oulad.zip'
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and not args.force:
        with zipfile.ZipFile(target) as z:csv_members(z)
        print('Validated existing OULAD archive; download skipped.');return
    partial=target.with_suffix('.zip.part')
    request=urllib.request.Request(URL,headers={'User-Agent':'LearnPathAI-OULAD-Importer/1.0'})
    with urllib.request.urlopen(request,timeout=120) as response,partial.open('wb') as output:
        size=0
        while True:
            chunk=response.read(1024*1024)
            if not chunk:break
            output.write(chunk);size+=len(chunk)
            if size%(16*1024*1024)==0:print('Downloaded',size//(1024*1024),'MiB',flush=True)
    with zipfile.ZipFile(partial) as z:csv_members(z)
    partial.replace(target)
    print('Validated Kaggle OULAD archive saved:',target)
if __name__=='__main__':main()
