# Builder handoff plan

## Initiative

- **Parent plan**: `docs/in-process/BADGE_PROGRESS_MINIMAL_PERSISTENCE_IN-PROCESS.md`
- **Execution owner**: ChoreOps Builder
- **Intent**: Implement minimal assignee badge progress persistence, relocate retired constants to migration-only legacy constants, and make badge-level start/end cycle dates the canonical persisted source.

## Locked requirements (do not change during implementation)

1. Keep `badge_progress.name` persisted for troubleshooting.
2. Move no-longer-required badge progress constants to `custom_components/choreops/migration_pre_v50_constants.py` with `_LEGACY` suffix.
3. Extend schema45 badge-progress cleanup to remove all retired badge-progress fields in one idempotent pass.
4. Persist active periodic cycle `start_date`/`end_date` on badge data (`badges[*].reset_schedule`) as single source of truth.
5. Assignee badge-progress sensor must read schedule from badge-level canonical dates (no mixed-source ambiguity).

## Scope and non-scope

### In scope

- `AssigneeBadgeProgress` contract minimization.
- Gamification manager schedule ownership shift from user progress to badge reset schedule.
- Schema45 migration cleanup extension for retired badge-progress keys.
- Test updates and additions for reset path, schedule updates, and sensor consistency.

### Out of scope

- New runtime badge-cycle container/model.
- Unrelated refactors in challenges/achievements/rewards.
- Dashboard template behavior changes.

## Implementation matrix: keep vs retire (builder baseline)

### Keep in user `badge_progress`

- `name`
- `status`
- `overall_progress`
- `criteria_met`
- `last_update_day`
- `points_cycle_count`
- `chores_cycle_count`
- `days_cycle_count`
- `chores_completed`
- `days_completed`

### Retire from user `badge_progress` (migrate + cleanup)

- `recurring_frequency`
- `start_date`
- `end_date`
- `cycle_count` (if moved to badge-level cycle ownership)
- `target_type`
- `threshold_value`
- `badge_type`
- `tracked_chores`
- `occasion_type`
- `associated_achievement`
- `associated_challenge`

### Badge-level canonical schedule fields

- `badges[*].reset_schedule.recurring_frequency` (config + runtime-consumed)
- `badges[*].reset_schedule.start_date` (active cycle start)
- `badges[*].reset_schedule.end_date` (active cycle end)
- `badges[*].reset_schedule.custom_interval`
- `badges[*].reset_schedule.custom_interval_unit`

## Phase execution plan

## Phase 1 — Contract and constants alignment

**Goal**: finalize field contract and legacy constant ownership before behavior edits.

- [ ] Step 1.1 — Update `AssigneeBadgeProgress` type contract to minimal persisted shape in `custom_components/choreops/type_defs.py` (~481-540).
- [ ] Step 1.2 — Identify active badge-progress constants to retire in `custom_components/choreops/const.py` (~1001-1021).
- [ ] Step 1.3 — Add `_LEGACY` replacements for retired keys in `custom_components/choreops/migration_pre_v50_constants.py` (append near existing `DATA_USER_BADGE_PROGRESS_PENALTY_APPLIED_LEGACY`).
- [ ] Step 1.4 — Update migration import map in `custom_components/choreops/migration_pre_v50.py` (imports near file top).

**Checkpoint A (must pass before Phase 2)**

- [ ] No runtime code references retired constants from `const.py` except compatibility handling explicitly delegated to migration.
- [ ] Type hints remain complete; no new `# type: ignore` added for avoidable cases.

## Phase 2 — Manager logic: badge-level schedule authority

**Goal**: move cycle date writes/reads to badge-level `reset_schedule`, minimize assignee writes.

- [ ] Step 2.1 — Refactor `sync_badge_progress_for_assignee` in `custom_components/choreops/managers/gamification_manager.py` (~4120-4645) to stop persisting retired denormalized user fields while keeping `name` and runtime counters/status.
- [ ] Step 2.2 — Refactor `_ensure_assignee_periodic_badge_structures` in `custom_components/choreops/managers/gamification_manager.py` (~1363-1419) to avoid reintroducing retired fields.
- [ ] Step 2.3 — Refactor `_advance_non_cumulative_badge_cycle_if_needed` in `custom_components/choreops/managers/gamification_manager.py` (~1421-1529) to read and update cycle dates on badge `reset_schedule` instead of user `badge_progress`.
- [ ] Step 2.4 — Ensure badge create/update/reschedule paths keep canonical schedule dates synchronized in `custom_components/choreops/managers/gamification_manager.py` (~4690-4830).
- [ ] Step 2.5 — Verify data reset behavior in `custom_components/choreops/managers/gamification_manager.py` (~5205-5272) does not require user date fields to rehydrate schedule.

**Checkpoint B (must pass before Phase 3)**

- [ ] Single schedule source confirmed in manager logic: badge `reset_schedule.start_date/end_date`.
- [ ] No evaluation path depends on user `start_date/end_date/recurring_frequency`.
- [ ] Manager write ownership remains compliant (all writes inside manager methods only).

## Phase 3 — Sensor and read-model consistency

**Goal**: eliminate mixed-source sensor behavior and keep debugging clarity.

- [ ] Step 3.1 — Update assignee badge-progress sensor schedule assembly in `custom_components/choreops/sensor.py` (~2187-2208) to read canonical badge schedule only.
- [ ] Step 3.2 — Keep `name` troubleshooting visibility intact in `custom_components/choreops/sensor.py` (~2229-2255).
- [ ] Step 3.3 — Verify no other sensor attribute builders use retired user schedule fields (search and update in `custom_components/choreops/sensor.py`).

**Checkpoint C (must pass before Phase 4)**

- [ ] Sensor output cannot silently switch between user and badge schedule sources.
- [ ] Assignee badge-progress attributes remain stable and understandable for troubleshooting.

## Phase 4 — Migration hardening and idempotence

**Goal**: safely strip retired fields in existing installs with schema45-compatible migration hooks.

- [ ] Step 4.1 — Extend `_remove_schema45_legacy_badge_progress_fields` in `custom_components/choreops/migration_pre_v50.py` (~473-499) to remove all retired user badge-progress keys.
- [ ] Step 4.2 — Add/extend schema45 summary counters and marker behavior in `custom_components/choreops/migration_pre_v50.py` (~705-760).
- [ ] Step 4.3 — Confirm migration uses `_LEGACY` constants from `custom_components/choreops/migration_pre_v50_constants.py` only.

**Checkpoint D (must pass before Phase 5)**

- [ ] Migration is idempotent (second pass is no-op).
- [ ] Marker/summaries are deterministic and testable.

## Phase 5 — Tests and platinum gate validation

**Goal**: prove functional correctness and standards compliance.

- [ ] Step 5.1 — Update existing badge behavior tests in `tests/test_badge_target_types.py` (~448-1320) for canonical badge schedule expectations.
- [ ] Step 5.2 — Add reset-path regression test in `tests/test_badge_target_types.py`: user reset + first evaluation persists required runtime fields only.
- [ ] Step 5.3 — Add schedule-change/reschedule test in `tests/test_badge_target_types.py`: badge-level `start_date/end_date` update and all assignee views align.
- [ ] Step 5.4 — Extend migration tests in `tests/test_schema45_user_migration.py` (~462+) for each retired user field removal and idempotence.
- [ ] Step 5.5 — Add sensor assertion coverage in `tests/test_badge_target_types.py` for single-source reset schedule attributes.

**Checkpoint E (release-ready quality gate)**

- [ ] `./utils/quick_lint.sh --fix`
- [ ] `mypy custom_components/choreops/`
- [ ] `mypy tests/`
- [ ] `python -m pytest tests/test_badge_target_types.py tests/test_schema45_user_migration.py -v --tb=line`
- [ ] `python -m pytest tests/ -v --tb=line`

## Platinum quality compliance checklist (from development standards)

- [ ] **Type hints**: updated functions and variables are fully typed; no avoidable suppressions.
- [ ] **Docstrings**: all changed public functions/methods include accurate docstrings.
- [ ] **No hardcoded user-facing strings**: use constants + translation keys.
- [ ] **Lazy logging only**: no f-strings in logs.
- [ ] **Manager write ownership**: no writes from `services.py`/`options_flow.py`.
- [ ] **Signal-first architecture**: no direct cross-manager write coupling introduced.
- [ ] **DateTime helpers**: use `dt_*` helpers; no raw datetime arithmetic in changed paths.
- [ ] **Architecture boundaries**: no HA imports in `utils/` or `engines/` due to this initiative.

## Builder guardrails and anti-regression notes

- Do not rename existing public service names or entity IDs as part of this initiative.
- Do not introduce runtime badge-cycle storage model in this pass.
- Keep changes surgical: only schedule authority + badge_progress minimization + migration/test updates.
- If a required field removal causes unexpected UI/report breakage, document exact dependency and pause for owner decision.

## Deliverables expected from builder handoff

1. Code changes in manager/sensor/migration/type defs consistent with locked requirements.
2. Updated/added tests proving:
   - canonical badge-level cycle date ownership,
   - no mixed-source sensor schedule output,
   - schema45 cleanup of all retired keys,
   - reset-path correctness.
3. Validation output summary including all checkpoint commands.
4. Short implementation note in parent plan status table with completion percentages updated.
