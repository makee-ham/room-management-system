from pathlib import Path

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
