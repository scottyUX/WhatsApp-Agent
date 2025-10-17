# Consultant Dashboard Refactor Plan _(temporary)_

> _Working branch: `feature/consultant-dashboard-refactor`_
>
> This checklist guides the frontend clean-up. Remove this file before merging once all tasks are complete.

---

## 1. Establish Shared Types & Constants
- [x] Create `src/types/consultant.ts` consolidating `PatientData`, `AppointmentItem`, and nested interfaces currently duplicated across components.
- [x] Introduce `src/constants/consultant.ts` with option lists (journey stages, hair-loss pattern, family history, treatments) and reuse everywhere.
- [x] Update existing imports to rely on the shared definitions; ensure no stale inline arrays remain.

## 2. Utilities & Validation
- [x] Move normalisers (`normalizeHairLossProfile`, `formatLabel`) into shared utils.
- [x] Extract validation helpers into `src/utils/consultantValidation.ts` (personal info, medical summary, hair-loss rules).
- [x] Define raw API response types and mapping utilities to align FE models with Supabase schema.
- [ ] Add focused unit tests for these utilities (Jest / Vitest) to lock behaviour.

## 3. Data Access Layer
- [x] Create `src/services/consultantApi.ts` wrapping `fetch`, supporting configurable options (GET/PUT).
- [x] Build `useConsultantDashboard` hook to own initial data load, normalisation, error state, and patient updates.
- [x] Update `app/consultant/page.tsx` to consume the hook instead of inlined fetch logic.

## 4. Component Decomposition
- [x] Break `PatientSnapshot` into subcomponents:
  - `PersonalInfoSection`
  - `ConsultationStatusSection`
  - `MedicalSummarySection`
  - `HairLossProfileSection`
  - keep `NotesSection` as-is (already modular)
- [x] Ensure each subcomponent receives typed props and uses shared utilities.
- [ ] Add lightweight stories/tests where value.

## 5. Layout Cleanup
- [x] Extract consult page sidebar/table into dedicated components (`AppointmentsPanel`, `PatientDirectoryTable`, etc.).
- [x] Simplify `app/consultant/page.tsx` to layout + event wiring.
- [x] Confirm modal interactions still work after component split.

## 6. Polish & Removal
- [ ] Verify type usage, remove dead code, run lint/tests.
- [ ] Manually QA consultant flow (load, edit, modal, responsiveness).
- [ ] Delete this                   plan file prior to opening the PR.

## 7. Error & Loading Strategy
- [ ] Create consistent error boundary components for dashboard modules.
- [ ] Standardize loading placeholders/spinners across data-fetching components.
- [ ] Add retry affordances (button or auto-retry) for failed API calls in the hook/service.

---

### Notes
- Backend changes already merged (Appoinment handling); frontend refactor should remain API-compatible.
- Keep each section in separate commits for easier review.
