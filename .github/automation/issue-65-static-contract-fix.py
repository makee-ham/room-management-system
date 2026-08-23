from pathlib import Path

path = Path('scripts/check-workspace.mjs')
text = path.read_text(encoding='utf-8')

photo_old = '''const fieldCompleteSource = html.slice(html.indexOf("if(a==='field-complete-v2')"), html.indexOf("if(a==='approve-inspection-v2')"));
if (fieldCompleteSource.includes('req.checked') || !fieldCompleteSource.includes('!req.requiredDone||req.failed') || !fieldCompleteSource.includes('checklist:{}')) {
  throw new Error('Maid completion/submission is not exclusively gated by required photo status.');
}'''
photo_new = '''const fieldCompleteSource = html.slice(html.indexOf("if(a==='field-complete-v2')"), html.indexOf("if(a==='approve-inspection-v2')"));
const delegatedSubmissionStart = html.indexOf('function createCleaningSubmissionRecord');
const delegatedSubmissionEnd = html.indexOf('function activeBombRoomReport', delegatedSubmissionStart);
const delegatedSubmissionSource = delegatedSubmissionStart >= 0 && delegatedSubmissionEnd > delegatedSubmissionStart ? html.slice(delegatedSubmissionStart, delegatedSubmissionEnd) : '';
const submissionStoresEmptyChecklist = fieldCompleteSource.includes('checklist:{}') || fieldCompleteSource.includes('createCleaningSubmissionRecord(id)') && delegatedSubmissionSource.includes('checklist:{}');
if (fieldCompleteSource.includes('req.checked') || !fieldCompleteSource.includes('!req.requiredDone||req.failed') || !submissionStoresEmptyChecklist) {
  throw new Error('Maid completion/submission is not exclusively gated by required photo status.');
}'''
count = text.count(photo_old)
if count != 1:
    raise SystemExit(f'photo-only delegated submission checker mismatch: {count}')
text = text.replace(photo_old, photo_new, 1)

completion_old = '''const submitCleaningStart = html.indexOf("if(a==='submit-cleaning-v2')");
const submitCleaningEnd = html.indexOf("if(a==='approve-inspection-v2')", submitCleaningStart);
const submitCleaningSource = html.slice(submitCleaningStart, submitCleaningEnd);
if (submitCleaningStart < 0 || !submitCleaningSource.includes('`${state.selectedDate} ${state.time}`') || !/weekStartIso\\([^)]*completedAt/.test(submitCleaningSource)) {
  throw new Error('Cleaning submission time and payroll week must derive from actual completion, not the original plan date.');
}'''
completion_new = '''const submitCleaningStart = html.indexOf("if(a==='submit-cleaning-v2')");
const submitCleaningEnd = html.indexOf("if(a==='approve-inspection-v2')", submitCleaningStart);
const submitCleaningSource = html.slice(submitCleaningStart, submitCleaningEnd);
const submissionCompletionSource = `${submitCleaningSource}${delegatedSubmissionSource}`;
if (submitCleaningStart < 0 || !submissionCompletionSource.includes('`${state.selectedDate} ${state.time}`') || !/weekStartIso\\([^)]*completedAt/.test(submissionCompletionSource)) {
  throw new Error('Cleaning submission time and payroll week must derive from actual completion, not the original plan date.');
}'''
count = text.count(completion_old)
if count != 1:
    raise SystemExit(f'completion-time delegated submission checker mismatch: {count}')
text = text.replace(completion_old, completion_new, 1)

path.write_text(text, encoding='utf-8')
