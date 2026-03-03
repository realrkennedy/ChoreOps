# Initiative plan: Dashboard UX modernization + rapid design iteration

## Initiative snapshot

- **Name / Code**: Dashboard UX modernization + rapid design iteration (`DASHBOARD_UX_MODERNIZATION`)
- **Target release / milestone**: v0.5.x dashboard UX track (multi-PR)
- **Owner / driver(s)**: ChoreOps maintainers + dashboard design/build contributors
- **Status**: In progress

## Summary & immediate steps

| Phase / Step                                | Description                                                                                  | % complete | Quick notes                                                   |
| ------------------------------------------- | -------------------------------------------------------------------------------------------- | ---------: | ------------------------------------------------------------- |
| Phase 1 – UX foundation + tooling           | Create UX-focused dashboard builder agent and standardize template naming/version strategy   |        100 | Completed: agent created, boundaries codified, toolkit linked |
| Phase 2 – Dev preload workflow              | Make rapid local dashboard testing easy using scenario-based live preload tooling            |        100 | Completed: script modernized + docs + targeted tests          |
| Phase 3 – User template modernization       | Build modern minimal-v2 first (header + chores), then gamification-v2 from reusable patterns |          0 | Keep existing v1 templates intact                             |
| Phase 4 – Admin modernization + docs/polish | Modernize admin templates and finalize docs/contracts/validation checklist                   |          0 | Align with template and UI guidelines                         |

1. **Key objective** – Deliver modern, app-like dashboards while preserving existing templates and runtime stability.
2. **Summary of recent work** – Completed Phase 2 preload workflow: modernized live scenario loader, added seeded UX state-driver scenario coverage (waiting/due/overdue), and updated utility/dashboard documentation for repeatable local UX loops.
3. **Next steps (short term)** – Start Phase 3 (user template modernization: additive `*-v2` templates) while keeping v1 templates unchanged.
4. **Risks / blockers**
   - Home Assistant dashboard constraints (no custom card authoring in this initiative) can limit advanced interaction patterns.
   - Dependency drift risk when introducing new custom card usage across templates.
   - Rapid design iteration may create contract drift unless canonical-vendored sync is enforced each cycle.
5. **References**
   - `docs/ARCHITECTURE.md`
   - `docs/DEVELOPMENT_STANDARDS.md`
   - `docs/CODE_REVIEW_GUIDE.md`
   - `tests/AGENT_TEST_CREATION_INSTRUCTIONS.md`
   - `docs/RELEASE_CHECKLIST.md`
   - `docs/DASHBOARD_TEMPLATE_GUIDE.md`
   - `docs/DASHBOARD_UI_DESIGN_GUIDELINE.md`
   - `docs/in-process/DASHBOARD_UX_MODERNIZATION_SUP_DASHBOARD_BUILDER_AGENT_DRAFT.md`
   - `docs/in-process/DASHBOARD_UX_MODERNIZATION_SUP_CARD_TOOLKIT.md`
6. **Decisions & completion check**
   - **Decisions captured**:
     - Keep all current template IDs and files unchanged (v1 remains supported).
     - Introduce new templates as additive v2 IDs, validated by existing registry/runtime contracts.
     - Prioritize reusable card fragments/patterns from minimal-v2 into gamification-v2.
     - Do not build a new custom card in this initiative; rely on existing ecosystem cards only.
   - **Completion confirmation**: `[ ]` All follow-up items completed (agent + preload + templates + docs + parity + validation) before owner sign-off.

> **Important:** Keep this Summary table current after each phase-level implementation milestone.

## Tracking expectations

- **Summary upkeep**: Update percentages, blockers, and quick notes after each phase completion.
- **Detailed tracking**: Keep implementation granularity in phase sections; keep Summary high-level.

## Detailed phase tracking

### Phase 1 – UX foundation + tooling

- **Goal**: Establish execution framework and naming/version contracts for UX-first dashboard work before template changes.
- **Steps / detailed work items** 1. [x] Create new UX-focused implementation agent file using the builder frontmatter/workflow baseline from `.github/agents/builder.agent.md` (lines 1-96), but tuned for dashboard UX iteration and HA Lovelace constraints.
  **Files**: `.github/agents/builder.agent.md` (source pattern), `.github/agents/dashboard-ux-builder.agent.md` (new).
  **Line anchors**: source frontmatter/workflow in `builder.agent.md` lines 1-96. 2. [x] Add explicit UX-agent guardrails for: no custom card development, only template/config-driven UX changes, strict dependency declaration updates in registry when `custom:*` usage changes.
  **Files**: `.github/agents/dashboard-ux-builder.agent.md`, `tests/test_dashboard_manifest_dependencies_contract.py`.
  **Line anchors**: dependency contract test expectations lines 33-152. 3. [x] Define and ratify additive naming strategy for new templates (`*-v2`) while preserving current `*-v1` IDs and regex compatibility.
  **Files**: `docs/DASHBOARD_TEMPLATE_GUIDE.md`, `custom_components/choreops/helpers/dashboard_helpers.py`.
  **Line anchors**: naming pattern in guide (new template section + structure) lines 152-260, template ID regex in `dashboard_helpers.py` line 87. 4. [x] Document UX iteration acceptance criteria (visual quality + usability + HA practicality) and tie them to state-channel requirements from UI guideline.
  **Files**: `docs/DASHBOARD_UI_DESIGN_GUIDELINE.md`, `docs/DASHBOARD_TEMPLATE_GUIDE.md`.
  **Line anchors**: state communication + styling rules in UI guideline lines 13-101. 5. [x] Add official handoff/update path so the new UX agent can pass completed plan phases back to Builder without bypassing existing phase-confirmation workflow.
  **Files**: `.github/agents/dashboard-ux-builder.agent.md`, `.github/agents/strategist.agent.md`.
  **Line anchors**: existing strategist handoff contract lines 1-18.
- **Key issues**
  - Agent instructions must remain precise enough for fast iteration but not conflict with established quality gates.
  - Naming strategy must preserve compatibility with `_VALID_TEMPLATE_ID_RE` and release-selection behavior.

### Phase 2 kickoff handoff packet (ready)

- **Agent**: `.github/agents/dashboard-ux-builder.agent.md`
- **Scope to execute first**: Phase 2, Step 1 only (modernize live preload script path/domain assumptions)
- **Primary files**: - `utils/load_test_scenario_to_live_ha.py` - `utils/README.md`
- **Hard constraints**: - Template source edits only in `choreops-dashboards/templates/*` - Dashboard translation source edits only in `choreops-dashboards/translations/en_dashboard.json` - Sync to vendored runtime when testing requires local runtime visibility
- **Validation for this kickoff step**: - `./utils/quick_lint.sh --fix` - targeted tests as applicable to changed utility logic
- **Expected completion output**: - updated plan checkbox for Phase 2 Step 1 - concise report: files changed, validations, blockers/next step

### Local sandbox auth (development only)

- **Dev instance token (sandbox)**:
       `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkMTg1MzVmMWRkOTg0OGUyOTNiNmI5OWY4ODc2NTc1MyIsImlhdCI6MTc3MjU1OTc0NywiZXhwIjoyMDg3OTE5NzQ3fQ.Bk0f4R062GzJifL_It2ybOd7Eu5iGRrOhZPoQHIAJEM`

### Phase 2 – Dev preload workflow

- **Goal**: Enable one-command(ish) local data preloading for dashboard UX testing using existing scenario logic.
- **Steps / detailed work items**
  1. [x] Modernize live preload script to current repository/domain conventions (`choreops` vs legacy `kidschores`) and scenario file locations.
         **Files**: `utils/load_test_scenario_to_live_ha.py`, `utils/README.md`.
         **Line anchors**: legacy paths/domain usage in script lines 1-48 and 81-112; README references lines 7-33.
  2. [x] Add CLI arguments for scenario selection (`tests/scenarios/scenario_minimal.yaml`, `scenario_full.yaml`, etc.), HA URL, and non-interactive token input via env var for repeatable local cycles.
         **Files**: `utils/load_test_scenario_to_live_ha.py`, `tests/scenarios/` YAML files.
         **Line anchors**: parser currently only supports `--reset` in script lines 266-279.
  3. [x] Align payload mapping to current options-flow field names/menu selections using reusable constants/flow contracts where feasible.
         **Files**: `utils/load_test_scenario_to_live_ha.py`, `custom_components/choreops/options_flow.py`.
         **Line anchors**: dashboard/options flow structure around lines 3818-4717; script entity-add flow lines 114-257.
  4. [x] Add dry-run/validation mode to verify scenario structure and intended operations before mutating live instance.
         **Files**: `utils/load_test_scenario_to_live_ha.py`, `tests/helpers/setup.py`.
         **Line anchors**: canonical scenario loader model in `setup.py` lines 1-220 and schema helpers lines 82-162.
  5. [x] Add usage documentation for UX iteration loops (reset/load/switch template/reload dashboard) including known limitations and safety notes.
         **Files**: `utils/README.md`, `docs/DASHBOARD_TEMPLATE_GUIDE.md`.
         **Line anchors**: utils usage block lines 7-33; guide workflow lines 67-85.
  6. [x] Add targeted tests for any new parser/helper logic extracted from live preload script (pure helper functions only; no live-HA calls in unit tests).
         **Files**: `tests/test_dashboard_*` (new/updated), optional `tests/helpers/*` helper test module.
         **Line anchors**: dashboard smoke/contract patterns in `tests/test_dashboard_template_render_smoke.py` lines 1-47.
- **Key issues**
  - Existing script is a dev utility with legacy assumptions; modernization should avoid introducing runtime coupling to test-only helpers.
  - Need safe defaults to avoid destructive resets in unintended instances.

### Phase 3 – User template modernization

- **Goal**: Deliver additive modern user templates by piloting minimal-v2 and reusing proven blocks in gamification-v2.
- **Steps / detailed work items**
  1. [ ] Create new canonical minimal template variant (`user-minimal-v2.yaml`) as additive file; keep `user-minimal-v1.yaml` unchanged.
         **Files**: `choreops-dashboards/templates/user-minimal-v1.yaml`, `choreops-dashboards/templates/user-minimal-v2.yaml` (new).
         **Line anchors**: existing minimal template header/card structure lines 1-50.
  2. [ ] Implement modernized **header card** and **chores card** in minimal-v2 using guideline state channels, preserving dynamic helper lookup/snippet contracts and metadata stamp placement.
         **Files**: `choreops-dashboards/templates/user-minimal-v2.yaml`, `docs/DASHBOARD_UI_DESIGN_GUIDELINE.md`.
         **Line anchors**: snippet/stamp rules in template guide lines 212-260; UI state model lines 17-101.
  3. [ ] Register minimal-v2 in canonical registry with accurate dependency declarations (required/recommended) and preference doc linkage.
         **Files**: `choreops-dashboards/dashboard_registry.json`, `choreops-dashboards/preferences/user-minimal-v2.md` (new).
         **Line anchors**: existing template registry contract lines 1-125.
  4. [ ] Build gamification-v2 by reusing minimal-v2 card patterns/snippets where practical; update only the cards needed to modernize layout and interactions first.
         **Files**: `choreops-dashboards/templates/user-gamification-v1.yaml`, `choreops-dashboards/templates/user-gamification-v2.yaml` (new).
         **Line anchors**: current gamification template baseline lines 1-50.
  5. [ ] Register gamification-v2 + preferences and ensure dependency declarations cover all `custom:*` usage.
         **Files**: `choreops-dashboards/dashboard_registry.json`, `choreops-dashboards/preferences/user-gamification-v2.md` (new).
         **Line anchors**: dependency contract expectations in test file lines 33-152.
  6. [ ] Sync canonical assets into vendored runtime mirror and verify parity before any integration-side flow/testing updates.
         **Files**: `utils/sync_dashboard_assets.py` (execution), `custom_components/choreops/dashboards/*` (synced outputs).
         **Line anchors**: required sync/parity workflow in template guide lines 67-85.
- **Key issues**
  - Must keep all templates as single-view outputs and preserve dual Jinja delimiter rules.
  - New visual complexity must remain performant in HA dashboard runtime.

### Phase 4 – Admin modernization + docs/polish

- **Goal**: Modernize admin templates with the same UX language and finalize docs/tests/options-flow readiness for production use.
- **Steps / detailed work items**
  1. [ ] Add additive admin variants (`admin-shared-v2.yaml`, `admin-peruser-v2.yaml`) with modernized header/action cards and preserved selector/helper validation flows.
         **Files**: `choreops-dashboards/templates/admin-shared-v2.yaml` (new), `choreops-dashboards/templates/admin-peruser-v2.yaml` (new).
         **Line anchors**: current admin baselines lines 1-50 in both v1 templates.
  2. [ ] Register admin v2 templates in canonical registry with dependency declarations and preference docs; ensure admin mode routing remains compatible.
         **Files**: `choreops-dashboards/dashboard_registry.json`, `choreops-dashboards/preferences/admin-shared-v2.md` + `admin-peruser-v2.md` (new).
         **Line anchors**: admin template IDs and contracts in registry lines 69-125.
  3. [ ] Validate template-select behavior and defaults in integration helper logic (especially default admin template selection and template normalization) for mixed v1/v2 availability.
         **Files**: `custom_components/choreops/helpers/dashboard_helpers.py`, `custom_components/choreops/options_flow.py`.
         **Line anchors**: default admin template selectors at `dashboard_helpers.py` lines 985-1008; configure step in `options_flow.py` lines 4081-4636.
  4. [ ] Expand/adjust dashboard tests for render smoke, registry/dependency contracts, and flow selection behavior with new template IDs.
         **Files**: `tests/test_dashboard_template_render_smoke.py`, `tests/test_dashboard_manifest_dependencies_contract.py`, `tests/test_options_flow_dashboard_release_selection.py` (and related dashboard flow tests).
         **Line anchors**: smoke render tests lines 1-47; dependency contract lines 33-152.
  5. [ ] Update dashboard docs with v2 naming, migration guidance, and UX design constraints (including HA practical limitations and “no custom card development” scope).
         **Files**: `docs/DASHBOARD_TEMPLATE_GUIDE.md`, `docs/DASHBOARD_UI_DESIGN_GUIDELINE.md`, optional wiki pages in `choreops-wiki/` for user-facing rollout notes.
         **Line anchors**: guide authority/workflow sections lines 9-85; UI guideline scope/state sections lines 6-101.
  6. [ ] Perform final parity + quality gate checklist and capture release readiness notes.
         **Files**: `docs/RELEASE_CHECKLIST.md`, `docs/in-process/DASHBOARD_UX_MODERNIZATION_IN-PROCESS.md` (this file updates).
         **Line anchors**: update Summary table and phase statuses in this plan after each completed gate.
- **Key issues**
  - Introducing multiple v2 templates may require clear UX labeling to avoid user confusion in template selectors.
  - Admin modernization must keep actionable clarity for high-density operational tasks.

## Validation commands (execution phase requirements)

Run during implementation phases (Builder/UX Builder):

1. `python utils/sync_dashboard_assets.py`
2. `python utils/sync_dashboard_assets.py --check`
3. `./utils/quick_lint.sh --fix`
4. `mypy custom_components/choreops/`
5. `python -m pytest tests/ -v --tb=line`
6. Focused dashboard regression pass (recommended):
   `python -m pytest tests/test_dashboard_template_render_smoke.py tests/test_dashboard_manifest_dependencies_contract.py tests/test_dashboard_template_contract.py -v --tb=line`

## Migration and schema impact

- **Storage schema change required**: **No**.
- **`meta.schema_version` increment required**: **No** (dashboard/templates/docs/utilities only; no `.storage/choreops/choreops_data` schema changes).
- **Compatibility note**: Maintain template ID regex compatibility (`^[a-z0-9]+-[a-z0-9-]+-v[0-9]+$`) and additive template introduction strategy.

## Translation keys (planned usage)

Re-use existing dashboard translation constants in `custom_components/choreops/const.py` where applicable:

- `TRANS_KEY_CFOF_DASHBOARD_TEMPLATE_PROFILE` (line 3370)
- `TRANS_KEY_CFOF_DASHBOARD_ADMIN_MODE` (line 3383)
- `TRANS_KEY_CFOF_DASHBOARD_ADMIN_TEMPLATE_GLOBAL` (line 3384)
- `TRANS_KEY_CFOF_DASHBOARD_ADMIN_TEMPLATE_PER_ASSIGNEE` (line 3387)
- `TRANS_KEY_CFOF_DASHBOARD_RELEASE_SELECTION` (line 3393)
- `TRANS_KEY_EXC_DASHBOARD_STATUS_UPDATED` (line 3420)
- `TRANS_KEY_EXC_DASHBOARD_STATUS_CREATED` (line 3421)
- `TRANS_KEY_EXC_DASHBOARD_STATUS_RECOMMENDED_DEPS_MISSING` (line 3428)

If new user-facing options/status text is introduced for UX iteration workflow, add new `TRANS_KEY_*` constants + `translations/en.json` entries in the same PR.

## Deliverables checklist

- [x] New agent spec created for dashboard UX implementation (`.github/agents/dashboard-ux-builder.agent.md`)
- [x] Live preload utility modernized for scenario-based local testing
- [ ] New additive user templates: minimal-v2 + gamification-v2
- [ ] New additive admin templates: shared-v2 + peruser-v2
- [ ] Registry/preferences/translations updated in canonical dashboard repo
- [ ] Vendored assets synced + parity verified
- [ ] Dashboard tests updated and passing
- [x] Dashboard docs updated (template guide + UI guideline + release notes) — foundational boundary/contract updates completed in Phase 1
