// Generated from backend PR #166 exact source 84cf863; production regeneration pending.
// Runtime configuration remains OFF. Do not edit generated types.
export type PublishCleaningTemplateRequest = {
  roomTypeCode: CleaningTemplateRoomTypeCode;
  cleaningKind: "checkout";
  expectedVersion: number;
  durationMinutes?: number | null | undefined;
  slots: Array<CleaningTemplateSlot>;
};

export type PublishedCleaningTemplate = {
  id: string;
  version: number;
  status: "published";
  durationMinutes: number | null;
  slots: Array<CleaningTemplateSlot>;
  publishedAt: string;
  createdAt: string;
};

export type CleaningTemplateRoomTypeState = {
  roomTypeCode: CleaningTemplateRoomTypeCode;
  roomTypeName: string;
  cleaningKind: "checkout";
  configured: boolean;
  expectedVersion: number;
  currentPublished: PublishedCleaningTemplate | null;
};

export type AttemptExecutionRequest = {
  expectedExecutionVersion: number;
  expectedAssignmentId: string;
  expectedAssignmentRevision: number;
};

export type AttemptExecution = {
  attemptId: string;
  cleaningTargetId: string;
  assignmentId: string;
  maidProfileId: string;
  assignmentRevision: number;
  executionVersion: number;
  status: "scheduled" | "in_progress" | "field_completed" | "upload_pending" | "submitted" | "approved" | "rejected" | "interrupted" | "superseded";
  startedAt: string | null;
  fieldCompletedAt: string | null;
  endedAt: string | null;
  effectiveAt: string;
  recordedAt: string;
};

export type Assignment = {
  assignmentId: string;
  cleaningTargetId: string;
  roomId: string | null;
  roomNumber: string | null;
  maidProfileId: string;
  maidDisplayName: string;
  serviceDate: string;
  sequenceNumber: number;
  revision: number;
  isCurrent: boolean;
  targetAssignmentVersion: number;
  availableFrom: string | null;
  dueAt: string | null;
  notifiedAt: string | null;
  endedAt: string | null;
  createdAt: string;
};

export type CheckoutIncidentReportRequest = {
  expectedExecutionVersion: number;
  expectedAssignmentId: string;
  expectedAssignmentRevision: number;
};

export type CheckoutIncidentDecisionRequest = {
  expectedVersion: number;
  expectedImpactFingerprint: string;
  decision: "EXTEND_CHECKOUT" | "CONFIRM_DEPARTED" | "FALSE_REPORT";
  reasonCode: "GUEST_STILL_PRESENT_EXTENDED" | "GUEST_DEPARTURE_CONFIRMED" | "REPORT_FALSE_CONFIRMED";
  newCheckoutAt: string | null;
  reassignment: CheckoutIncidentReassignment;
};

export type CheckoutIncidentEnvelope = {
  incident: CheckoutIncident;
};

export type CleaningTemplateRoomTypeCode = "standard" | "premium" | "oceanPremium" | "oceanFamily";

export type CleaningTemplateSlot = {
  slotKey: string;
  displayOrder: number;
  required: boolean;
  label: string;
  description?: string;
  section?: string;
  instanceKey?: string;
};

export type CheckoutIncidentReassignment = {
  maidProfileId: string;
  sequenceNumber: number;
  serviceDate: string;
  availableFrom: string;
  dueAt: string;
};

export type CheckoutIncident = {
  incidentId: string;
  reservationId: string;
  roomId: string;
  cleaningTargetId: string;
  assignmentId: string;
  attemptId: string;
  reportedBy: string;
  reasonCode: "GUEST_STILL_PRESENT";
  status: "open" | "resolved";
  version: number;
  impactFingerprint: string;
  reportedAt: string;
  resolvedAt?: string | null;
  currentDecisionId?: string | null;
  decision?: CheckoutIncidentDecision | null;
};

export type CheckoutIncidentDecision = {
  decisionId: string;
  incidentId: string;
  incidentVersion: number;
  decision: "EXTEND_CHECKOUT" | "CONFIRM_DEPARTED" | "FALSE_REPORT";
  reasonCode: string;
  decidedBy: string;
  decidedAt: string;
  newCheckoutAt?: string;
  nextAssignmentId: string;
  nextAttemptId?: string;
};

