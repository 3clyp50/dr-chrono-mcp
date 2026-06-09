# Clinical Inbox Endpoint Inventory

Planning inventory for the clinical-inbox autopilot, derived from physician-marked DrChrono API
screenshots and validated against the live corpus work. Treat this as a product/API map, not as
API reference replacement; confirm exact field names against the current DrChrono docs before
shipping new write paths.

## Need

### `GET /api/messages`

Primary message-center lane for the full inbox. Use this for broad inbox polling once we move
beyond the voice-corpus pull.

Why it matters:
- Covers message-center items across patient, lab, fax, referral, and general message types.
- Supports cursor pagination.
- Supports filters visible in the docs/screenshots: `cursor`, `doctor`, `owner`, `patient`,
  `page_size`, `received_since`, `responsible_user`, `type`, and `updated_since`.
- This is the likely webhook/poll fallback surface for "what needs attention now?"

Implementation note:
- Prefer `updated_since` / `received_since` for incremental inbox polling.
- Keep all pagination cursor handling exact: consume `next`, parse its query, and replay the
  returned cursor params.

### `GET /api/messages/{id}`

Detail fetch for a message-center item.

Why it matters:
- The list endpoint may not carry every body/note/attachment field needed to draft safely.
- Use after triage when the item is selected for auto-draft or HITL review.

### `POST /api/messages`

Write-back path for created messages.

Why it matters:
- This is the endpoint for sending or creating the drafted response after agent/HITL approval.
- Screenshots show message-center write permissions and response shape aligned with the message
  object used by list/read.

Implementation note:
- Keep send-vs-draft behavior explicit. Do not silently send patient-facing messages while still
  validating the workflow.

### `GET /api/patient_messages`

Patient-message corpus source.

Why it matters:
- Verified live as a practical source for historical patient-message bodies used to build the
  physician voice graph.
- Response includes `body`, `patient`, `attachments`, `updated_at`, `created_at`, `doctor`,
  `message`, and `subject`.

Implementation note:
- Use `doctor` and `page_size`; advance by cursor from `next`.
- Do not use `since` on this endpoint until DrChrono confirms support. Live testing showed this
  endpoint can fail when `since` is sent.
- Current code uses a 500-page / 50,000-row safety cap. Add resumability before full backfills.

## Maybe Need

### `PATCH /api/messages/{id}`

Potential state/annotation path.

Why it might matter:
- Could support internal notes, workflow step transitions, archived/read/starred state, or draft
  management if DrChrono exposes those fields in a stable way.

Open questions:
- Which fields are writable?
- Can it safely create a draft-like state, or only update an existing message?
- Does it alter patient-visible content or only message-center metadata?

### `PUT /api/messages/{id}`

Potential full update path.

Why it might matter:
- Could be needed if DrChrono requires full-message updates instead of PATCH for certain fields.

Open questions:
- Whether PUT is materially different from PATCH for message-center workflows.
- Whether the endpoint requires sending the full current message shape.

### `GET /api/prescription_messages`

Future refill/prescription lane.

Why it might matter:
- Prescription messages are a natural inbox lane after labs/patient messages.
- Screenshots show filters such as `created_at`, `cursor`, `doctor`, `page_size`,
  `parent_message`, `patient`, and `since`.

Current posture:
- Not first slice. Keep it for a later refill/autopilot lane after the message-center loop works.

### `GET /api/patient_communications/{id}`

Possible CQM/communication-history support.

Why it might matter:
- Could provide structured patient-communication records for audit or context.

Current posture:
- Maybe only. Not needed for the voice graph or first message-center write-back.

## Not Needed For The First Slice

These appeared near the marked screenshots but are not required for the current inbox autopilot
loop:
- Patient physical exams.
- Implantable devices.
- Patient risk assessments.
- Generic documents CRUD, unless an inbox item has an attachment that must be fetched.
- CQM communication records unless they become necessary for compliance reporting.

## Extra Product Inference

The PDF shifts the next build step from "patient-message corpus only" to a broader
message-center loop:

1. Use `/api/messages` for current inbox polling and triage across patient, lab, fax, referral,
   and general message types.
2. Use `/api/messages/{id}` to hydrate the selected item before drafting.
3. Use the existing voice graph to retrieve phrasing/action.
4. Use `POST /api/messages` for approved write-back.
5. Explore `PATCH`/`PUT /api/messages/{id}` only after DrChrono confirms whether these can manage
   drafts, annotations, read/archive status, or workflow state without patient-visible side
   effects.

That means the current PR is the reusable voice/retrieval core; the next PR should add
message-center triage/read/write tools on top of it.
