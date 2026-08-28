from pathlib import Path

path = Path('.github/automation/apply-demo-date-all-maid-availability.py')
text = path.read_text(encoding='utf-8')

product_marker = '''replace_once(old_availability_notice, new_availability_notice, "availability notification fixture")
'''
product_insert = r'''

replace_once(
    """function renderAvailabilityMatrix() {
        const start=weekStartIso(state.assignmentDate),days=""",
    """function renderAvailabilityMatrix() {
        const start='2026-08-17',days=""",
    "workforce fixed next-week matrix",
)
'''
if text.count(product_marker) != 1:
    raise SystemExit(f'workforce product insertion marker mismatch: {text.count(product_marker)}')
if 'workforce fixed next-week matrix' in text:
    raise SystemExit('workforce fixed-week patch already inserted unexpectedly')
text = text.replace(product_marker, product_marker + product_insert, 1)

checker_marker = """console.log('All-maid availability and work-history fixture contracts: passed');
"""
checker_insert = r'''const workforceMatrixStart = html.indexOf('function renderAvailabilityMatrix()');
if (workforceMatrixStart < 0) throw new Error('Workforce availability matrix source could not be isolated.');
const workforceMatrixSource = html.slice(workforceMatrixStart, workforceMatrixStart + 5000);
if (!workforceMatrixSource.includes("const start='2026-08-17'")) {
  throw new Error('Workforce matrix must stay on the submitted 2026-08-17 next-week schedule.');
}
if (workforceMatrixSource.includes('weekStartIso(state.assignmentDate)')) {
  throw new Error('Workforce matrix must not drift with the cleaning assignment date.');
}
console.log('All-maid availability and work-history fixture contracts: passed');
'''
if text.count(checker_marker) != 1:
    raise SystemExit(f'workforce checker insertion marker mismatch: {text.count(checker_marker)}')
text = text.replace(checker_marker, checker_insert, 1)

path.write_text(text, encoding='utf-8')
