// Generated from the canonical OpenAPI v0.4.0.
// Do not edit generated types directly.
export type ErrorCode = "VALIDATION_ERROR" | "INVALID_PHONE" | "REQUEST_TOO_LARGE" | "MISSING_ACCESS_TOKEN" | "INVALID_ACCESS_TOKEN" | "PROFILE_NOT_FOUND" | "ACCOUNT_INACTIVE" | "ACCOUNT_EXECUTION_LIFECYCLE_REQUIRED" | "ATTEMPT_ACCESS_REQUIRED" | "ATTEMPT_NOT_FOUND" | "ATTEMPT_VERSION_CONFLICT" | "ASSIGNMENT_NOT_NOTIFIED" | "ATTEMPT_INVALID_TRANSITION" | "MAID_ALREADY_IN_PROGRESS" | "ATTEMPT_COMMAND_FAILED" | "CAPABILITY_ACCESS_REQUIRED" | "PHOTO_RETENTION_DELETE_PREPARED" | "ACCOUNT_VERSION_CONFLICT" | "CLEANING_WINDOW_NOT_EXPIRED" | "ASSIGNMENT_SCHEDULE_INVALID" | "ROLLOVER_NOT_ALLOWED" | "INVALID_ATTEMPT_COMMAND" | "ATTEMPT_ACTIVATION_NOT_ALLOWED" | "CLEANING_SERVICE_DATE_NOT_DUE" | "CLEANING_SERVICE_DATE_EXPIRED" | "CLEANING_WINDOW_NOT_OPEN" | "CLEANING_WINDOW_EXPIRED" | "CHECKOUT_NOT_MATERIALIZED" | "RECLEAN_MAID_IMMUTABLE" | "PREVIOUS_ROOM_WORKFLOW_ACTIVE" | "SESSION_REVOKED" | "INVALID_CREDENTIALS" | "ACCOUNT_LOCKED" | "LOGIN_RATE_LIMITED" | "LOGIN_CLIENT_ID_UNAVAILABLE" | "LOGIN_RATE_LIMIT_UNAVAILABLE" | "ACTIVITY_LOG_UNAVAILABLE" | "AUTH_LOOKUP_FAILED" | "LOGIN_STATE_UPDATE_FAILED" | "INVALID_CURRENT_PASSWORD" | "AUTH_PASSWORD_CHANGE_FAILED" | "PASSWORD_STATE_INCONSISTENT" | "PASSWORD_STATE_UPDATE_FAILED" | "PASSWORD_CHANGE_RECEIPT_FAILED" | "PASSWORD_CHANGE_IN_PROGRESS" | "PASSWORD_CHANGE_SESSION_MISMATCH" | "PASSWORD_VERIFICATION_RATE_LIMITED" | "PASSWORD_VERIFICATION_RATE_LIMIT_UNAVAILABLE" | "PASSWORD_VERIFICATION_SESSION_REVOKE_FAILED" | "PASSWORD_RESET_STATE_UPDATE_FAILED" | "PASSWORD_CHANGE_REQUIRED" | "ACCOUNT_MANAGER_REQUIRED" | "ADMIN_REQUIRED" | "ASSIGNMENT_ACCESS_REQUIRED" | "DEVELOPER_REQUIRED" | "DEVELOPER_PROJECTION_FAILED" | "DATABASE_UNREACHABLE" | "MIGRATION_DRIFT" | "RLS_CONFIGURATION_INVALID" | "SCHEDULER_NOT_CONFIGURED" | "SCHEDULER_ACTOR_INVALID" | "SCHEDULER_DEGRADED" | "SCHEDULER_HEARTBEAT_FAILED" | "DIAGNOSTIC_TIMEOUT" | "DIAGNOSTICS_RATE_LIMITED" | "ACCOUNT_NOT_FOUND" | "DEVELOPER_ACCOUNT_PROTECTED" | "LAST_ACTIVE_ADMIN_REQUIRED" | "ACCOUNT_MUST_BE_INACTIVE" | "DEPARTED_ACCOUNT_IMMUTABLE" | "IDEMPOTENCY_KEY_REUSED" | "RESERVED_IDEMPOTENCY_KEY" | "DEACTIVATION_MUST_BE_FINISHED" | "PHONE_ALREADY_REGISTERED" | "LOGIN_ID_CONFLICT" | "PHONE_REQUIRED_FOR_RESET" | "AUTH_USER_CREATE_FAILED" | "AUTH_USER_UPDATE_FAILED" | "AUTH_PASSWORD_RESET_FAILED" | "ACCOUNT_AUTH_STATE_INCONSISTENT" | "ACCOUNT_COMMAND_FAILED" | "FORBIDDEN" | "MAID_REQUIRED" | "AVAILABILITY_ACCESS_REQUIRED" | "ACTIVE_MAID_REQUIRED" | "CLEANING_TARGET_NOT_FOUND" | "ASSIGNMENT_VERSION_CONFLICT" | "ASSIGNMENT_TARGET_STATE_INVALID" | "ASSIGNMENT_SEQUENCE_CONFLICT" | "ASSIGNMENT_NOT_FOUND" | "ASSIGNMENT_IMPACT_CHANGED" | "ASSIGNMENT_DRAFT_STALE_SCHEDULE" | "ASSIGNMENT_AVAILABILITY_REQUIRED" | "ASSIGNMENT_AVAILABILITY_STALE" | "ASSIGNMENT_MAID_UNAVAILABLE" | "ASSIGNMENT_WINDOW_EXPIRED" | "ASSIGNMENT_COMMIT_NOT_ALLOWED" | "ASSIGNMENT_COMMAND_FAILED" | "ASSIGNMENT_PREVIEW_DATE_NOT_ALLOWED" | "ASSIGNMENT_PREVIEW_DURATION_POLICY_UNCONFIRMED" | "ASSIGNMENT_PREVIEW_LIMIT_EXCEEDED" | "ASSIGNMENT_PREVIEW_FAILED" | "INVALID_ASSIGNMENT_DURATION_POLICY" | "ASSIGNMENT_DURATION_POLICY_VERSION_CONFLICT" | "ACTIVE_ADMIN_REQUIRED" | "OUTSIDE_AVAILABILITY_WINDOW" | "CHANGE_REQUEST_BEFORE_DEADLINE" | "STALE_VERSION" | "PENDING_CHANGE_REQUEST_EXISTS" | "INVALID_TRANSITION" | "AVAILABILITY_NOT_FOUND" | "CHANGE_REQUEST_NOT_FOUND" | "WEEK_START_MUST_BE_MONDAY" | "AVAILABILITY_DATES_MUST_BE_UNIQUE" | "AVAILABILITY_DATE_OUTSIDE_WEEK" | "AVAILABILITY_COMMAND_FAILED" | "INVALID_GUEST_NAME" | "INVALID_GUEST_COUNT" | "INVALID_RESERVATION_SCHEDULE" | "STANDARD_RESERVATION_REQUIRES_END" | "RESERVATION_TYPE_IMMUTABLE" | "RESERVATION_END_IMMUTABLE" | "BOOKABILITY_RANGE_TOO_LARGE" | "INVALID_ROOM_TYPE_FILTER" | "EXCLUDE_RESERVATION_NOT_FOUND" | "EXCLUDE_RESERVATION_NOT_ELIGIBLE" | "INVALID_RESERVATION_RANGE" | "RESERVATION_RANGE_TOO_LARGE" | "INVALID_RESERVATION_CURSOR" | "RESERVATION_CURSOR_NOT_CONFIGURED" | "INVALID_MOVE_EFFECTIVE_AT" | "RESERVATION_OVERLAP" | "TARGET_ROOM_OVERLAP" | "TARGET_ROOM_BLOCKED" | "TARGET_ROOM_NOT_READY" | "PIN_LEASE_ACTIVE" | "OPEN_ENDED_STAY_REQUIRES_END" | "ROOM_ALLOCATION_BLOCKED" | "RESERVATION_NOT_FOUND" | "CLEANING_REQUEST_NOT_FOUND" | "CLEANING_TEMPLATE_NOT_CONFIGURED" | "INVALID_CLEANING_TEMPLATE" | "INVALID_CLEANING_TEMPLATE_SLOTS" | "CLEANING_TEMPLATE_VERSION_CONFLICT" | "CLEANING_TEMPLATE_COMMAND_FAILED" | "INVALID_MANUAL_CLEANING_REQUEST" | "ACTIVE_STAY_RESERVATION_REQUIRED" | "STAYOVER_ACCESS_WINDOW_INVALID" | "VACANT_ROOM_REQUIRED" | "RESERVATION_ROOM_MISMATCH" | "NOT_MANUAL_CLEANING_REQUEST" | "REPLAN_REQUIRED" | "SCHEDULE_LOCKED" | "CONFLICT" | "RESERVATION_COMMAND_FAILED" | "RESERVATION_PII_KEY_INVALID" | "RESERVATION_PII_KEYRING_INVALID" | "RESERVATION_PII_DECRYPT_FAILED" | "COMPLAINT_ACCESS_REQUIRED" | "COMPLAINT_MAID_MISMATCH" | "COMPLAINT_NOT_FOUND" | "INVALID_COMPLAINT_CATEGORY" | "INVALID_COMPLAINT_FINDING" | "INVALID_COMPLAINT_PENALTY" | "INVALID_REWORK_DECISION" | "INVALID_COMPLAINT_RESPONSE" | "COMPLAINT_APPEAL_REASON_REQUIRED" | "COMPLAINT_APPEAL_REASON_FORBIDDEN" | "COMPLAINT_PERIOD_INVALID" | "COMPLAINT_PAGE_LIMIT_INVALID" | "INVALID_COMPLAINT_CURSOR" | "INVALID_COMPLAINT_REWORK" | "COMPLAINT_COMPENSATION_AMOUNT_INVALID" | "COMPLAINT_INTAKE_WINDOW_CLOSED" | "COMPLAINT_SOURCE_NOT_APPROVED" | "COMPLAINT_RESPONSE_WINDOW_CLOSED" | "COMPLAINT_RESPONSE_WINDOW_OPEN" | "COMPLAINT_APPEAL_UNRESOLVED" | "COMPLAINT_RESPONSE_ALREADY_RECORDED" | "COMPLAINT_DECISION_REQUIRED" | "COMPLAINT_REWORK_MAID_UNAVAILABLE" | "COMPLAINT_REWORK_WINDOW_UNAVAILABLE" | "COMPLAINT_REWORK_NOT_CONFIRMED" | "COMPLAINT_REWORK_ALREADY_MATERIALIZED" | "COMPLAINT_REWORK_DECISION_STALE" | "COMPLAINT_REWORK_PRESTART_FROZEN" | "RECLEAN_TEMPLATE_NOT_CONFIGURED" | "COMPLAINT_INVALID_TRANSITION" | "COMPLAINT_COMMAND_FAILED" | "NOTIFICATION_ACCESS_REQUIRED" | "NOTIFICATION_NOT_FOUND" | "INVALID_NOTIFICATION_CURSOR" | "NOTIFICATION_CURSOR_NOT_CONFIGURED" | "NOTIFICATION_RESPONSE_TOO_LARGE" | "NOTIFICATION_QUERY_FAILED" | "PAYROLL_ACCESS_REQUIRED" | "PAYROLL_MAID_NOT_FOUND" | "PAYROLL_WEEK_MUST_START_MONDAY" | "PAYROLL_PAGE_LIMIT_INVALID" | "PAYROLL_PAGE_KIND_INVALID" | "PAYROLL_CURSOR_INVALID" | "PAYROLL_CURSOR_NOT_CONFIGURED" | "PAYROLL_RESPONSE_TOO_LARGE" | "INVALID_EXPECTED_VERSION" | "PAYROLL_WEEK_NOT_CLOSED" | "PAYROLL_CYCLE_NOT_OPEN" | "NO_PAYROLL_AMOUNT" | "PAYROLL_NONPOSITIVE_REQUIRES_CARRY" | "PAYROLL_POSITIVE_REQUIRES_START" | "PAYROLL_CYCLE_ECONOMICALLY_FROZEN" | "PAYROLL_SOURCE_PAYMENT_UNCERTAIN" | "PAYROLL_SOURCE_ALREADY_REVERSED" | "PAYROLL_ROOT_ENTITLEMENT_NEGATIVE" | "STALE_ADJUSTMENT_VERSION" | "PAYROLL_LATE_EARNING_ALREADY_CARRIED" | "PAYROLL_EARNING_NOT_LATE" | "PAYROLL_LATE_CARRY_TARGET_FROZEN" | "PAYROLL_EARLIER_CARRY_PENDING" | "PAYROLL_PRIOR_LATE_EARNING_PENDING" | "PAYROLL_SOURCE_NOT_FOUND" | "PAYROLL_ADJUSTMENT_INVALID" | "PAYROLL_PAYMENT_ATTEMPT_NOT_FOUND" | "PAYROLL_PAYMENT_ATTEMPT_TERMINAL" | "PAYROLL_PAYMENT_TRANSITION_INVALID" | "PAYROLL_PAYMENT_REFERENCE_ALREADY_USED" | "PAYROLL_PAYMENT_REFERENCE_INVALID" | "PAYROLL_PAYMENT_METHOD_INVALID" | "PAYROLL_PAYMENT_REASON_INVALID" | "PAYROLL_PAYMENT_REOPEN_REASON_INVALID" | "PAYROLL_PAYMENT_RESULT_AMOUNT_MISMATCH" | "PAYROLL_COMMAND_FAILED" | "ROOM_NOT_FOUND" | "ROOM_OPERATION_NOT_FOUND" | "INVALID_ROOM_PIN" | "INVALID_PIN_BOOTSTRAP_LIMIT" | "INVALID_PIN_BOOTSTRAP" | "ROOM_PIN_BOOTSTRAP_CONFIG_INVALID" | "ROOM_PIN_BOOTSTRAP_FAILED" | "ROOM_PIN_KEY_UNAVAILABLE" | "ROOM_PIN_CRYPTO_CONFIG_INVALID" | "ROOM_PIN_DECRYPT_FAILED" | "ROOM_PIN_COMMAND_FAILED" | "STALE_PIN_VERSION" | "ROOM_NUMBER_CHANGED" | "ROOM_PIN_REISSUE_REQUIRED" | "ROOM_PIN_MISMATCH_UNRESOLVED" | "PIN_CHANGE_IN_PROGRESS_REQUIRED" | "PIN_CHANGE_IN_PROGRESS" | "PIN_CHANGE_LEASE_EXPIRED" | "PIN_CHANGE_LEASE_NOT_RESOLVABLE" | "PIN_REVEAL_AUTHORIZATION_CHANGED" | "GENERATED_PIN_REVEAL_NOT_ALLOWED" | "GENERATED_PIN_CONFIRMATION_NOT_ALLOWED" | "ROOM_PIN_UNCONFIGURED" | "ROOM_PIN_SHEET_OPERATOR_REQUIRED" | "ROOM_PIN_SHEET_NOT_CONFIGURED" | "ROOM_PIN_SHEET_OPERATION_FAILED" | "ROOM_PIN_SHEET_RESPONSE_TOO_LARGE" | "ROOM_PIN_SHEET_FULL_RESYNC_STALE" | "ROOM_PIN_SHEET_WORKER_BUSY" | "ROOM_PIN_SHEET_FULL_RESYNC_PENDING" | "ROOM_PIN_SHEET_ROOM_MASTER_INVALID" | "PIN_ACCESS_LEASE_REQUIRED" | "PIN_ENTITLEMENT_REQUIRED" | "PIN_ACCESS_REQUIRED" | "SENSITIVE_TEXT_NOT_ALLOWED" | "PIN_MATERIAL_NOT_ALLOWED" | "ROOM_COMMAND_FAILED" | "ORIGIN_NOT_ALLOWED" | "ROUTE_NOT_FOUND" | "RUNTIME_NOT_CONFIGURED" | "INTERNAL_SERVER_ERROR";

export type ErrorEnvelope = {
  error: {
  code: ErrorCode;
  message: string;
};
  requestId: string;
};

export type RoomProjection = {
  id: string;
  roomNumber: string;
  roomTypeCode: string;
  roomTypeName: string;
  elevatorZone: "A" | "B" | "C" | null;
  dataStatus: "verified" | "verification_required";
  stateVersion: number;
  evaluatedAt: string;
  reservationPhase: "none" | "upcoming" | "current";
  serverTime: string;
  occupancyStatus: RoomOccupancyStatus;
  reservationLifecycle: RoomReservationLifecycle;
  readinessStatus: RoomReadinessStatus;
  primaryDisplayStatus: RoomPrimaryDisplayStatus;
  nextReservationId: string | null;
  nextCheckInAt: string | null;
  nextCheckOutAt: string | null;
  blockingReasonCodes: Array<RoomBlockingReasonCode>;
  readinessReasonCodes: Array<RoomReadinessReasonCode>;
  occupied: boolean;
  cleaningRequired: boolean;
  candleCount: number;
  pinSyncStatus: "verified" | "mismatch" | "unconfigured";
  allocationBlocked: boolean;
  allocationReady: boolean;
  reasonCodes: Array<RoomReasonCode>;
};

export type RoomTypeCatalogItem = {
  id: string;
  code: string;
  displayName: string;
  baseCleaningFee: number;
  active: boolean;
  version: number;
  roomCount: number;
};

export type RoomTypeCatalogEnvelope = {
  items: Array<RoomTypeCatalogItem>;
};

export type Reservation = {
  id: string;
  roomId: string;
  reservationType: ReservationType;
  checkInAt: string;
  checkOutAt: string | null;
  guestCount: number;
  status: ReservationStatus;
  preparationObligationId: string;
  checkoutObligationId: string | null;
  version: number;
  roomStateVersion?: number;
  actualCheckInAt: string | null;
  actualCheckoutAt: string | null;
  cancelledAt: string | null;
  createdAt: string;
  updatedAt: string;
};

export type ReservationType = "standard" | "long_stay";

export type ReservationRangePageEnvelope = {
  reservations: Array<Reservation>;
  nextCursor: string | null;
  serverTime: string;
};

export type ReservationCreateRequest = ReservationStandardCreateRequest | ReservationLongStayCreateRequest;

export type ReservationStandardCreateRequest = {
  roomId: string;
  reservationType: "standard";
  checkInAt: string;
  checkOutAt: string;
  guestCount: number;
  guestName?: string | null;
  expectedRoomVersion: number;
};

export type ReservationLongStayCreateRequest = {
  roomId: string;
  reservationType: "long_stay";
  checkInAt: string;
  checkOutAt: string | null;
  guestCount: number;
  guestName?: string | null;
  expectedRoomVersion: number;
};

export type ReservationChangeRequest = ReservationStandardChangeRequest | ReservationLongStayChangeRequest;

export type ReservationStandardChangeRequest = {
  roomId: string;
  reservationType: "standard";
  checkInAt: string;
  checkOutAt: string;
  guestCount: number;
  guestName?: string | null;
  expectedVersion: number;
  reasonCode: ReasonCode;
};

export type ReservationLongStayChangeRequest = {
  roomId: string;
  reservationType: "long_stay";
  checkInAt: string;
  checkOutAt: string | null;
  guestCount: number;
  guestName?: string | null;
  expectedVersion: number;
  reasonCode: ReasonCode;
};

export type ReservationBookabilityReasonCode = "RESERVATION_OVERLAP" | "OCCUPIED" | "RESERVATION_CURRENT" | "CLEANING_REQUIRED" | "CANDLE_PRESENT" | "OPERATION_BLOCKED" | "ROOM_ISSUE_BLOCKED" | "DATA_UNCONFIRMED" | "PIN_MISMATCH" | "PIN_UNCONFIGURED";

export type ReservationBookabilityCandidate = {
  roomId: string;
  roomNumber: string;
  roomTypeId: string;
  roomStateVersion: number;
  intervalBookable: boolean;
  checkInReady: boolean;
  reasonCodes: Array<ReservationBookabilityReasonCode>;
  evaluatedAt: string;
};

export type ReservationBookabilityPreviewRequest = ReservationBookabilityStandardPreviewRequest | ReservationBookabilityLongStayPreviewRequest;

export type ReservationBookabilityStandardPreviewRequest = {
  reservationType: "standard";
  checkInAt: string;
  checkOutAt: string;
  excludeReservationId?: string | null;
  roomTypeIds?: Array<string>;
};

export type ReservationBookabilityLongStayPreviewRequest = {
  reservationType: "long_stay";
  checkInAt: string;
  checkOutAt: string | null;
  excludeReservationId?: string | null;
  roomTypeIds?: Array<string>;
};

export type ReservationBookabilityPreview = {
  reservationType: ReservationType;
  checkInAt: string;
  checkOutAt: string | null;
  excludeReservationId: string | null;
  evaluatedAt: string;
  candidates: Array<ReservationBookabilityCandidate>;
  commitAuthority: "CREATE_OR_CHANGE_REVALIDATES";
};

export type ReservationBookabilityPreviewEnvelope = {
  preview: ReservationBookabilityPreview;
};

export type ReservationRoomMovePreviewRequest = {
  targetRoomId: string;
  effectiveAt?: string;
  reasonCode: ReservationRoomMoveReasonCode;
  expectedReservationVersion: number;
  expectedSourceRoomVersion: number;
  expectedTargetRoomVersion: number;
};

export type ReservationRoomMovePreview = {
  mode: ReservationRoomMoveMode;
  eligible: boolean;
  rejectionReasonCodes: Array<ReservationRoomMoveRejectionReasonCode>;
  blockingReasonCodes: Array<ReservationRoomMoveBlockingReasonCode>;
  warnings: Array<string>;
  targetBlockReasonCodes: Array<RoomBlockingReasonCode>;
  sourceOutcome: ReservationRoomMoveOutcome;
  targetOutcome: ReservationRoomMoveOutcome;
  impactFingerprint: string;
  evaluatedAt: string;
  expiresAt: string;
  effectiveAt: string;
  reservationId: string;
  reservationVersion: number;
  stayId: string;
  stayVersion: number;
  sourceSegmentId: string;
  sourceSegmentVersion: number;
  sourceRoomId: string;
  sourceRoomVersion: number;
  targetRoomId: string;
  targetRoomVersion: number;
  reservationType: ReservationType;
  checkInAt: string;
  checkOutAt: string | null;
  guestCount: number;
  preparationObligationId: string;
  checkoutObligationId: string | null;
  checkoutObligationVersion: number | null;
  plannedCheckoutTargetId: string | null;
  plannedCheckoutTargetVersion: number | null;
};

export type ReservationRoomMoveCommitRequest = {
  targetRoomId: string;
  expectedReservationVersion: number;
  expectedSourceRoomVersion: number;
  expectedTargetRoomVersion: number;
  evaluatedAt: string;
  expiresAt: string;
  effectiveAt: string;
  impactFingerprint: string;
  reasonCode: ReservationRoomMoveReasonCode;
};

export type ReservationRoomMoveResult = {
  reservation: Reservation;
  mode: ReservationRoomMoveMode;
  evaluatedAt: string;
  expiresAt: string;
  effectiveAt: string;
  movedAt: string;
  sourceRoomId: string;
  targetRoomId: string;
  sourceRoomVersion: number;
  targetRoomVersion: number;
  plannedCheckoutTargetId: string | null;
  plannedCheckoutTargetVersion: number | null;
  sourceOutcome: ReservationRoomMoveOutcome;
  targetOutcome: ReservationRoomMoveOutcome;
  stay?: ReservationRoomMoveStay;
  segments?: Array<ReservationRoomMoveSegment>;
  sourceCleaningTargetId?: string;
  pinAccessEndsAt?: string;
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

export type AssignmentDraftRequest = {
  cleaningTargetId: string;
  maidProfileId: string;
  sequenceNumber: number;
  expectedAssignmentVersion: number;
};

export type AssignmentPreviewRequest = {
  serviceDate: string;
  previewSeed?: string;
};

export type AssignmentPreviewUnconfirmed = {
  serviceDate: string;
  previewSeed: string;
  decisionReady: false;
  durationPolicyStatus: "unconfirmed";
  proposedAssignments: Array<AssignmentPreviewRow>;
  error: {
  code: "ASSIGNMENT_PREVIEW_DURATION_POLICY_UNCONFIRMED";
  message: string;
};
};

export type AssignmentPreviewResult = {
  serviceDate: string;
  previewSeed: string;
  durationPolicy: AssignmentDurationPolicy;
  decisionReady: true;
  inputFingerprint: string;
  fixedAssignments: Array<AssignmentPreviewRow>;
  proposedAssignments: Array<AssignmentPreviewRow>;
  remainingUnassignedTargets: Array<AssignmentPreviewBlockedTarget>;
  blockedTargets: Array<AssignmentPreviewBlockedTarget>;
  maidSummaries: Array<{
  maidProfileId: string;
  totalFee: number;
  fixedCount: number;
  proposedCount: number;
}>;
  objectiveScore: {
  completedTargetCount: number;
  feeSpread: number;
  feeDeviation: string;
  routeScore: {
  zoneChanges: number;
  roomDistance: number;
};
};
};

export type AssignmentCommitImpact = {
  serviceDate: string;
  impactFingerprint: string;
  committableDrafts: Array<AssignmentCommitCandidate>;
  blockedDrafts: Array<AssignmentCommitBlockedCandidate>;
  remainingUnassignedTargets: Array<AssignmentCommitUnassignedTarget>;
};

export type AssignmentCommitRequest = {
  serviceDate: string;
  expectedImpactFingerprint: string;
  items: Array<AssignmentCommitItem>;
};

export type AssignmentCommitResult = {
  serviceDate: string;
  impactFingerprint: string;
  notifiedAssignments: Array<AssignmentNotified>;
  remainingDrafts: Array<AssignmentCommitCandidate>;
  blockedDrafts: Array<AssignmentCommitBlockedCandidate>;
  unassignedTargets: Array<AssignmentCommitUnassignedTarget>;
};

export type AssignmentPrestartChangeRequest = {
  expectedCurrentAssignmentId: string;
  expectedAssignmentVersion: number;
  reasonCode: "MAID_UNAVAILABLE" | "SCHEDULE_CHANGED" | "SEQUENCE_CHANGED" | "OPERATIONAL_CHANGE";
  maidProfileId: string;
  sequenceNumber: number;
  availableFrom?: string;
  dueAt?: string;
};

export type AssignmentPrestartUnassignRequest = {
  expectedCurrentAssignmentId: string;
  expectedAssignmentVersion: number;
  reasonCode: "MAID_UNAVAILABLE" | "SCHEDULE_CHANGED" | "SEQUENCE_CHANGED" | "OPERATIONAL_CHANGE";
};

export type AssignmentCancellationRequest = {
  expectedCurrentAssignmentId: string;
  expectedAssignmentVersion: number;
  reasonCode: "PERSONAL_REASON" | "HEALTH_REASON" | "MAID_UNAVAILABLE" | "OPERATIONAL_CHANGE";
  reasonDetail?: string;
};

export type AssignmentCancellationDecisionRequest = {
  expectedCurrentAssignmentId: string;
  expectedAssignmentVersion: number;
  reasonCode: "APPROVED" | "REJECTED" | "OPERATIONAL_CHANGE" | "MAID_UNAVAILABLE";
  decision: "approved" | "rejected";
};

export type AssignmentChangeRequest = {
  requestId: string;
  cleaningTargetId: string;
  assignmentId: string;
  maidProfileId: string;
  requestType: "cancel_assignment";
  reasonCode: string;
  reasonDetail: string | null;
  status: "pending" | "approved" | "rejected" | "superseded";
  sourceAssignmentRevision: number;
  sourceTargetAssignmentVersion: number;
  requestedAt: string;
  decision: "approved" | "rejected" | null;
  decisionReasonCode: string | null;
  decidedAt: string | null;
};

export type AssignmentChangeRequestPage = {
  requests: Array<AssignmentChangeRequest>;
  nextCursor: string | null;
};

export type AttemptLifecycleRequest = {
  expectedExecutionVersion: number;
  expectedAssignmentId: string;
  expectedAssignmentRevision: number;
  expectedProfileVersion: number;
  action: "allow_finish";
  reasonCode: "DEACTIVATION_FINISH_CURRENT";
  payload: {

};
} | {
  expectedExecutionVersion: number;
  expectedAssignmentId: string;
  expectedAssignmentRevision: number;
  expectedProfileVersion: number;
  action: "allow_upload";
  reasonCode: "DEACTIVATION_UPLOAD_ONLY";
  payload: {

};
} | {
  expectedExecutionVersion: number;
  expectedAssignmentId: string;
  expectedAssignmentRevision: number;
  expectedProfileVersion: number;
  action: "expire_scheduled";
  reasonCode: "SCHEDULE_EXPIRED";
  payload: {

};
} | {
  expectedExecutionVersion: number;
  expectedAssignmentId: string;
  expectedAssignmentRevision: number;
  expectedProfileVersion: number;
  action: "interrupt_handover";
  reasonCode: "ADMIN_HANDOVER" | "DEACTIVATION_HANDOVER";
  payload: {
  maidProfileId: string;
  sequenceNumber: number;
  serviceDate: string;
  availableFrom: string;
  dueAt: string;
  deactivateOld: boolean;
};
};

export type AttemptLifecycleImpact = {
  attempt: AttemptExecution;
  capability: AttemptCapability | null;
  profileStatus: "active" | "deactivation_pending" | "upload_only" | "inactive" | "departed";
  profileVersion: number;
  targetAssignmentVersion: number;
};

export type AttemptLifecycleResult = {
  attempt: AttemptExecution;
  capability: AttemptCapability | null;
  profileStatus: "active" | "deactivation_pending" | "upload_only" | "inactive" | "departed";
  nextAttempt: AttemptExecution | null;
  profileVersion: number;
  effectiveAt: string;
  recordedAt: string;
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

export type AttemptWithOfflineLease = {
  attempt: AttemptExecution;
  lease: OfflineWorkLease;
  serverTime: string;
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

export type AttemptPhotoSlots = {
  attemptId: string;
  assignmentId: string;
  assignmentRevision: number;
  slots: Array<{
  slotId: string;
  slotKey: string;
  required: boolean;
  displayOrder: number;
  maxPhotos: 1 | 10;
  currentRevision: number;
  collectionRevision: number | null;
  photoCount: number;
  uploadStatus: "missing" | "cleared" | "verified" | "pending" | "failed" | "purged" | "expired" | "unavailable";
  photoId: string | null;
  photos: Array<AttemptPhotoItem>;
  retentionPolicy?: "cleaning_submission" | "room_issue" | "complaint" | "interruption" | "sync_conflict" | "mixed" | "orphan" | "legacy_upload";
  retentionStartsAt?: string | null;
  expiresAt?: string | null;
  purgedAt?: string | null;
  mediaAvailability?: "available" | "purged" | "unavailable";
}>;
};

export type PhotoUploadResponse = PhotoUploadOperation & {

};

export type BombRoomReportRequest = {
  evidencePhotoIds: Array<string>;
  memo: string;
};

export type BombRoomReportEnvelope = {
  bombReport: {
  id: string;
  attemptId: string;
  evidenceCount: number;
  reportedAt: string;
};
};

export type CreateSubmissionRequest = {
  clientSubmissionId: string;
  expectedRevision: number;
  candleCount: number;
};

export type CleaningSubmission = {
  id: string;
  attemptId: string;
  version: number;
  status: "submitted" | "superseded" | "approved" | "rejected";
  submittedBy: string;
  submittedAt: string;
  currentRevision: number;
  current: boolean;
  photoCount: number;
  candleCount: number;
  bombReportId?: string | null;
  bombDecision?: "approved" | "rejected" | null;
  inspectionDecision?: "approved" | "rejected" | null;
  inspectionReasonCode?: string | null;
  decidedAt?: string | null;
  bombReport?: {
  id: string;
  attemptId: string;
  memo: string;
  evidenceCount: number;
  evidencePhotoIds: Array<string>;
  reportedAt: string;
};
  photos?: Array<SubmissionPhotoBinding>;
  photoSlots?: Array<SubmissionPhotoSlot>;
  reviewContext?: SubmissionReviewContext;
};

export type SubmissionEnvelope = {
  submission: CleaningSubmission;
};

export type SubmissionListEnvelope = {
  submissions: Array<CleaningSubmission>;
};

export type BombRoomDecisionRequest = {
  decision: "approved" | "rejected";
  reasonCode: "BOMB_CONFIRMED" | "BOMB_NOT_CONFIRMED" | "BOMB_EVIDENCE_INSUFFICIENT";
};

export type InspectionDecisionRequest = {
  reasonCode: "QUALITY_OK" | "QUALITY_REWORK" | "EVIDENCE_INCOMPLETE" | "CLEANING_INCOMPLETE";
};

export type BombRoomDecisionEnvelope = {
  bombDecision: {
  id: string;
  submissionId: string;
  decision: "approved" | "rejected";
  reasonCode: string;
  decidedAt: string;
};
};

export type InspectionDecisionEnvelope = {
  inspection: {
  submissionId: string;
  decisionId: string;
  decision: "approved" | "rejected";
  reasonCode: string;
  decidedAt: string;
  earningId: string | null;
  recleanTargetId: string | null;
  recleanAssignmentId: string | null;
};
};

export type Notification = {
  id: string;
  category: string;
  title: string;
  body: string;
  roomId: string | null;
  cleaningTargetId: string | null;
  deepLink: {
  kind: "cleaningTarget" | "assignmentRequest" | "submission" | "complaintCase" | "payrollCycle" | "payrollProfile";
  entityId: string;
} | null;
  groupId: string | null;
  requiresAction: boolean;
  readAt: string | null;
  resolvedAt: string | null;
  occurredAt: string;
};

export type NotificationEnvelope = {
  notification: Notification;
};

export type NotificationListEnvelope = {
  notifications: Array<Notification>;
  nextCursor: string | null;
};

export type CleaningHistoryItem = {
  submissionId: string | null;
  attemptId: string;
  cleaningTargetId: string;
  roomId: string;
  roomNumber: string | null;
  roomTypeCode: string | null;
  roomTypeName: string | null;
  performerProfileId: string;
  performerDisplayName: string;
  cleaningKind: "checkout" | "stayover" | "additional" | "reclean";
  originalServiceDate: string;
  serviceDate: string;
  startedAt: string | null;
  fieldCompletedAt: string;
  submittedAt: string | null;
  inspectionStatus: "not_submitted" | "pending" | "approved" | "rejected";
  decidedAt: string | null;
  photoCount: number;
  mediaAvailability: "not_submitted" | "available" | "purged" | "unavailable";
  expiresAt: string | null;
  baseFeeSnapshot: number;
  earningTotalAmount: number | null;
};

export type CleaningHistoryPage = {
  date: string;
  fromDate: string;
  toDate: string;
  items: Array<CleaningHistoryItem>;
  nextCursor: string | null;
};

export type WorkHistoryDay = {
  date: string;
  availableSubmitted: boolean;
  assignmentNotified: boolean;
  fieldCompleted: boolean;
};

export type WorkHistoryItem = {
  maidProfileId: string;
  maidDisplayName: string;
  maidDisplayNameSource: "current_profile";
  availabilitySubmittedAt: string | null;
  availabilityCurrentVersion: number | null;
  availabilityVersionCount: number;
  days: Array<WorkHistoryDay>;
};

export type WorkHistorySummary = {
  maidCount: number;
  availabilityMaidCount: number;
  availabilityDayCount: number;
  notifiedMaidCount: number;
  notifiedDayCount: number;
  fieldCompletedMaidCount: number;
  fieldCompletedDayCount: number;
};

export type WorkHistoryPage = {
  weekStart: string;
  weekEnd: string;
  timezone: "Asia/Seoul";
  summary: WorkHistorySummary;
  items: Array<WorkHistoryItem>;
  nextCursor: string | null;
};

export type RoomPinRevealRequest = {
  assignmentId?: string;
  attemptId?: string;
  accessLeaseId?: string;
};

export type RoomPinReveal = {
  roomId: string;
  credential: string;
  pinVersion: number;
  clearAfterSeconds: number;
  expiresAt: string;
};

export type RoomPinRevealEnvelope = {
  pin: RoomPinReveal;
};

export type PublishCleaningTemplateRequest = {
  roomTypeCode: CleaningTemplateRoomTypeCode;
  cleaningKind: "checkout";
  expectedVersion: number;
  durationMinutes?: number | null | undefined;
  slots: Array<CheckoutCleaningTemplateV8Slot>;
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

export type PayrollAdjustment = {
  adjustmentId: string;
  maidProfileId: string;
  bookVersion: number;
  availableWeekStart: string;
  amount: number;
  currency: "KRW";
  reasonCode: PayrollAdjustmentReason;
  rootEarningId: string;
  correctionOfEarningId?: string;
  correctionOfAdjustmentId?: string;
  reversalOfEarningId?: string;
  reversalOfAdjustmentId?: string;
  lateCarriedEarningId?: string;
  alreadyClaimed: boolean;
  createdAt: string;
};

export type PayrollAdjustmentCorrectionRequest = {
  sourceAdjustmentId: string;
  amount: number;
  expectedVersion: number;
};

export type PayrollAdjustmentEntry = {
  adjustmentId: string;
  availableWeekStart: string;
  amount: number;
  reasonCode: PayrollAdjustmentReason;
  alreadyClaimed: boolean;
};

export type PayrollAdjustmentEnvelope = {
  adjustment: PayrollAdjustment;
};

export type PayrollAdjustmentReason = "earning_correction" | "adjustment_correction" | "earning_reversal" | "adjustment_reversal" | "late_earning_carry";

export type PayrollAdjustmentReversalRequest = {
  sourceAdjustmentId: string;
  expectedVersion: number;
};

export type PayrollCorrectionRequest = PayrollEarningCorrectionRequest | PayrollAdjustmentCorrectionRequest;

export type PayrollCycle = {
  cycleId: string | null;
  maidProfileId: string;
  weekStart: string;
  status: PayrollStatus;
  version: number;
  lockedAmount: number | null;
  paymentStartedAt: string | null;
  itemCount: number;
  totalAmount: number;
  items: Array<PayrollItem>;
  itemsNextCursor: string | null;
  lateEarningCount: number;
  lateEarningAmount: number;
  lateEarnings: Array<PayrollLateEarning>;
  lateEarningsNextCursor: string | null;
  offsetSettled: boolean;
  adjustmentAmount: number;
  carryInAmount: number;
  carryOutAmount: number;
  payableAmount: number;
  adjustmentCount: number;
  paymentAttemptId: string | null;
  paymentAttemptNumber: number | null;
  paidAt: string | null;
  checkReasonCode: "TRANSFER_RESULT_UNCERTAIN" | null;
  lastReopenReasonCode: "NO_TRANSFER_CONFIRMED" | null;
};

export type PayrollCycleEnvelope = {
  payroll: PayrollCycle;
};

export type PayrollEarningCorrectionRequest = {
  sourceEarningId: string;
  amount: number;
  expectedVersion: number;
};

export type PayrollEarningReversalRequest = {
  sourceEarningId: string;
  expectedVersion: number;
};

export type PayrollEntriesEnvelope = {
  kind: "items" | "lateEarnings" | "adjustments";
  entries: Array<PayrollItem | PayrollLateEarning | PayrollAdjustmentEntry>;
  nextCursor: string | null;
};

export type PayrollItem = {
  earningId: string;
  earnedOn: string;
  amount: number;
  alreadyClaimed: boolean;
};

export type PayrollLateCarryRequest = {
  expectedVersion: number;
};

export type PayrollLateEarning = {
  earningId: string;
  earnedOn: string;
  amount: number;
};

export type PayrollListEnvelope = {
  payroll: Array<PayrollCycle>;
  nextCursor: string | null;
};

export type PayrollPaymentCheckRequest = {
  expectedVersion: number;
  reasonCode: "TRANSFER_RESULT_UNCERTAIN";
};

export type PayrollPaymentPaidRequest = {
  expectedVersion: number;
  paymentMethod: "bank_transfer";
  providerReferenceId: string;
};

export type PayrollPaymentReopenRequest = {
  expectedVersion: number;
  reasonCode: "NO_TRANSFER_CONFIRMED";
};

export type PayrollPaymentResult = {
  paymentResultId: string;
  paymentAttemptId: string;
  payrollCycleId: string;
  resultType: "check" | "paid" | "reopened";
  beforeStatus: "paying" | "check";
  afterStatus: "check" | "paid" | "open";
  cycleVersion: number;
  lockedAmount: number;
  paymentMethod?: "bank_transfer";
  providerReferenceId?: string;
  reasonCode?: "TRANSFER_RESULT_UNCERTAIN" | "NO_TRANSFER_CONFIRMED";
  occurredAt: string;
};

export type PayrollPaymentResultEnvelope = {
  paymentResult: PayrollPaymentResult;
};

export type PayrollReversalRequest = PayrollEarningReversalRequest | PayrollAdjustmentReversalRequest;

export type PayrollStartRequest = {
  maidProfileId: string;
  weekStart: string;
  expectedVersion: number;
};

export type PayrollStatus = "open" | "paying" | "check" | "paid";

export type Complaint = {
  id: string;
  roomId: string;
  cleaningTargetId: string;
  cleaningAttemptId: string;
  submissionId: string;
  inspectionDecisionId: string;
  originalEarningId: string;
  maidProfileId: string;
  category: ComplaintCategory;
  status: ComplaintStatus;
  version: number;
  currentDecisionId: string | null;
  firstDecidedAt: string | null;
  responseDeadline: string | null;
  receivedAt: string;
  updatedAt: string;
  currentDecision: ComplaintDecision | null;
  maidResponse: ComplaintMaidResponse | null;
  reworkDecision: ComplaintReworkDecision | null;
};

export type ComplaintCasRequest = {
  expectedVersion: number;
};

export type ComplaintCategory = "cleanliness_general" | "bathroom_cleanliness" | "bedding_quality" | "trash_not_removed" | "amenity_missing" | "damage_or_loss" | "odor_or_smoke" | "access_or_handover";

export type ComplaintCreateRequest = {
  originalEarningId: string;
  category: ComplaintCategory;
  expectedVersion: 0;
};

export type ComplaintDecision = {
  id: string;
  complaintId: string;
  decisionVersion: number;
  decisionKind: "initial" | "correction";
  priorDecisionId: string | null;
  finding: ComplaintFinding;
  penaltyScore: number;
  reworkRequired: boolean;
  decidedAt: string;
};

export type ComplaintDecisionRequest = {
  expectedVersion: number;
  finding: ComplaintFinding;
  penaltyScore: number;
  reworkRequired: boolean;
};

export type ComplaintEnvelope = {
  complaint: Complaint;
};

export type ComplaintFinding = "confirmed" | "unverifiable" | "false";

export type ComplaintHistoryEnvelope = {
  events: Array<ComplaintHistoryEvent>;
  nextCursor: string | null;
};

export type ComplaintHistoryEvent = {
  eventId: number;
  eventType: "received" | "review_started" | "decided" | "acknowledged" | "appealed" | "closed" | "corrected" | "rework_materialized";
  fromStatus?: "received" | "under_review" | "decided" | "acknowledged" | "appealed" | "closed";
  toStatus: ComplaintStatus;
  caseVersion: number;
  occurredAt: string;
  decision?: ComplaintDecision;
  maidResponse?: ComplaintMaidResponse;
  compensationDecisionId?: string;
};

export type ComplaintListEnvelope = {
  complaints: Array<Complaint>;
  nextCursor: string | null;
};

export type ComplaintMaidResponse = {
  id: string;
  complaintId: string;
  decisionId: string;
  maidProfileId: string;
  responseType: "acknowledged" | "appealed";
  appealReasonCode: "work_completed_as_required" | "evidence_misinterpreted" | "not_responsible" | "timeline_mismatch" | null;
  respondedAt: string;
};

export type ComplaintResponseRequest = {
  expectedVersion: number;
  responseType: "acknowledged";
} | {
  expectedVersion: number;
  responseType: "appealed";
  appealReasonCode: "work_completed_as_required" | "evidence_misinterpreted" | "not_responsible" | "timeline_mismatch";
};

export type ComplaintReworkDecision = {
  view: "originalMaid";
  sameMaid: boolean;
  sourceDecisionIsCurrent: boolean;
} | {
  view: "assigneeMaid";
  id: string;
  reworkCleaningTargetId: string;
  compensationAmount: number;
  currency: "KRW";
  sourceDecisionIsCurrent: boolean;
} | {
  view: "admin";
  id: string;
  complaintId: string;
  sourceComplaintDecisionId: string;
  currentComplaintDecisionId: string;
  sourceDecisionIsCurrent: boolean;
  originalCleaningTargetId: string;
  reworkCleaningTargetId: string;
  originalMaidProfileId: string;
  assigneeMaidProfileId: string;
  sameMaid: boolean;
  originalBaseFeeSnapshot: number;
  compensationAmount: number;
  currency: "KRW";
  sourceCaseVersion: number;
  decisionVersion: 1;
  decidedAt: string;
};

export type ComplaintReworkEnvelope = {
  complaint: Complaint;
  reworkDecision: ComplaintReworkDecision;
  assignment: {
  id: string;
  cleaningTargetId: string;
  maidProfileId: string;
  sequenceNumber: number;
  revision: number;
  serviceDate: string;
  availableFrom: string;
  dueAt: string | null;
};
};

export type ComplaintReworkRequest = {
  expectedVersion: number;
  complaintDecisionId: string;
  assigneeMaidProfileId: string;
  compensationAmount: number;
};

export type ComplaintStatus = "received" | "under_review" | "decided" | "acknowledged" | "appealed" | "closed";

export type WebPushSubscription = {
  id: string;
  version: number;
  status: "active" | "retired";
  createdAt: string;
  updatedAt: string;
  retiredAt: string | null;
};

export type WebPushSubscriptionEnvelope = {
  subscription: WebPushSubscription;
};

export type WebPushSubscriptionRegisterRequest = {
  bindingProof: string;
  subscription: {
  endpoint: string;
  expirationTime: number | null;
  keys: {
  p256dh: string;
  auth: string;
};
};
  expectedCurrent?: {
  subscriptionId: string;
  version: number;
};
};

export type WebPushSubscriptionRetireRequest = {
  expectedVersion: number;
};

export type RoomOccupancyStatus = "VACANT" | "OCCUPIED";

export type RoomReservationLifecycle = "NONE" | "FUTURE" | "RESERVATION_PRESENT" | "ARRIVAL_PENDING" | "OCCUPIED";

export type RoomReadinessStatus = "READY" | "CLEANING_REQUIRED" | "CHECKIN_BLOCKED";

export type RoomPrimaryDisplayStatus = "BLOCKED" | "OCCUPIED" | "ARRIVAL_PENDING" | "RESERVATION_PRESENT" | "CLEANING_REQUIRED" | "READY";

export type RoomBlockingReasonCode = "CANDLE_PRESENT" | "OPERATION_BLOCKED" | "ROOM_ISSUE_BLOCKED" | "DATA_UNCONFIRMED";

export type RoomReadinessReasonCode = "CANDLE_PRESENT" | "OPERATION_BLOCKED" | "ROOM_ISSUE_BLOCKED" | "DATA_UNCONFIRMED" | "CLEANING_REQUIRED" | "PIN_MISMATCH" | "PIN_UNCONFIGURED";

export type RoomReasonCode = "OCCUPIED" | "RESERVATION_CURRENT" | "CLEANING_REQUIRED" | "CANDLE_PRESENT" | "OPERATION_BLOCKED" | "ROOM_ISSUE_BLOCKED" | "DATA_UNCONFIRMED";

export type ReservationStatus = "active" | "cancelled" | "checked_out";

export type ReasonCode = string;

export type ReservationRoomMoveReasonCode = "GUEST_REQUEST" | "ROOM_UNAVAILABLE" | "OPERATIONAL_ADJUSTMENT";

export type ReservationRoomMoveMode = "BEFORE_CHECKIN" | "DURING_STAY";

export type ReservationRoomMoveRejectionReasonCode = "RESERVATION_NOT_ACTIVE" | "SAME_ROOM" | "INVALID_MOVE_EFFECTIVE_AT" | "OPEN_ENDED_STAY_REQUIRES_END" | "CLEANING_WORKFLOW_PUBLIC" | "PLANNED_CHECKOUT_NOT_PRIVATE" | "CLEANING_WORKFLOW_ASSIGNED" | "CLEANING_WORKFLOW_NOTIFIED" | "CLEANING_WORKFLOW_STARTED" | "ACTIVE_PIN_ACCESS_EXISTS" | "TARGET_ROOM_BLOCKED" | "TARGET_ROOM_NOT_READY" | "RESERVATION_OVERLAP";

export type ReservationRoomMoveBlockingReasonCode = "RESERVATION_VERSION_CONFLICT" | "SOURCE_ROOM_VERSION_CONFLICT" | "TARGET_ROOM_VERSION_CONFLICT" | "TARGET_ROOM_OVERLAP" | "ROOM_CHANGE_PREVIEW_STALE" | "CLEANING_ASSIGNMENT_LOCKED" | "PIN_LEASE_ACTIVE" | "TARGET_ROOM_BLOCKED" | "TARGET_ROOM_NOT_READY";

export type ReservationRoomMoveOutcome = {
  occupancyStatus: RoomOccupancyStatus;
  readinessStatus: RoomReadinessStatus;
  stateVersion: number;
};

export type ReservationRoomMoveStay = {
  id: string;
  version: number;
  currentRoomId: string;
};

export type ReservationRoomMoveSegment = {
  id: string;
  roomId: string;
  startsAt: string;
  endsAt: string | null;
};

export type AssignmentPreviewRow = {
  cleaningTargetId: string;
  roomId: string;
  roomNumber: string;
  roomTypeCode: "standard" | "premium" | "oceanPremium" | "oceanFamily" | "unknown";
  elevatorZone: string;
  maidProfileId: string;
  maidDisplayName: string;
  proposedSequenceNumber: number;
  serviceDate: string;
  expectedAssignmentVersion: number;
  expectedAvailabilityVersion: number | null;
  feeSnapshot: number;
  durationMinutes: number | null;
  availableFrom: string;
  dueAt: string | null;
};

export type AssignmentDurationPolicy = {
  id?: string;
  version: number;
  status: "confirmed";
  standardMinutes: number;
  premiumMinutes: number;
  oceanPremiumMinutes: number;
  oceanFamilyMinutes: number;
  createdAt?: string;
  confirmedAt?: string;
};

export type AssignmentPreviewBlockedTarget = {
  cleaningTargetId: string;
  reason: string;
};

export type AssignmentCommitCandidate = {
  assignmentId: string;
  cleaningTargetId: string;
  roomId: string;
  roomNumber: string;
  maidProfileId: string;
  maidDisplayName: string;
  serviceDate: string;
  sequenceNumber: number;
  revision: number;
  targetAssignmentVersion: number;
  expectedAvailabilityVersion: number;
  availableFrom: string | null;
  dueAt: string | null;
};

export type AssignmentCommitBlockedCandidate = {
  assignmentId: string;
  cleaningTargetId: string;
  roomId: string;
  roomNumber: string;
  maidProfileId: string;
  maidDisplayName: string;
  serviceDate: string;
  sequenceNumber: number;
  revision: number;
  targetAssignmentVersion: number;
  currentAvailabilityVersion: number | null;
  reasonCodes: Array<string>;
  availableFrom: string | null;
  dueAt: string | null;
};

export type AssignmentCommitUnassignedTarget = {
  cleaningTargetId: string;
  roomId: string;
  roomNumber: string;
  serviceDate: string;
  status: "unassigned";
  targetAssignmentVersion: number;
  availableFrom: string | null;
  dueAt: string | null;
};

export type AssignmentCommitItem = {
  cleaningTargetId: string;
  expectedAssignmentVersion: number;
  expectedAvailabilityVersion: number;
};

export type AssignmentNotified = {
  assignmentId: string;
  cleaningTargetId: string;
  roomId: string;
  roomNumber: string;
  maidProfileId: string;
  maidDisplayName: string;
  serviceDate: string;
  sequenceNumber: number;
  revision: number;
  targetAssignmentVersion: number;
  expectedAvailabilityVersion: number;
  availableFrom: string | null;
  dueAt: string | null;
  notifiedAt: string;
};

export type AttemptCapability = {
  capabilityId: string;
  attemptId: string;
  assignmentId: string;
  assignmentRevision: number;
  kind: "finish_current" | "upload_submit" | "evidence_upload";
  allowedActions: Array<"complete_field_work" | "upload_evidence" | "validate_evidence" | "submit">;
  issuedAt: string;
  expiresAt: string;
  revokedAt: string | null;
};

export type OfflineWorkLease = {
  leaseId: string;
  version: 1;
  attemptId: string;
  assignmentId: string;
  assignmentRevision: number;
  issuedAt: string;
  expiresAt: string;
  metadataExpiresAt: string;
  allowedActions: Array<"complete_field_work">;
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

export type AttemptPhotoItem = {
  photoItemId: string | null;
  itemRevision: number;
  displayOrder: number;
  photoId: string | null;
  photoVersion: number;
  uploadStatus: "verified" | "pending" | "failed" | "purged" | "expired" | "unavailable";
  retentionPolicy: "cleaning_submission" | "room_issue" | "complaint" | "interruption" | "sync_conflict" | "mixed" | "orphan" | "legacy_upload";
  retentionStartsAt: string | null;
  expiresAt: string | null;
  purgedAt: string | null;
  mediaAvailability: "available" | "purged" | "unavailable";
};

export type PhotoUploadOperation = {
  operationId: string;
  objectId: string;
  attemptId: string;
  targetSlotId: string;
  photoItemId: string | null;
  status: "reserved" | "provider_succeeded" | "reconciliation_pending" | "accepted" | "compensation_pending" | "compensated";
  leaseVersion: number;
  leaseExpiresAt: string | null;
  photoId: string | null;
  photoVersion: number | null;
  collectionRevision: number | null;
  itemRevision: number | null;
  uploadedAt: string | null;
  purgeAfter: string | null;
  retentionPolicy: "cleaning_submission" | "room_issue" | "complaint" | "interruption" | "sync_conflict" | "mixed" | "orphan" | "legacy_upload";
  retentionStartsAt: string | null;
  expiresAt: string | null;
  purgedAt: string | null;
  mediaAvailability: "available" | "purged" | "unavailable";
  compensationAllowed: boolean;
  quotaWarning?: boolean;
};

export type SubmissionPhotoBinding = {
  photoId: string;
  photoItemId?: string | null;
  itemRevision?: number | null;
  photoDisplayOrder?: number | null;
  targetPhotoSlotId: string;
  slotKey: string;
  label: string;
  displayOrder: number;
  required: boolean;
  photoVersion: number;
  retentionPolicy: "cleaning_submission" | "room_issue" | "complaint" | "interruption" | "sync_conflict" | "mixed" | "orphan" | "legacy_upload";
  retentionStartsAt: string | null;
  expiresAt: string | null;
  purgedAt: string | null;
  mediaAvailability: "available" | "purged" | "unavailable";
};

export type SubmissionPhotoSlot = {
  targetPhotoSlotId: string;
  slotKey: string;
  label: string;
  displayOrder: number;
  required: boolean;
  photos: Array<{
  photoId: string;
  photoItemId: string | null;
  itemRevision: number | null;
  displayOrder: number;
  photoVersion: number;
  retentionPolicy: "cleaning_submission" | "room_issue" | "complaint" | "interruption" | "sync_conflict" | "mixed" | "orphan" | "legacy_upload";
  retentionStartsAt: string | null;
  expiresAt: string | null;
  purgedAt: string | null;
  mediaAvailability: "available" | "purged" | "unavailable";
}>;
};

export type SubmissionReviewContext = {
  cleaningTargetId: string;
  cleaningKind: "checkout" | "stayover" | "additional" | "reclean";
  roomNumber: string;
  serviceDate: string;
  maidProfileId: string;
};

export type CleaningTemplateRoomTypeCode = "standard" | "premium" | "oceanPremium" | "oceanFamily";

export type CheckoutCleaningTemplateV8Slot = CleaningTemplateSlot & {

};

export type CleaningTemplateSlot = {
  slotKey: string;
  displayOrder: number;
  required: boolean;
  label: string;
  maxPhotos?: number;
  description?: string;
  section?: string;
  instanceKey?: string;
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

