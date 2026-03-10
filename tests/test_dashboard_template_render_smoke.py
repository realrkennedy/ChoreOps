"""Minimal render smoke tests for dashboard templates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import jinja2
import yaml

from custom_components.choreops import const
from custom_components.choreops.helpers import (
    dashboard_builder as builder,
    dashboard_helpers as dh,
)

TEMPLATES_ROOT = Path("custom_components/choreops/dashboards/templates")


def _read_template(name: str) -> str:
    """Read a vendored dashboard template file."""
    return (TEMPLATES_ROOT / name).read_text(encoding="utf-8")


def test_user_template_renders_without_parse_errors() -> None:
    """User template renders and parses into a dashboard dict."""
    template_str = _read_template("user-chores-essential-v1.yaml")
    context = dh.build_dashboard_context(
        "Zoe",
        assignee_id="user-123",
        integration_entry_id="entry-123",
        template_profile="user-chores-essential-v1",
        release_ref="0.0.1-beta.3",
        generated_at="2026-03-02T00:00:00+00:00",
    )

    rendered = builder.render_dashboard_template(template_str, dict(context))

    assert isinstance(rendered.get("views"), list)
    assert len(rendered["views"]) == 1
    assert rendered["views"][0]["title"] == "Zoe"
    assert rendered["views"][0]["path"] == "zoe"
    assert isinstance(rendered["views"][0].get("sections"), list)


def test_admin_template_renders_without_parse_errors() -> None:
    """Admin template renders and parses into a dashboard dict."""
    template_str = _read_template("admin-shared-v1.yaml")
    context = dh.build_admin_dashboard_context(
        integration_entry_id="entry-123",
        template_profile="admin-shared-v1",
        release_ref="0.0.1-beta.3",
        generated_at="2026-03-02T00:00:00+00:00",
    )

    rendered = builder.render_dashboard_template(template_str, context)

    assert isinstance(rendered.get("views"), list)
    assert len(rendered["views"]) == 1
    assert rendered["views"][0]["title"] == "ChoreOps Admin"
    assert rendered["views"][0]["path"] == "admin"
    assert isinstance(rendered["views"][0].get("sections"), list)


@dataclass
class _MockState:
    """Minimal Home Assistant-like state object for template rendering tests."""

    entity_id: str
    state: str
    attributes: dict[str, object]
    name: str


def test_admin_target_selector_template_renders_as_valid_cards() -> None:
    """Shared admin target selector inner template renders valid card configs."""
    template_str = _read_template("admin-shared-v1.yaml")
    context = dh.build_admin_dashboard_context(
        integration_entry_id="entry-123",
        template_profile="admin-shared-v1",
        release_ref="0.0.1-beta.3",
        generated_at="2026-03-09T00:00:00+00:00",
    )

    rendered = builder.render_dashboard_template(template_str, context)
    selector_template = next(
        card["filter"]["template"]
        for section in rendered["views"][0]["sections"]
        for card in section.get("cards", [])
        if isinstance(card, dict)
        and isinstance(card.get("filter"), dict)
        and "select.select_option" in str(card["filter"].get("template", ""))
    )

    mock_states = {
        "select.choreops_admin_target": _MockState(
            entity_id="select.choreops_admin_target",
            state="Alice",
            attributes={
                "purpose": "purpose_system_dashboard_admin_user",
                "integration_entry_id": "entry-123",
                "dashboard_helper_eid": "sensor.alice_dashboard_helper",
            },
            name="Admin Target",
        ),
        "sensor.shared_admin_dashboard_helper": _MockState(
            entity_id="sensor.shared_admin_dashboard_helper",
            state="available",
            attributes={
                "purpose": "purpose_system_dashboard_helper",
                "integration_entry_id": "entry-123",
                "dashboard_lookup_key": "entry-123:shared_admin",
                "ui_control": {},
                "user_dashboard_helpers": {
                    "user-alice": "sensor.alice_dashboard_helper",
                    "user-bob": "sensor.bob_dashboard_helper",
                },
                "translation_sensor_eid": "sensor.translations",
            },
            name="Shared Admin Dashboard Helper",
        ),
        "sensor.alice_dashboard_helper": _MockState(
            entity_id="sensor.alice_dashboard_helper",
            state="ok",
            attributes={
                "purpose": "purpose_dashboard_helper",
                "integration_entry_id": "entry-123",
                "user_name": "Alice",
                "ui_control": {},
                "dashboard_helpers": {"translation_sensor_eid": "sensor.translations"},
            },
            name="Alice Dashboard Helper",
        ),
        "sensor.bob_dashboard_helper": _MockState(
            entity_id="sensor.bob_dashboard_helper",
            state="ok",
            attributes={
                "purpose": "purpose_dashboard_helper",
                "integration_entry_id": "entry-123",
                "user_name": "Bob",
                "ui_control": {},
                "dashboard_helpers": {"translation_sensor_eid": "sensor.translations"},
            },
            name="Bob Dashboard Helper",
        ),
        "sensor.translations": _MockState(
            entity_id="sensor.translations",
            state="ok",
            attributes={
                "ui_translations": {
                    "none": "None",
                    "admin_target": "Admin target",
                    "choose_user_for_admin_actions": (
                        "Choose the user for admin actions below."
                    ),
                    "current_review_target": "Current review target",
                }
            },
            name="Translations",
        ),
    }

    def integration_entities(_domain: str) -> list[str]:
        return list(mock_states)

    def expand_filter(values: list[object]) -> list[_MockState]:
        expanded_states: list[_MockState] = []
        for value in values:
            if isinstance(value, _MockState):
                expanded_states.append(value)
            elif isinstance(value, str) and value in mock_states:
                expanded_states.append(mock_states[value])
        return expanded_states

    def states(entity_id: str) -> str:
        if entity_id in mock_states:
            return mock_states[entity_id].state
        return "unknown"

    def state_attr(entity_id: str, attr_name: str) -> object | None:
        if entity_id in mock_states:
            return mock_states[entity_id].attributes.get(attr_name)
        return None

    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    env.filters["expand"] = expand_filter
    env.tests["search"] = lambda value, pattern: (
        __import__("re").search(pattern, value) is not None
    )
    env.tests["match"] = lambda value, pattern: (
        __import__("re").match(pattern, value) is not None
    )

    output = env.from_string(selector_template).render(
        integration_entities=integration_entities,
        states=states,
        state_attr=state_attr,
    )

    parsed = yaml.safe_load(f"[{output}]")

    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["type"] == "custom:button-card"
    assert parsed[0]["entity"] == "select.choreops_admin_target"
    assert parsed[0]["tap_action"]["action"] == "call-service"
    assert parsed[0]["tap_action"]["service"] == "choreops.manage_ui_control"
    assert parsed[0]["tap_action"]["data"] == {
        "config_entry_id": "entry-123",
        "ui_control_target": "shared_admin",
        "ui_control_action": "update",
        "key": "admin-shared/admin-target-selector/header-collapse",
        "value": False,
    }
    assert parsed[0]["hold_action"]["action"] == "more-info"
    assert "Alice" in parsed[0]["custom_fields"]["target"]


def test_admin_target_selector_template_shows_guidance_without_selection() -> None:
    """Shared admin target selector shows chooser guidance when no user is selected."""
    template_str = _read_template("admin-shared-v1.yaml")
    context = dh.build_admin_dashboard_context(
        integration_entry_id="entry-123",
        template_profile="admin-shared-v1",
        release_ref="0.0.1-beta.3",
        generated_at="2026-03-09T00:00:00+00:00",
    )

    rendered = builder.render_dashboard_template(template_str, context)
    selector_template = next(
        card["filter"]["template"]
        for section in rendered["views"][0]["sections"]
        for card in section.get("cards", [])
        if isinstance(card, dict)
        and isinstance(card.get("filter"), dict)
        and "select.select_option" in str(card["filter"].get("template", ""))
    )

    mock_states = {
        "select.choreops_admin_target": _MockState(
            entity_id="select.choreops_admin_target",
            state="None",
            attributes={
                "purpose": "purpose_system_dashboard_admin_user",
                "integration_entry_id": "entry-123",
                "dashboard_helper_eid": "",
            },
            name="Admin Target",
        ),
        "sensor.shared_admin_dashboard_helper": _MockState(
            entity_id="sensor.shared_admin_dashboard_helper",
            state="available",
            attributes={
                "purpose": "purpose_system_dashboard_helper",
                "integration_entry_id": "entry-123",
                "dashboard_lookup_key": "entry-123:shared_admin",
                "ui_control": {},
                "user_dashboard_helpers": {
                    "user-alice": "sensor.alice_dashboard_helper",
                },
                "translation_sensor_eid": "sensor.translations",
            },
            name="Shared Admin Dashboard Helper",
        ),
        "sensor.alice_dashboard_helper": _MockState(
            entity_id="sensor.alice_dashboard_helper",
            state="ok",
            attributes={
                "purpose": "purpose_dashboard_helper",
                "integration_entry_id": "entry-123",
                "user_name": "Alice",
                "ui_control": {},
                "dashboard_helpers": {"translation_sensor_eid": "sensor.translations"},
            },
            name="Alice Dashboard Helper",
        ),
        "sensor.translations": _MockState(
            entity_id="sensor.translations",
            state="ok",
            attributes={
                "ui_translations": {
                    "none": "None",
                    "admin_target": "Admin target",
                    "choose_user_for_admin_actions": (
                        "Choose the user for admin actions below."
                    ),
                    "current_review_target": "Current review target",
                    "selected_user": "Selected user",
                }
            },
            name="Translations",
        ),
    }

    def integration_entities(_domain: str) -> list[str]:
        return list(mock_states)

    def expand_filter(values: list[object]) -> list[_MockState]:
        expanded_states: list[_MockState] = []
        for value in values:
            if isinstance(value, _MockState):
                expanded_states.append(value)
            elif isinstance(value, str) and value in mock_states:
                expanded_states.append(mock_states[value])
        return expanded_states

    def states(entity_id: str) -> str:
        if entity_id in mock_states:
            return mock_states[entity_id].state
        return "unknown"

    def state_attr(entity_id: str, attr_name: str) -> object | None:
        if entity_id in mock_states:
            return mock_states[entity_id].attributes.get(attr_name)
        return None

    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    env.filters["expand"] = expand_filter
    env.tests["search"] = lambda value, pattern: (
        __import__("re").search(pattern, value) is not None
    )
    env.tests["match"] = lambda value, pattern: (
        __import__("re").match(pattern, value) is not None
    )

    output = env.from_string(selector_template).render(
        integration_entities=integration_entities,
        states=states,
        state_attr=state_attr,
    )

    parsed = yaml.safe_load(f"[{output}]")

    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["type"] == "custom:button-card"
    assert parsed[0]["entity"] == "select.choreops_admin_target"
    assert parsed[0]["label"] == "Choose the user for admin actions below."
    assert parsed[0]["tap_action"]["action"] == "call-service"
    assert parsed[0]["tap_action"]["service"] == "choreops.manage_ui_control"
    assert parsed[0]["tap_action"]["data"] == {
        "config_entry_id": "entry-123",
        "ui_control_target": "shared_admin",
        "ui_control_action": "update",
        "key": "admin-shared/admin-target-selector/header-collapse",
        "value": False,
    }
    assert parsed[0]["hold_action"]["action"] == "more-info"


def test_user_chores_template_renders_with_button_card_templates() -> None:
    """User chores template renders as full dashboard with root templates."""
    template_str = _read_template("user-chores-standard-v1.yaml")
    chore_engine_context = _read_template("shared/chore_engine/context_v1.yaml")
    chore_engine_prepare_groups = _read_template(
        "shared/chore_engine/prepare_groups_v1.yaml"
    )
    chore_engine_header = _read_template("shared/chore_engine/header_v1.yaml")
    chore_engine_settings = _read_template("shared/chore_engine/settings_panel_v1.yaml")
    chore_engine_group_render = _read_template(
        "shared/chore_engine/group_render_v1.yaml"
    )
    standard_row_template_str = _read_template(
        "shared/button_card_template_chore_row_v1.yaml"
    )
    kids_row_template_str = _read_template(
        "shared/button_card_template_chore_row_kids_v1.yaml"
    )
    template_str = dh.compile_prepared_template_assets(
        {
            "templates/user-chores-standard-v1.yaml": template_str,
            "templates/shared/chore_engine/context_v1.yaml": chore_engine_context,
            "templates/shared/chore_engine/prepare_groups_v1.yaml": (
                chore_engine_prepare_groups
            ),
            "templates/shared/chore_engine/header_v1.yaml": chore_engine_header,
            "templates/shared/chore_engine/settings_panel_v1.yaml": (
                chore_engine_settings
            ),
            "templates/shared/chore_engine/group_render_v1.yaml": (
                chore_engine_group_render
            ),
            "templates/shared/button_card_template_chore_row_v1.yaml": (
                standard_row_template_str
            ),
            "templates/shared/button_card_template_chore_row_kids_v1.yaml": (
                kids_row_template_str
            ),
        }
    )["templates/user-chores-standard-v1.yaml"]
    context = dh.build_dashboard_context(
        "Zoe",
        assignee_id="user-123",
        integration_entry_id="entry-123",
        template_profile="user-chores-standard-v1",
        release_ref="0.0.1-beta.3",
        generated_at="2026-03-02T00:00:00+00:00",
    )

    rendered = builder.render_dashboard_template(template_str, dict(context))

    assert isinstance(rendered.get("views"), list)
    assert len(rendered["views"]) == 1
    assert rendered["views"][0]["title"] == "Zoe"
    assert rendered["views"][0]["path"] == "zoe"
    assert isinstance(rendered["views"][0].get("sections"), list)
    assert isinstance(rendered.get("button_card_templates"), dict)
    assert "chore_row_v1" in rendered["button_card_templates"]
    assert "chore_row_kids_v1" in rendered["button_card_templates"]


def test_user_chores_template_contains_ui_control_contract() -> None:
    """User chores template should reference the reviewed UI control contract."""
    template_str = _read_template("user-chores-standard-v1.yaml")

    assert "template_shared.chore_engine/context_v1" in template_str
    assert "template_shared.chore_engine/prepare_groups_v1" in template_str
    assert "template_shared.chore_engine/header_v1" in template_str
    assert "template_shared.chore_engine/settings_panel_v1" in template_str
    assert "template_shared.chore_engine/group_render_v1" in template_str
    assert "pref_ui_control_key_root = 'chores'" in template_str


def test_shared_chore_engine_fragment_contains_ui_control_contract() -> None:
    """Shared chores engine fragment should reference the reviewed UI control contract."""
    template_str = _read_template("shared/chore_engine/context_v1.yaml")

    assert "state_attr(dashboard_helper, 'ui_control')" in template_str
    assert "ui_control_key_root = pref_ui_control_key_root" in template_str
    assert "'/header_collapse'" in template_str
    assert "'/row_variant'" in template_str
    assert "'/exclude_completed'" in template_str
    assert "'/exclude_blocked'" in template_str
    assert "'/sort_within_groups'" in template_str


def test_user_gamification_premier_template_renders_with_button_card_templates() -> (
    None
):
    """Gamification Premier template renders as full dashboard with root templates."""
    template_str = _read_template("user-gamification-premier-v1.yaml")
    chore_engine_context = _read_template("shared/chore_engine/context_v1.yaml")
    chore_engine_prepare_groups = _read_template(
        "shared/chore_engine/prepare_groups_v1.yaml"
    )
    chore_engine_header = _read_template("shared/chore_engine/header_v1.yaml")
    chore_engine_settings = _read_template("shared/chore_engine/settings_panel_v1.yaml")
    chore_engine_group_render = _read_template(
        "shared/chore_engine/group_render_v1.yaml"
    )
    standard_row_template_str = _read_template(
        "shared/button_card_template_chore_row_v1.yaml"
    )
    kids_row_template_str = _read_template(
        "shared/button_card_template_chore_row_kids_v1.yaml"
    )
    template_str = dh.compile_prepared_template_assets(
        {
            "templates/user-gamification-premier-v1.yaml": template_str,
            "templates/shared/chore_engine/context_v1.yaml": chore_engine_context,
            "templates/shared/chore_engine/prepare_groups_v1.yaml": (
                chore_engine_prepare_groups
            ),
            "templates/shared/chore_engine/header_v1.yaml": chore_engine_header,
            "templates/shared/chore_engine/settings_panel_v1.yaml": (
                chore_engine_settings
            ),
            "templates/shared/chore_engine/group_render_v1.yaml": (
                chore_engine_group_render
            ),
            "templates/shared/button_card_template_chore_row_v1.yaml": (
                standard_row_template_str
            ),
            "templates/shared/button_card_template_chore_row_kids_v1.yaml": (
                kids_row_template_str
            ),
        }
    )["templates/user-gamification-premier-v1.yaml"]
    context = dh.build_dashboard_context(
        "Zoe",
        assignee_id="user-123",
        integration_entry_id="entry-123",
        template_profile="user-gamification-premier-v1",
        release_ref="0.0.1-beta.4",
        generated_at="2026-03-06T00:00:00+00:00",
    )

    rendered = builder.render_dashboard_template(template_str, dict(context))

    assert isinstance(rendered.get("views"), list)
    assert len(rendered["views"]) == 1
    assert rendered["views"][0]["title"] == "Zoe"
    assert rendered["views"][0]["path"] == "zoe"
    assert isinstance(rendered["views"][0].get("sections"), list)
    assert isinstance(rendered.get("button_card_templates"), dict)
    assert "chore_row_v1" in rendered["button_card_templates"]
    assert "chore_row_kids_v1" in rendered["button_card_templates"]


def test_user_gamification_premier_template_contains_ui_control_contract() -> None:
    """Gamification Premier template should reference the reviewed UI control contract."""
    template_str = _read_template("user-gamification-premier-v1.yaml")

    assert f"{const.DOMAIN}.{const.SERVICE_MANAGE_UI_CONTROL}" in _read_template(
        "shared/chore_engine/settings_panel_v1.yaml"
    )
    assert "ui_control_key_root = 'gamification/rewards'" in template_str
    assert "template_shared.chore_engine/context_v1" in template_str
    assert "template_shared.chore_engine/prepare_groups_v1" in template_str
    assert "template_shared.chore_engine/header_v1" in template_str
    assert "template_shared.chore_engine/settings_panel_v1" in template_str
    assert "template_shared.chore_engine/group_render_v1" in template_str
    assert "pref_ui_control_key_root = 'gamification/chores'" in template_str
