from pathlib import Path

path = Path('scripts/check-workspace.mjs')
text = path.read_text(encoding='utf-8')
old = '''const fieldCompleteSource = html.slice(html.indexOf("if(a==='field-complete-v2')"), html.indexOf("if(a==='approve-inspection-v2')"));
if (fieldCompleteSource.includes('req.checked') || !fieldCompleteSource.includes('!req.requiredDone||req.failed') || !fieldCompleteSource.includes('checklist:{}')) {
  throw new Error('Maid completion/submission is not exclusively gated by required photo status.');
}'''
new = '''const fieldCompleteSource = html.slice(html.indexOf("if(a==='field-complete-v2')"), html.indexOf("if(a==='approve-inspection-v2')"));
const delegatedSubmissionStart = html.indexOf('function createCleaningSubmissionRecord');
const delegatedSubmissionEnd = html.indexOf('function activeBombRoomReport', delegatedSubmissionStart);
const delegatedSubmissionSource = delegatedSubmissionStart >= 0 && delegatedSubmissionEnd > delegatedSubmissionStart ? html.slice(delegatedSubmissionStart, delegatedSubmissionEnd) : '';
const submissionStoresEmptyChecklist = fieldCompleteSource.includes('checklist:{}') || fieldCompleteSource.includes('createCleaningSubmissionRecord(id)') && delegatedSubmissionSource.includes('checklist:{}');
if (fieldCompleteSource.includes('req.checked') || !fieldCompleteSource.includes('!req.requiredDone||req.failed') || !submissionStoresEmptyChecklist) {
  throw new Error('Maid completion/submission is not exclusively gated by required photo status.');
}'''
count = text.count(old)
if count != 1:
    raise SystemExit(f'photo-only delegated submission checker mismatch: {count}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
