# Supporting spec: reusable dashboard snippet contract

## Purpose

This support document defines the exact reusable snippet payloads for repeated card boilerplate in dashboard templates.

Scope of reuse:

1. User helper setup block
2. Admin helper/select setup block(s)
3. User validation block (`name` + helper availability)
4. Metadata stamp block (standard one-line troubleshooting stamp)
5. Admin validation block(s)
6. Optional user override block(s)

These snippets are intended to be inserted into card template bodies via centralized context injection at dashboard generation time.

## Token naming contract

Use a dedicated `template_snippets` context object, with stable keys:

- `template_snippets.user_setup`
- `template_snippets.user_validation`
- `template_snippets.admin_setup_shared`
- `template_snippets.admin_setup_peruser`
- `template_snippets.meta_stamp`
- `template_snippets.admin_validation_missing_selector`
- `template_snippets.admin_validation_invalid_selection`
- `template_snippets.user_override_helper` (optional)

Optional future additions (not required for initial rollout):

- `template_snippets.admin_validation`

## Canonical snippet payloads

### 1) `user_setup`

```jinja
{%- set name = '<< user.name >>' -%}
{%- set user_id = '<< user.user_id >>' -%}
{%- set entry_id = '<< integration.entry_id >>' -%}
{%- set lookup_key = entry_id ~ ':' ~ user_id -%}
{%- set dashboard_helper = integration_entities('choreops')
    | select('search', '^sensor\\.')
    | list
    | expand
    | selectattr('attributes.purpose', 'defined')
    | selectattr('attributes.purpose', 'eq', 'purpose_dashboard_helper')
    | selectattr('attributes.dashboard_lookup_key', 'eq', lookup_key)
    | map(attribute='entity_id')
    | first
    | default("err-dashboard_helper_missing", true) -%}
```

### 2) `user_validation`

```jinja
{#-- Validation: Check if name is configured --#}
{%- if name == 'K i d n a m e' | replace(' ', '') or name == '' -%}
  {{
    {
      'type': 'markdown',
      'content': "⚠️ **Dashboard Not Configured**\n\nDashboard variable `name=` not set.\n\n**Fix:** Change `'<< user.name >>'` to child's name in\nthe **User Configuration** section at top.\n\n**Tip:** Use Find & Replace (Ctrl+F) in edit\nmode to update all cards at once.\n\n📖 [Setup Instructions](https://github.com/ccpk1/choreops-ha-dashboard?tab=readme-ov-file#-how-to-implement-this-dashboard)"
    }
  }},
  {%- set skip_render = true -%}
{%- elif states(dashboard_helper) in ['unknown', 'unavailable'] -%}
  {{
    {
      'type': 'markdown',
      'content': "⚠️ **Dashboard Configuration Error**\n\nCannot find: `" ~ dashboard_helper ~ "`\n\nThe ChoreOps integration may not have a child\nnamed '" ~ name ~ "'. Check Settings → Integrations →\nChoreOps to verify the name matches exactly.\n\n📖 [Setup Instructions](https://github.com/ccpk1/choreops-ha-dashboard?tab=readme-ov-file#-how-to-implement-this-dashboard)"
    }
  }},
  {%- set skip_render = true -%}
{%- else -%}
  {%- set skip_render = false -%}
{%- endif -%}
```

Validation cleanup note:

- Replace legacy kidname-oriented wording in validation copy with neutral user-context wording.
- Keep behavior the same (`skip_render` assignment contract), but modernize message text and references.

### 3) `admin_setup_shared`

```jinja
{%- set entry_id = '<< integration.entry_id >>' -%}
{%- set admin_selector_eid = integration_entities('choreops')
    | select('match', '^select\\.')
    | list
    | expand
    | selectattr('attributes.purpose', 'defined')
    | selectattr('attributes.purpose', 'eq', 'purpose_system_dashboard_admin_user')
    | selectattr('attributes.integration_entry_id', 'eq', entry_id)
    | map(attribute='entity_id')
    | first
    | default('', true) -%}
```

### 4) `admin_setup_peruser`

```jinja
{%- set name = '<< user.name >>' -%}
{%- set user_id = '<< user.user_id >>' -%}
{%- set entry_id = '<< integration.entry_id >>' -%}
{%- set lookup_key = entry_id ~ ':' ~ user_id -%}
{%- set admin_selector_eid = integration_entities('choreops')
    | select('search', '^sensor\\.')
    | list
    | expand
    | selectattr('attributes.purpose', 'defined')
    | selectattr('attributes.purpose', 'eq', 'purpose_dashboard_helper')
    | selectattr('attributes.dashboard_lookup_key', 'eq', lookup_key)
    | map(attribute='entity_id')
    | first
    | default('', true) -%}
```

### 5) `meta_stamp`

```jinja
{%- set stamp_release = (dashboard_meta.release_ref if dashboard_meta.release_ref is defined else None) or (dashboard_meta.release_version if dashboard_meta.release_version is defined else 'local') -%}
{%- set stamp_template = (dashboard_meta.template_id if dashboard_meta.template_id is defined else 'unknown-template') -%}
{%- set stamp_generated = (dashboard_meta.generated_at if dashboard_meta.generated_at is defined else 'unknown-time') -%}
{%- set meta_stamp = 'ℹ️ ' ~ stamp_template ~ ' • ' ~ stamp_release ~ ' • ' ~ stamp_generated -%}
{{ meta_stamp }}
```

### 6) `admin_validation_missing_selector`

```jinja
{%- if admin_selector_eid == '' -%}
  {{
    {
      'type': 'markdown',
      'content': "⚠️ **Admin Selector Not Found**\n\nThe admin selector entity could not be resolved for this dashboard context.\n\nReload ChoreOps and verify admin dashboard controls are enabled."
    }
  }},
  {%- set skip_render = true -%}
{%- else -%}
  {%- set skip_render = false -%}
{%- endif -%}
```

### 7) `admin_validation_invalid_selection` (optional second validator)

```jinja
{%- if not skip_render and states(admin_selector_eid) in ['None', '', 'unknown', 'unavailable'] -%}
  {{
    {
      'type': 'markdown',
      'content': "ℹ️ **No Assignee Selected**\n\nSelect an assignee from the admin selector to continue."
    }
  }},
  {%- set skip_render = true -%}
{%- endif -%}
```

### 8) `user_override_helper` (advanced customization)

```jinja
{#-- Optional advanced override; leave empty for auto-lookup --#}
{%- set override_dashboard_helper = '' -%}
{%- if override_dashboard_helper != '' -%}
  {%- set dashboard_helper = override_dashboard_helper -%}
{%- endif -%}
```

## In-template usage pattern

Within each auto-entities `filter.template` block, replace repeated boilerplate with one-line insert markers:

```jinja
<< template_snippets.user_setup >>
<< template_snippets.user_validation >>
<< template_snippets.user_override_helper >>
<< template_snippets.meta_stamp >>
```

or for admin:

```jinja
<< template_snippets.admin_setup_shared >>
<< template_snippets.admin_validation_missing_selector >>
<< template_snippets.admin_validation_invalid_selection >>
<< template_snippets.meta_stamp >>
```

and per-user admin:

```jinja
<< template_snippets.admin_setup_peruser >>
<< template_snippets.admin_validation_missing_selector >>
<< template_snippets.meta_stamp >>
```

Mandatory card structure contract:

1. Card header comment line must remain first in template block:

- `{#-- ===== <CARD NAME> CARD ===== --#}`

2. Numbered sections must remain present and consistent:

- `{#-- 1. User Configuration --#}` (or admin equivalent)
- setup + validation (`skip_render`) before data collection

3. Section labels may vary by card detail, but section ordering must not be inverted.

Recommended card placement:

- Mushroom cards: append to `secondary` with newline separation
- Markdown cards: append as the final line under main content
- Heading cards: use adjacent markdown card when no subtitle/secondary field exists

## Constraints

- Snippets must preserve HA Jinja syntax exactly (no escaping of `{%`, `{{`, or filters).
- Snippets are inserted before card-specific variables and logic.
- Snippet content is treated as authoritative; cards should not redefine `name`, `user_id`, `entry_id`, `lookup_key`, `dashboard_helper`, or `admin_selector_eid` unless explicitly required.
- `meta_stamp` output format must remain stable (same separators/order) for troubleshooting and tests.
- Override mode must remain opt-in and default to auto-lookup behavior.
- Any exception must be documented inline in template comments with reason.

## Rollout order

1. Apply to high-repeat cards in [../../../choreops-dashboards/templates/user-gamification-v1.yaml](../../../choreops-dashboards/templates/user-gamification-v1.yaml)
2. Apply to [../../../choreops-dashboards/templates/user-minimal-v1.yaml](../../../choreops-dashboards/templates/user-minimal-v1.yaml)
3. Apply to [../../../choreops-dashboards/templates/admin-shared-v1.yaml](../../../choreops-dashboards/templates/admin-shared-v1.yaml)
4. Apply to [../../../choreops-dashboards/templates/admin-peruser-v1.yaml](../../../choreops-dashboards/templates/admin-peruser-v1.yaml)
5. Sync and parity-check vendored templates in ChoreOps

## Test assertions to add

- Contract test that each target template references snippet insert markers.
- Contract test that forbidden duplicated inline setup blocks are absent in converted cards.
- Contract test that each stamped card references `template_snippets.meta_stamp` in an approved placement.
- Contract test that each converted card retains header comment and numbered section ordering contract.
- Contract test that override snippet exists but defaults to disabled behavior.
- Render test that snippet-expanded templates still parse as YAML and render valid view configs.
