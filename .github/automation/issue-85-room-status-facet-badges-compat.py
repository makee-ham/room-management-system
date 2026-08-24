from pathlib import Path

path=Path('scripts/check-workspace.mjs')
text=path.read_text(encoding='utf-8')
old="  'data-checkout-inspection-facet',"
new="  'card.dataset.checkoutInspectionFacet',"
if text.count(old)!=1:
    raise SystemExit(f'facet checker compatibility marker mismatch: {text.count(old)}')
path.write_text(text.replace(old,new,1),encoding='utf-8')
