from pathlib import Path
import hashlib
import json

path=Path('WIREFRAME/index.html')
text=path.read_text(encoding='utf-8')
replacements={
    ",checkoutInspectionPending=checkoutInspectionPending(no),blocked=":",inspectionPending=checkoutInspectionPending(no),blocked=",
    "available=!occupied&&!cleaningNeeded&&!checkoutInspectionPending&&!blocked;":"available=!occupied&&!cleaningNeeded&&!inspectionPending&&!blocked;",
    ",checkoutInspectionPending,blocked,blockers,available,conflict,":",checkoutInspectionPending:inspectionPending,blocked,blockers,available,conflict,",
}
for old,new in replacements.items():
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'room facet runtime compatibility mismatch for {old!r}: {count}')
    text=text.replace(old,new,1)
path.write_text(text,encoding='utf-8')

digest=hashlib.sha256(path.read_bytes()).hexdigest()
sums_path=Path('SHA256SUMS.txt')
lines=sums_path.read_text(encoding='utf-8').splitlines()
found=False
for index,line in enumerate(lines):
    if line.endswith('  WIREFRAME/index.html'):
        lines[index]=f'{digest}  WIREFRAME/index.html';found=True
if not found:raise SystemExit('WIREFRAME checksum line missing after runtime compatibility patch')
sums_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
manifest_path=Path('manifest.json')
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest.setdefault('sha256',{})['WIREFRAME/index.html']=digest
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
