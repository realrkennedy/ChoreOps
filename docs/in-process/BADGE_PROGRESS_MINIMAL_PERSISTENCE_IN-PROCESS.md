# Initiative Plan

## Initiative snapshot

- **Name / Code**: Badge progress minimal persistence cleanup
- **Target release / milestone**: `release/0.5.0-beta.5-prep` follow-up hardening
- **Owner / driver(s)**: ChoreOps maintainers + Builder execution handoff
- **Status**: Not started

## Summary & immediate steps

| Phase / Step                         | Description                                                   | % complete | Quick notes                                                      |
| ------------------------------------ | ------------------------------------------------------------- | ---------- | ---------------------------------------------------------------- |
| Phase 1 – Contract + field policy    | Define required vs denormalized `badge_progress` fields       | 0%         | Keep `name` for troubleshooting per owner direction              |
| Phase 2 – Manager + sensor alignment | Move active cycle dates to badge-level source and align reads | 0%         | Badge `start_date`/`end_date` become canonical persisted source  |
| Phase 3 – Migration + tests          | Strip legacy user fields safely and update tests              | 0%         | Move retired constants to migration `_LEGACY` + schema45 cleanup |
| Phase 4 – Docs + validation          | Update architecture/developer docs and run quality gates      | 0%         | Include explicit non-goals and follow-up options                 |

1. **Key objective** – Reduce assignee `badge_progress` to required runtime fields only (plus `name`) while making badge-level schedule dates the single persisted source of truth.
2. **Summary of recent work**
   - Analysis confirmed per-user schedule fields (`start_date`, `end_date`, `recurring_frequency`) are written in `sync_badge_progress_for_assignee` and used in rollover.
   - Analysis confirmed assignee badge-progress sensor currently falls back to badge reset schedule when user fields are missing.
   - Analysis confirmed user reset clears badge runtime fields and can expose sparse progress creation paths.
3. **Next steps (short term)**

- Finalize required field contract for `AssigneeBadgeProgress`.
- Define badge-level active cycle fields (`start_date`/`end_date`) under `badges[*].reset_schedule` as canonical persisted source.
- Draft migration field-removal list, `_LEGACY` constant moves, and schema45 idempotence marker updates.

4. **Risks / blockers**

- Badge-level date ownership requires clear rules for reschedule/schedule-edit behavior to avoid unintended jumps in active cycle windows.
- Existing tests currently assert user `start_date`/`end_date`; those must be intentionally rewritten, not patched ad hoc.
- Dashboard and troubleshooting flows may rely on denormalized fields in unexpected places.

5. **References**
   - `docs/ARCHITECTURE.md`
   - `docs/DEVELOPMENT_STANDARDS.md`
   - `docs/CODE_REVIEW_GUIDE.md`
  - `docs/in-process/BADGE_PROGRESS_MINIMAL_PERSISTENCE_SUP_BUILDER_HANDOFF.md`
   - `tests/AGENT_TEST_CREATION_INSTRUCTIONS.md`
   - `tests/AGENT_TESTING_USAGE_GUIDE.md`
   - `docs/RELEASE_CHECKLIST.md`
   - `docs/PLAN_TEMPLATE.md`
6. **Decisions & completion check**
   - **Decisions captured**:
     - Keep `badge_progress.name` as a persisted troubleshooting field.
     - Directionally remove user-level schedule date persistence from `badge_progress`.
     - Active periodic cycle dates (`start_date`, `end_date`) are persisted on the badge record and treated as canonical source for all users assigned to that badge.
     - Any no-longer-required badge-progress constants are moved out of active runtime constants and into `migration_pre_v50_constants.py` with `_LEGACY` suffix.
   - **Completion confirmation**: `[ ]` All follow-up items completed before owner approval.

## Detailed phase tracking

### Phase 1 – Contract + field policy

- **Goal**: Define a strict minimal `AssigneeBadgeProgress` contract and authoritative source rules.
- **Steps / detailed work items**
  - [ ] Create explicit “required runtime fields” list in planning notes and map each to writer/reader paths using `custom_components/choreops/managers/gamification_manager.py` (~1363-1765, ~4120-4645).
  - [ ] Classify all current persisted badge-progress keys into: keep, remove, derived-from-badge, derived-from-runtime-eval (anchor in `custom_components/choreops/type_defs.py` ~481-540).
  - [ ] Define source-of-truth matrix for schedule values used by rollover/evaluation/sensor output with badge-level canonical ownership (anchor in `custom_components/choreops/managers/gamification_manager.py` ~1421-1530 and `custom_components/choreops/sensor.py` ~2187-2208).
  - [ ] Decide and document exact keep-set for this initiative: include `name`; include only user runtime counters/status needed for evaluation.
  - [ ] Record non-goals for this phase: no separate runtime badge-cycle container; use badge `reset_schedule` dates as persisted cycle source.
- **Key issues**
  - Open-ended periodic windows currently rely on persisted per-user dates; replacement logic must safely transition to badge-level persisted dates.

### Phase 2 – Manager + sensor alignment

- **Goal**: Plan code-path changes so schedule reads use badge-level persisted dates and user progress remains minimal.
- **Steps / detailed work items**
  - [ ] Update sync plan to stop writing denormalized schedule/config fields to user progress in `custom_components/choreops/managers/gamification_manager.py` (~4302-4645), except `name` and required runtime metrics.
  - [ ] Add/adjust manager logic so cycle `start_date` and `end_date` are written and updated in `badges[*].reset_schedule` during initial scheduling, rollover, and reschedule flows in `custom_components/choreops/managers/gamification_manager.py` (~1421-1530, ~4302-4645, ~4690-4830).
  - [ ] Ensure badge schedule edit/reschedule operations update canonical badge-level dates and trigger consistent recomputation for assigned users.
  - [ ] Update sensor plan in `custom_components/choreops/sensor.py` (~2187-2278) to expose schedule from a single authoritative source and avoid mixed fallback semantics.
  - [ ] Review reset impact in `custom_components/choreops/managers/gamification_manager.py` (~5205-5272) to ensure first-write behavior is valid with stripped user fields.
  - [ ] Identify and update any helper/debug endpoints that assume denormalized user schedule fields (search in manager/sensor/tests).
- **Key issues**
  - Existing rollover helper reads user `recurring_frequency`/`end_date`; prerequisite logic must be safely relocated to badge-level schedule reads.

### Phase 3 – Migration + tests

- **Goal**: Plan safe data cleanup and regression coverage for existing installs.
- **Steps / detailed work items**
  - [ ] Add migration checklist for stripping deprecated user badge-progress fields via idempotent schema45 contract hook in `custom_components/choreops/migration_pre_v50.py` (~473-760).
  - [ ] Move any no-longer-required active badge-progress constants from runtime constants to `custom_components/choreops/migration_pre_v50_constants.py`, rename with `_LEGACY`, and update all migration references.
  - [ ] Extend schema45 cleanup routine to remove those retired badge-progress keys from `users[*].badge_progress[*]` in one pass (same process pattern as prior legacy key cleanup).
  - [ ] Update type contract tests and schema45 migration tests in `tests/test_schema45_user_migration.py` (extend existing legacy-field cleanup pattern).
  - [ ] Update behavioral tests in `tests/test_badge_target_types.py` (~448-1320) to assert minimal persisted user keys and badge-level authoritative schedule rendering.
  - [ ] Add explicit reset-path test: user reset → first periodic evaluation persists required runtime fields and no deprecated fields.
  - [ ] Add sensor attribute test: assignee badge-progress schedule attributes come from badge-level canonical dates and do not depend on user `start_date`/`end_date`.
  - [ ] Add schedule-change test: editing/rescheduling a periodic badge updates badge-level `start_date`/`end_date` and all assignee views consistently.
- **Key issues**
  - **Schema version note**: prefer schema45 hook extension with marker (no version bump) if shape change remains backward-compatible; escalate to schema bump only if migration semantics require a hard version checkpoint.

### Phase 4 – Docs + validation

- **Goal**: Ensure maintainability, release safety, and explicit operator guidance.
- **Steps / detailed work items**
  - [ ] Update `docs/ARCHITECTURE.md` with final source-of-truth: badge-level `reset_schedule.start_date/end_date` as canonical persisted cycle window; user progress keeps runtime metrics + `name` only.
  - [ ] Update `docs/DEVELOPMENT_STANDARDS.md` with persistence policy for denormalized badge fields and troubleshooting exception (`name`).
  - [ ] Add release note/checklist entry in `docs/RELEASE_CHECKLIST.md` describing migration behavior and expected post-upgrade state.
  - [ ] Run and document validation commands:
    - [ ] `./utils/quick_lint.sh --fix`
    - [ ] `mypy custom_components/choreops/`
    - [ ] `python -m pytest tests/test_badge_target_types.py tests/test_schema45_user_migration.py -v --tb=line`
    - [ ] `python -m pytest tests/ -v --tb=line` (final confidence run)
- **Key issues**
  - If broader suite reveals unrelated failures, document as external blockers without expanding scope.
