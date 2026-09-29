"""Tests for the dashboard helper recent economy adjustment feed."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from custom_components.choreops import const
from tests.helpers import SetupResult, get_dashboard_helper, setup_from_yaml

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


@pytest.fixture
async def scenario_full(
    hass: HomeAssistant,
    mock_hass_users: dict[str, Any],
) -> SetupResult:
    """Load the complete family scenario."""
    return await setup_from_yaml(
        hass,
        mock_hass_users,
        "tests/scenarios/scenario_full.yaml",
    )


async def test_recent_adjustments_are_filtered_and_newest_first(
    hass: HomeAssistant,
    scenario_full: SetupResult,
) -> None:
    """Expose bonus and penalty entries without unrelated ledger activity."""
    coordinator = scenario_full.coordinator
    assignee_id = scenario_full.assignee_ids["Max!"]

    await coordinator.economy_manager.deposit(
        assignee_id=assignee_id,
        amount=8.0,
        source=const.POINTS_SOURCE_BONUSES,
        reference_id="bonus-id",
        item_name="Great teamwork",
    )
    await coordinator.economy_manager.deposit(
        assignee_id=assignee_id,
        amount=2.0,
        source=const.POINTS_SOURCE_MANUAL,
        item_name="Manual adjustment",
    )
    await coordinator.economy_manager.withdraw(
        assignee_id=assignee_id,
        amount=3.0,
        source=const.POINTS_SOURCE_PENALTIES,
        reference_id="penalty-id",
        item_name="Missed responsibility",
    )
    await hass.async_block_till_done()

    dashboard = get_dashboard_helper(hass, "max")
    entries = dashboard[const.ATTR_DASHBOARD_RECENT_ADJUSTMENTS]

    assert [entry[const.DATA_LEDGER_SOURCE] for entry in entries] == [
        const.POINTS_SOURCE_PENALTIES,
        const.POINTS_SOURCE_BONUSES,
    ]
    assert entries[0] == {
        const.DATA_LEDGER_TIMESTAMP: entries[0][const.DATA_LEDGER_TIMESTAMP],
        const.DATA_LEDGER_AMOUNT: -3.0,
        const.DATA_LEDGER_BALANCE_AFTER: 7.0,
        const.DATA_LEDGER_SOURCE: const.POINTS_SOURCE_PENALTIES,
        "source_label": "Penalty",
        const.DATA_LEDGER_ITEM_NAME: "Missed responsibility",
        const.DATA_LEDGER_REFERENCE_ID: "penalty-id",
    }
    assert entries[1][const.DATA_LEDGER_ITEM_NAME] == "Great teamwork"
    assert entries[1][const.DATA_LEDGER_AMOUNT] == 8.0


async def test_recent_adjustments_are_bounded(
    hass: HomeAssistant,
    scenario_full: SetupResult,
) -> None:
    """Limit dashboard attributes while retaining the newest transactions."""
    coordinator = scenario_full.coordinator
    assignee_id = scenario_full.assignee_ids["Max!"]
    entry_count = const.DEFAULT_DASHBOARD_RECENT_ADJUSTMENTS + 3

    for index in range(entry_count):
        await coordinator.economy_manager.deposit(
            assignee_id=assignee_id,
            amount=1.0,
            source=const.POINTS_SOURCE_BONUSES,
            item_name=f"Bonus {index}",
        )
    await hass.async_block_till_done()

    dashboard = get_dashboard_helper(hass, "max")
    entries = dashboard[const.ATTR_DASHBOARD_RECENT_ADJUSTMENTS]

    assert len(entries) == const.DEFAULT_DASHBOARD_RECENT_ADJUSTMENTS
    assert entries[0][const.DATA_LEDGER_ITEM_NAME] == f"Bonus {entry_count - 1}"
    assert entries[-1][const.DATA_LEDGER_ITEM_NAME] == "Bonus 3"
