import { createHash } from 'node:crypto';

// An intentional backend contract transition is valid only for its exact reviewed documents.
// All other differences, including changes on the same endpoint, retain the normal CI failure.
export function partitionReviewedChanges(baseText,currentText,differences,reviews){
  const digest=text=>createHash('sha256').update(text).digest('hex');
  const baseSha256=digest(baseText),currentSha256=digest(currentText);
  const allowed=new Set(reviews.filter(review=>review.baseSha256===baseSha256&&review.currentSha256===currentSha256).flatMap(review=>review.changes));
  return {reviewed:differences.filter(change=>allowed.has(change)),unreviewed:differences.filter(change=>!allowed.has(change))};
}
