"""Minimal render smoke tests for dashboard templates."""

from __future__ import annotations

from pathlib import Path

from custom_components.choreops.helpers import (
    dashboard_builder as builder,
    dashboard_helpers as dh,
)

TEMPLATES_ROOT = Path("custom_components/choreops/dashboards/templates")


def _read_template(name: str) -> str:
    """Read a vendored dashboard template file."""
    return (TEMPLATES_ROOT / name).read_text(encoding="utf-8")


def test_user_template_renders_without_parse_errors() -> None:
    """User template renders and parses into a view dict."""
    template_str = _read_template("user-minimal-v1.yaml")
    context = dh.build_dashboard_context(
        "Zoe",
        assignee_id="user-123",
        integration_entry_id="entry-123",
        template_profile="user-minimal-v1",
        release_ref="0.0.1-beta.3",
        generated_at="2026-03-02T00:00:00+00:00",
    )

    rendered = builder.render_dashboard_template(template_str, dict(context))

    assert rendered["title"] == "Zoe Chores"
    assert rendered["path"] == "zoe"
    assert isinstance(rendered.get("sections"), list)


def test_admin_template_renders_without_parse_errors() -> None:
    """Admin template renders and parses into a view dict."""
    template_str = _read_template("admin-shared-v1.yaml")
    context = dh.build_admin_dashboard_context(
        integration_entry_id="entry-123",
        template_profile="admin-shared-v1",
        release_ref="0.0.1-beta.3",
        generated_at="2026-03-02T00:00:00+00:00",
    )

    rendered = builder.render_dashboard_template(template_str, context)

    assert rendered["title"] == "ChoreOps Admin"
    assert rendered["path"] == "admin"
    assert isinstance(rendered.get("sections"), list)
