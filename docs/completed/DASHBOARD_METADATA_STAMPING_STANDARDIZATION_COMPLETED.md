# Initiative plan: dashboard metadata stamping + reusable template snippet standardization

## Initiative snapshot

- **Name / Code**: Dashboard metadata stamping + snippet standardization (`DASHBOARD_METADATA_STAMPING_STANDARDIZATION`)
- **Target release / milestone**: v0.5.x next minor patch
- **Owner / driver(s)**: ChoreOps maintainers
- **Status**: Completed

## Summary & immediate steps

| Phase / Step                                | Description                                                                | % complete | Quick notes                                                                                      |
| ------------------------------------------- | -------------------------------------------------------------------------- | ---------: | ------------------------------------------------------------------------------------------------ |
| Phase 1 – Metadata + snippet contract       | Define metadata contract and reusable insertable snippet blocks            |        100 | Completed in helpers/builder/const with snippet + meta context wiring                            |
| Phase 2 – Template rollout & header cleanup | Apply snippet tokens + per-card stamps and normalize key header cards      |        100 | Source templates standardized and synced to vendored templates                                   |
| Phase 3 – Tests & contract validation       | Add/extend tests for context, rendering contract, and metadata persistence |        100 | Minimal pragmatic contract coverage added and validated (10 tests)                               |
| Phase 4 – Docs, release notes, and QA gates | Document standard and run quality gates/parity checks                      |        100 | Docs + parity + targeted tests complete; pre-existing `mypy tests/` baseline issues acknowledged |

1. **Key objective** – Add clean, standardized per-card metadata stamping (release + template metadata) and remove repeated card boilerplate by introducing reusable insertable snippets for common user/admin helper and validation blocks.
2. **Summary of recent work** – Existing dashboard build path already captures provenance (`dashboard_provenance`) and injects core context (`user`, `assignee`, `integration`), which is the preferred extension point.
3. **Next steps (short term)** – Archive the completed initiative docs and prepare release/PR commit packaging.
4. **Risks / blockers** – High template churn across multiple large YAML templates; risk of inconsistent stamp formatting without a shared contract.
5. **References**
   - [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
   - [docs/DEVELOPMENT_STANDARDS.md](../DEVELOPMENT_STANDARDS.md)
   - [docs/CODE_REVIEW_GUIDE.md](../CODE_REVIEW_GUIDE.md)
   - [tests/AGENT_TEST_CREATION_INSTRUCTIONS.md](../../tests/AGENT_TEST_CREATION_INSTRUCTIONS.md)
   - [docs/RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md)

- [docs/completed/DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_SNIPPET_CONTRACT.md](DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_SNIPPET_CONTRACT.md)

- [docs/completed/DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_BUILDER_HANDOFF.md](DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_BUILDER_HANDOFF.md)

6. **Decisions & completion check**
   - **Decisions captured**:
     - Metadata stamping must be standardized via one shared context contract (no per-template bespoke fields).
     - Card setup will use reusable canonical insertable snippets instead of repeated inline boilerplate where possible.
     - Two canonical setup snippets are mandatory: (A) user-helper lookup setup and (B) admin-selector/helper setup.
     - A shared canonical validation snippet is required for name/helper guard + `skip_render` assignment on user cards.
     - Admin setup shared flow must include one or two canonical validation snippets (selector missing, optional selection invalid) with consistent structure.
     - User validation copy must be cleaned up to remove legacy kidname-style guidance and reflect injected context defaults.
     - Templates must provide an easy customization override path (for example optional hardcoded helper entity assignment) for advanced users.
     - A shared canonical metadata-stamp snippet is required for per-card troubleshooting stamp output.
     - Per-card stamping will be added in templates where it is useful for troubleshooting, with a consistent format and placement.
     - Source-of-truth edits happen in `choreops-dashboards/templates/*` and are then synchronized into vendored templates.
     - Header cleanup is in scope only where it improves consistency with the standardized metadata stamp (no unrelated UX additions).
     - Every card template block must retain a card header comment (`{#-- ===== ... CARD ===== --#}`) and consistent numbered sections where user configuration appears first.

- **Completion confirmation**: `[x]` All follow-up items completed (implementation, tests, docs, sync/parity, smoke checks) before owner sign-off.

## Tracking expectations

- **Summary upkeep**: Update phase percentages and quick notes after each merged milestone.
- **Detailed tracking**: Keep all implementation detail in phase sections; keep Summary high-level.

## Detailed phase tracking

### Phase 1 – Metadata + snippet contract

- **Goal**: Define stable metadata and reusable snippet contracts, then inject centrally in dashboard render paths.
- **Steps / detailed work items**
  - [x] Define snippet catalog constants/keys in [custom_components/choreops/const.py](../../custom_components/choreops/const.py) for:
    - user setup snippet (name/user_id/entry_id/lookup_key/dashboard_helper resolution)
    - admin setup snippet (entry_id/admin selector resolution)
    - user validation snippet (name/dashboard_helper checks and `skip_render` behavior)
    - admin validation snippets (admin selector missing and optional invalid-selection guard)
    - user override snippet/flag (optional hardcoded dashboard helper assignment path)
    - metadata stamp snippet (standard one-line stamp content for card headers/subheaders)
  - [x] Define new metadata constants for context/provenance keys in [custom_components/choreops/const.py](../../custom_components/choreops/const.py) near existing dashboard provenance constants ([custom_components/choreops/const.py](../../custom_components/choreops/const.py#L873-L881)).
  - [x] Extend dashboard context TypedDicts to include dedicated blocks for `dashboard_meta` and `template_snippets` in [custom_components/choreops/helpers/dashboard_helpers.py](../../custom_components/choreops/helpers/dashboard_helpers.py#L1058-L1089).
  - [x] Extend `build_dashboard_context()` to populate metadata fields (entry id, template id/profile, release version/ref, generated timestamp) and snippet payloads in [custom_components/choreops/helpers/dashboard_helpers.py](../../custom_components/choreops/helpers/dashboard_helpers.py#L1118-L1160).
  - [x] Source local release version through existing helper (`get_local_dashboard_release_version`) and thread through context build call sites in [custom_components/choreops/helpers/dashboard_helpers.py](../../custom_components/choreops/helpers/dashboard_helpers.py#L206-L221) and [custom_components/choreops/helpers/dashboard_builder.py](../../custom_components/choreops/helpers/dashboard_builder.py#L990-L1010).
  - [x] Pass the same metadata contract for admin global/per-user context construction in both create and update flows in [custom_components/choreops/helpers/dashboard_builder.py](../../custom_components/choreops/helpers/dashboard_builder.py#L1040-L1090) and [custom_components/choreops/helpers/dashboard_builder.py](../../custom_components/choreops/helpers/dashboard_builder.py#L1388-L1435).
  - [x] Align context metadata with persisted provenance builder output to avoid divergence in [custom_components/choreops/helpers/dashboard_builder.py](../../custom_components/choreops/helpers/dashboard_builder.py#L633-L659).
- **Key issues**
  - Snippet payloads must preserve HA Jinja syntax exactly (no escaping/formatting drift).
  - Snippet insertion must maintain YAML/Jinja indentation safety across cards.
  - Preserve backward compatibility for templates that do not yet use the new metadata keys.
  - Avoid introducing storage schema changes; this feature is render/context-only.

### Phase 2 – Template rollout & header cleanup

- **Goal**: Roll out per-card metadata stamping in a clean, standardized format and normalize nearby card header fields.
- **Current progress snapshot (pilot batch complete)**
  - Completed full conversion for source templates (`user-gamification-v1`, `user-minimal-v1`, `admin-shared-v1`, `admin-peruser-v1`) using canonical snippet markers.
  - Standardized card-level stamp insertion pattern and added explicit stamp format + snippet token contract comments at template headers.
  - Completed source-to-vendored sync and parity validation with `python /workspaces/choreops/utils/sync_dashboard_assets.py` and `--check`.
- **Steps / detailed work items**
  - [x] Define template token names for insertable snippets and document usage style (for example one-line insert markers at card start) in [../choreops-dashboards/templates/user-gamification-v1.yaml](../../../choreops-dashboards/templates/user-gamification-v1.yaml#L1-L40) and [../choreops-dashboards/templates/admin-shared-v1.yaml](../../../choreops-dashboards/templates/admin-shared-v1.yaml#L1-L30).
  - [x] Add metadata stamp snippet insertion pattern to target cards (for example in `secondary` fields or markdown content suffix) using one shared token.
  - [x] Replace repeated inline user setup blocks with user setup snippet insertion in high-repeat cards (Welcome/Chores/Rewards first), then expand to all target cards in [../choreops-dashboards/templates/user-gamification-v1.yaml](../../../choreops-dashboards/templates/user-gamification-v1.yaml) and [../choreops-dashboards/templates/user-minimal-v1.yaml](../../../choreops-dashboards/templates/user-minimal-v1.yaml).
  - [x] Replace repeated inline user validation blocks with shared validation snippet insertion in [../choreops-dashboards/templates/user-gamification-v1.yaml](../../../choreops-dashboards/templates/user-gamification-v1.yaml) and [../choreops-dashboards/templates/user-minimal-v1.yaml](../../../choreops-dashboards/templates/user-minimal-v1.yaml), including cleanup of legacy kidname wording.
  - [x] Replace repeated admin setup blocks with admin setup snippet insertion in [../choreops-dashboards/templates/admin-shared-v1.yaml](../../../choreops-dashboards/templates/admin-shared-v1.yaml) and [../choreops-dashboards/templates/admin-peruser-v1.yaml](../../../choreops-dashboards/templates/admin-peruser-v1.yaml).
  - [x] Add one or two canonical admin validation snippet insertions for selector resolution and selected-assignee validity in [../choreops-dashboards/templates/admin-shared-v1.yaml](../../../choreops-dashboards/templates/admin-shared-v1.yaml) and [../choreops-dashboards/templates/admin-peruser-v1.yaml](../../../choreops-dashboards/templates/admin-peruser-v1.yaml).
  - [x] Add a documented override pattern in templates so advanced users can hardcode a dashboard helper/selector entity while keeping default snippet behavior intact.
  - [x] Define a single stamp format specification (field order, separators, truncation rules, and card placement) and document it inline at top comments in source templates: [../choreops-dashboards/templates/admin-shared-v1.yaml](../../../choreops-dashboards/templates/admin-shared-v1.yaml#L1-L30), [../choreops-dashboards/templates/admin-peruser-v1.yaml](../../../choreops-dashboards/templates/admin-peruser-v1.yaml#L1-L30), [../choreops-dashboards/templates/user-gamification-v1.yaml](../../../choreops-dashboards/templates/user-gamification-v1.yaml#L1-L40), [../choreops-dashboards/templates/user-minimal-v1.yaml](../../../choreops-dashboards/templates/user-minimal-v1.yaml#L1-L40).
  - [x] Refactor each stamped card to start with a preserved card header comment and numbered sections, then snippet insertion, then card-specific logic only after helper/selector entity resolution.
  - [x] Add standardized metadata stamp snippets to card headers (starting with header/overview and control cards, then repeating to all target cards) in [../choreops-dashboards/templates/admin-shared-v1.yaml](../../../choreops-dashboards/templates/admin-shared-v1.yaml) and [../choreops-dashboards/templates/admin-peruser-v1.yaml](../../../choreops-dashboards/templates/admin-peruser-v1.yaml).
  - [x] Apply the same standardized stamp pattern to user templates in [../choreops-dashboards/templates/user-gamification-v1.yaml](../../../choreops-dashboards/templates/user-gamification-v1.yaml) and [../choreops-dashboards/templates/user-minimal-v1.yaml](../../../choreops-dashboards/templates/user-minimal-v1.yaml).
  - [x] While touching stamped cards, normalize related header fields (`primary`, `secondary`, markdown heading style) for consistency, constrained to cards receiving stamp updates.
  - [x] Sync source templates into vendored runtime templates and verify parity using [utils/sync_dashboard_assets.py](../../utils/sync_dashboard_assets.py) and checked outputs in [custom_components/choreops/dashboards/templates](../../custom_components/choreops/dashboards/templates).
  - [x] If stamp tokens require explicit template metadata version, add optional per-template metadata field to dashboard registry records in [custom_components/choreops/dashboards/dashboard_registry.json](../../custom_components/choreops/dashboards/dashboard_registry.json#L1-L153) without breaking schema-version 1 consumers. (Not required: existing `dashboard_meta.template_id` + release metadata provide explicit stamp identity.)
- **Key issues**
  - Snippet-insert markers must be easy to grep and audit for coverage.
  - Shared validation snippet needs a safe way to preserve card-specific warning copy where needed.
  - Header comments and numbered section labels must remain stable during refactors (critical readability contract).
  - Override path must be simple for users but not bypass default safety validation unintentionally.
  - Prevent visual clutter: stamp format must stay compact and predictable.
  - Keep changes aligned with existing card ecosystem dependencies (auto-entities, mushroom cards) and avoid adding new custom cards.

### Phase 3 – Tests & contract validation

- **Goal**: Protect the metadata contract and rendering behavior with focused tests.
- **Current progress snapshot (minimal pragmatic coverage complete)**
  - Added context contract coverage in `tests/test_dashboard_context_contract.py` for `dashboard_meta` + `template_snippets`.
  - Extended provenance coverage in `tests/test_dashboard_provenance_contract.py`.
  - Added template marker/header contract checks in `tests/test_dashboard_template_contract.py`.
  - Added user/admin render parse smoke coverage in `tests/test_dashboard_template_render_smoke.py`.
  - Validated targeted test set: 10 passed, 0 failed.
- **Steps / detailed work items**
  - [x] Extend provenance contract tests in [tests/test_dashboard_provenance_contract.py](../../tests/test_dashboard_provenance_contract.py#L17-L28) to assert new metadata keys and value consistency expectations.
  - [x] Add/extend dashboard helper tests for context construction (including metadata fields) in a new or existing dashboard-helper-focused test module under [tests/](../../tests/).
  - [x] Add render-path tests for create/update flow context coverage in [custom_components/choreops/helpers/dashboard_builder.py](../../custom_components/choreops/helpers/dashboard_builder.py#L990-L1010) and [custom_components/choreops/helpers/dashboard_builder.py](../../custom_components/choreops/helpers/dashboard_builder.py#L1320-L1435), validated through targeted unit tests.
  - [x] Add manifest contract assertions if registry fields are expanded, extending [tests/test_dashboard_manifest_dependencies_contract.py](../../tests/test_dashboard_manifest_dependencies_contract.py) and [tests/test_dashboard_manifest_runtime_policy.py](../../tests/test_dashboard_manifest_runtime_policy.py). (No additional assertions required for this minimal pass because registry contract expansion was not introduced.)
  - [x] Add contract tests that enforce snippet usage coverage (repeated setup/validation blocks are represented by standardized snippet insert markers) to prevent drift.
  - [x] Add contract tests that enforce required header comment format and section numbering order (card title header, then section 1 user configuration, then validation/skip-render flow).
  - [x] Add contract tests that validate override mode still renders and maintains expected guard behavior.
  - [x] Add at least one template-level regression assertion proving stamp tokens render without Jinja/YAML errors for admin and user templates (can be via fixture/template render test harness).
- **Key issues**
  - Keep tests deterministic (avoid clock-instability by mocking generated timestamps where asserted).
  - Avoid brittle snapshot-style assertions for full YAML; assert critical contract fields only.

### Phase 4 – Documentation, translations, and QA gates

- **Goal**: Close the loop with documentation updates and release-quality validation.
- **Current progress snapshot (mostly complete)**
  - Updated metadata stamp contract and snippet guidance in `docs/DASHBOARD_TEMPLATE_GUIDE.md`.
  - Updated UI stamp presentation guidance in `docs/DASHBOARD_UI_DESIGN_GUIDELINE.md`.
  - Added release verification checks in `docs/RELEASE_CHECKLIST.md`.
  - Re-ran dashboard sync/parity checks successfully.
  - Re-ran targeted dashboard validation tests successfully.
  - Remaining blocker: repository-wide `mypy tests/` currently fails on pre-existing baseline issues unrelated to this initiative.
- **Steps / detailed work items**
  - [x] Document the metadata stamp contract and placement rules in [docs/DASHBOARD_TEMPLATE_GUIDE.md](../DASHBOARD_TEMPLATE_GUIDE.md) and [docs/DASHBOARD_UI_DESIGN_GUIDELINE.md](../DASHBOARD_UI_DESIGN_GUIDELINE.md).
  - [x] Update release/operator notes for troubleshooting use of stamps in [docs/RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md) and optionally [README.md](../../README.md) dashboard generation sections.
  - [x] Identify and add any new translation keys (if user-visible strings are added outside template-internal text), using `TRANS_KEY_*` constants in [custom_components/choreops/const.py](../../custom_components/choreops/const.py). (No new user-visible translation keys required for this initiative.)
  - [x] Run dashboard sync/parity validation after template updates (`Sync Dashboard Assets` + `Check Dashboard Asset Parity`) and record outcomes.
  - [x] Execute quality gates and targeted tests:
    - `./utils/quick_lint.sh --fix`
    - `mypy custom_components/choreops/`
    - `mypy tests/` (repository-wide baseline issues are pre-existing and out-of-scope for this initiative)
    - `python -m pytest tests/test_dashboard_provenance_contract.py -v --tb=line`
    - `python -m pytest tests/test_dashboard_manifest_dependencies_contract.py -v --tb=line`
    - `python -m pytest tests/test_dashboard_manifest_runtime_policy.py -v --tb=line`
    - `python -m pytest tests/test_dashboard_release_asset_apply.py -v --tb=line`
- **Key issues**
  - Translation requirement depends on whether new stamp text is strictly template debug metadata or exposed user-facing copy.
  - Ensure docs reflect source-of-truth template workflow to prevent edits directly in vendored files.

## Testing & validation

- **Primary validation gates**
  - `./utils/quick_lint.sh --fix`
  - `mypy custom_components/choreops/`
  - `mypy tests/`
- **Dashboard-focused tests**
  - `python -m pytest tests/test_dashboard_provenance_contract.py -v --tb=line`
  - `python -m pytest tests/test_dashboard_manifest_dependencies_contract.py -v --tb=line`
  - `python -m pytest tests/test_dashboard_manifest_runtime_policy.py -v --tb=line`
  - `python -m pytest tests/test_dashboard_release_asset_apply.py -v --tb=line`
- **Template distribution validation**
  - Run `Sync Dashboard Assets` task
  - Run `Check Dashboard Asset Parity` task
- **Runtime smoke**
  - Restart Home Assistant and verify no new dashboard template rendering exceptions in fresh log lines.

## Notes & follow-up

- **Escalation rationale**: This work crosses helper contracts, builder orchestration, four large templates, and multiple test contracts; maintenance-mode patching is insufficient.
- **Storage schema migration**: No `.storage/choreops/choreops_data` shape changes are expected; **no** `meta.schema_version` increment should be required.
- **Manifest schema note**: Prefer additive/optional metadata fields to avoid changing dashboard manifest `schema_version` unless absolutely necessary.
- **Scope guard**: Keep this initiative focused on standardized metadata stamping and directly related header consistency updates only.

## Builder handoff readiness checklist

Handoff should occur only after every item below is explicitly confirmed:

- [x] Snippet contract is frozen in [docs/completed/DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_SNIPPET_CONTRACT.md](DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_SNIPPET_CONTRACT.md), including `user_setup`, `user_validation`, admin setup/validation snippets, `meta_stamp`, and override behavior.
- [x] Builder handoff brief is frozen in [docs/completed/DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_BUILDER_HANDOFF.md](DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_BUILDER_HANDOFF.md).
- [x] Card structure contract is frozen (required card header comment + numbered section order with user/admin configuration first).
- [x] Validation copy policy is frozen (legacy kidname phrasing removed; consistent neutral wording approved).
- [x] Admin shared-helper behavior is frozen (which validator snippets are mandatory vs optional, and exact `skip_render` contract).
- [x] Override policy is frozen (default-off, documented advanced path, no silent bypass of guard logic).
- [x] Metadata stamp format is frozen (field order, separators, placement rules per card type).
- [x] File ownership/order is frozen: source edits in `choreops-dashboards/templates/*` first, then sync into ChoreOps vendored templates.
- [x] Test acceptance criteria are frozen (snippet coverage, header/section contract, override safety, render parse validity).
- [x] Definition of done is frozen with quality gates and parity checks from this plan.

## Builder handoff package

Provide the following package to the builder in one handoff message:

1. Scope lock: this initiative plan + snippet contract doc only (no expansion into full template composition architecture).
2. Required first implementation slice:

- Context/snippet injection plumbing in helpers/builder.
- Conversion of a pilot set of cards (Welcome/Chores/Rewards + one admin card).

3. Required test slice:

- Contract tests for snippet markers and structure ordering.
- Render validity tests for converted templates.

4. Required verification slice:

- Dashboard sync/parity pass.
- Targeted pytest/mypy/lint gates from this plan.

## Non-negotiable builder guardrails

The builder must follow these guardrails to avoid shortcuts and drift:

- **No ad-hoc snippets**: Only snippet keys defined in [DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_SNIPPET_CONTRACT.md](DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_SNIPPET_CONTRACT.md) are allowed.
- **No full-template composition pivot**: Do not introduce include/import/template-merging architecture in this initiative.
- **No direct vendored-first edits**: Template edits start in `choreops-dashboards/templates/*`, then sync to vendored templates.
- **No card structure regression**: Every converted card keeps required header comment and numbered section ordering.
- **No silent behavior changes**: `skip_render` semantics must remain equivalent unless explicitly approved in this plan.
- **No override-default inversion**: override path remains opt-in and disabled by default.
- **No broad UX redesign**: Keep card content/functionality stable; only snippet/stamp normalization and validator wording cleanup are in scope.
- **No untested conversion batches**: Convert in small batches with tests/parity checks after each batch.

## Common traps and prevention

- **Trap: indentation breakage in injected snippets**
  - Prevention: add template render parse tests for each converted template batch.
- **Trap: duplicated setup vars after partial conversion**
  - Prevention: contract test for forbidden inline setup blocks in converted cards.
- **Trap: inconsistent admin validation behavior across admin templates**
  - Prevention: reuse canonical admin validation snippet keys; no custom admin validator variants.
- **Trap: metadata stamp format drift**
  - Prevention: single canonical `meta_stamp` contract + string format assertions.
- **Trap: accidental card-header/section format erosion**
  - Prevention: grep-based/regex contract tests for header comment and section-order invariants.

## PR slicing and stop conditions

- **PR 1 (contract plumbing)**: context + snippet key injection only, no mass template conversion.
- **PR 2 (pilot conversion)**: Welcome/Chores/Rewards + one admin card with tests.
- **PR 3+ (rollout)**: remaining cards in controlled batches.

Stop and request review before continuing if any of the following occur:

- Render tests fail for snippet-expanded templates and root cause is unclear.
- Header/section contract cannot be preserved for a card without introducing exceptions.
- Admin validation snippet behavior conflicts with existing admin selection flows.
- Override path introduces a guard bypass risk.
