# Builder handoff brief: dashboard metadata stamping + snippet standardization

## Scope lock

Builder scope is strictly limited to:

1. Reusable snippet injection plumbing for dashboard templates
2. Metadata stamp snippet support
3. Template conversion to snippet markers
4. Validator wording cleanup and admin validation consistency
5. Optional advanced override path (default disabled)

Out of scope:

- Full template composition architecture
- New card types/components
- Broad UX redesign of card content

## Source of truth

- Main plan: [DASHBOARD_METADATA_STAMPING_STANDARDIZATION_IN-PROCESS.md](DASHBOARD_METADATA_STAMPING_STANDARDIZATION_IN-PROCESS.md)
- Snippet contract: [DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_SNIPPET_CONTRACT.md](DASHBOARD_METADATA_STAMPING_STANDARDIZATION_SUP_SNIPPET_CONTRACT.md)

## Execution order (mandatory)

1. Implement snippet/context plumbing in helpers/builder.
2. Add/adjust tests for snippet/context contracts.
3. Convert pilot cards:
   - user `WELCOME`
   - user `CHORES`
   - user `REWARDS`
   - one admin card (`APPROVAL ACTIONS` preferred)
4. Run validation gates + parity check.
5. Continue rollout in small batches.

## Hard constraints

- Preserve card header comments:
  - `{#-- ===== <CARD NAME> CARD ===== --#}`
- Preserve numbered section ordering:
  - section 1 configuration/setup
  - validation + `skip_render`
  - data collection and render
- Use canonical snippet keys only.
- Keep override disabled by default.
- Keep admin validator behavior consistent across admin templates.

## Forbidden shortcuts

- Copy/paste custom variants of canonical snippets.
- Converting cards without adding/updating contract tests.
- Editing vendored templates first.
- Removing or flattening section comments to speed conversion.
- Altering card functional logic unless required by snippet insertion.

## Acceptance criteria

- Snippet keys exist and are injected from centralized context.
- Pilot converted cards render successfully with no YAML/Jinja failures.
- Header/section contract checks pass.
- Admin validation snippets behave consistently (missing selector and optional invalid-selection checks).
- User validation copy no longer uses legacy kidname guidance.
- Override path exists and is disabled by default.
- Metadata stamp appears in approved placement with canonical format.
- Sync/parity passes between source and vendored templates.

## Required handback from builder

Provide all of the following in handback:

1. Changed file list grouped by helper/builder/templates/tests.
2. Proof of pilot card conversion coverage.
3. Test command outputs for required suites.
4. Parity validation outcome.
5. Explicit note of any exceptions to snippet/card structure contract.
