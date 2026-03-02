"""Minimal dashboard context contract tests."""

from __future__ import annotations

from custom_components.choreops import const
from custom_components.choreops.helpers import dashboard_helpers as dh


def test_build_dashboard_context_includes_meta_and_snippets() -> None:
    """Dashboard context includes required metadata and snippet keys."""
    context = dh.build_dashboard_context(
        "Zoe",
        assignee_id="user-123",
        integration_entry_id="entry-123",
        template_profile="user-minimal-v1",
        release_ref="0.0.1-beta.3",
        generated_at="2026-03-02T00:00:00+00:00",
    )

    assert (
        context[const.DASHBOARD_CONTEXT_KEY_META][
            const.DASHBOARD_PROVENANCE_KEY_TEMPLATE_ID
        ]
        == "user-minimal-v1"
    )
    assert (
        context[const.DASHBOARD_CONTEXT_KEY_META][
            const.DASHBOARD_PROVENANCE_KEY_GENERATED_AT
        ]
        == "2026-03-02T00:00:00+00:00"
    )

    snippets = context[const.DASHBOARD_CONTEXT_KEY_SNIPPETS]
    assert const.DASHBOARD_SNIPPET_KEY_USER_SETUP in snippets
    assert const.DASHBOARD_SNIPPET_KEY_USER_VALIDATION in snippets
    assert const.DASHBOARD_SNIPPET_KEY_META_STAMP in snippets


def test_build_admin_dashboard_context_includes_meta_and_snippets() -> None:
    """Admin context includes required metadata and admin snippet keys."""
    context = dh.build_admin_dashboard_context(
        integration_entry_id="entry-123",
        template_profile="admin-shared-v1",
        release_ref="0.0.1-beta.3",
        generated_at="2026-03-02T00:00:00+00:00",
    )

    assert (
        context[const.DASHBOARD_CONTEXT_KEY_META][
            const.DASHBOARD_PROVENANCE_KEY_TEMPLATE_ID
        ]
        == "admin-shared-v1"
    )

    snippets = context[const.DASHBOARD_CONTEXT_KEY_SNIPPETS]
    assert const.DASHBOARD_SNIPPET_KEY_ADMIN_SETUP_SHARED in snippets
    assert const.DASHBOARD_SNIPPET_KEY_ADMIN_VALIDATION_MISSING_SELECTOR in snippets
    assert const.DASHBOARD_SNIPPET_KEY_META_STAMP in snippets
