"""Tests for bonus and penalty catalog CRUD services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest
import voluptuous as vol

from tests.helpers import (
    DOMAIN,
    SERVICE_CREATE_BONUS,
    SERVICE_CREATE_PENALTY,
    SERVICE_DELETE_BONUS,
    SERVICE_DELETE_PENALTY,
    SERVICE_UPDATE_BONUS,
    SERVICE_UPDATE_PENALTY,
    SetupResult,
    setup_from_yaml,
)

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


class TestBonusCatalogCrudServices:
    """Validate bonus CRUD schemas and manager-backed persistence."""

    async def test_create_bonus_accepts_documented_fields(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Create a bonus with literal user-facing field names."""
        coordinator = scenario_full.coordinator
        persist_mock = MagicMock()
        with patch.object(coordinator, "_persist", new=persist_mock):
            response = await hass.services.async_call(
                DOMAIN,
                SERVICE_CREATE_BONUS,
                {
                    "name": "Family Teamwork",
                    "points": 25,
                    "description": "Everyone pitched in",
                    "icon": "mdi:account-group",
                    "labels": ["family", "teamwork"],
                },
                blocking=True,
                return_response=True,
            )

        persist_mock.assert_called_once_with(immediate=True)
        bonus_id = response["id"]
        bonus = coordinator.bonuses_data[bonus_id]
        assert bonus["name"] == "Family Teamwork"
        assert bonus["points"] == 25
        assert bonus["bonus_labels"] == ["family", "teamwork"]

    async def test_create_bonus_rejects_prefixed_fields(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Reject undocumented prefixed field names."""
        with pytest.raises(vol.Invalid):
            await hass.services.async_call(
                DOMAIN,
                SERVICE_CREATE_BONUS,
                {"bonus_name": "Invalid", "bonus_points": 5},
                blocking=True,
            )

    async def test_update_bonus_by_id_can_rename(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Update and rename an existing bonus by stable UUID."""
        coordinator = scenario_full.coordinator
        bonus_id = scenario_full.bonus_ids["Extra Effort"]
        with patch.object(coordinator, "_persist", new=MagicMock()):
            response = await hass.services.async_call(
                DOMAIN,
                SERVICE_UPDATE_BONUS,
                {"id": bonus_id, "name": "Outstanding Effort", "points": 30},
                blocking=True,
                return_response=True,
            )

        assert response == {"id": bonus_id}
        assert coordinator.bonuses_data[bonus_id]["name"] == "Outstanding Effort"
        assert coordinator.bonuses_data[bonus_id]["points"] == 30

    async def test_delete_bonus_by_id(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Delete an existing bonus by stable UUID."""
        coordinator = scenario_full.coordinator
        bonus_id = scenario_full.bonus_ids["Helping Sibling"]
        with patch.object(coordinator, "_persist", new=MagicMock()):
            response = await hass.services.async_call(
                DOMAIN,
                SERVICE_DELETE_BONUS,
                {"id": bonus_id},
                blocking=True,
                return_response=True,
            )

        assert response == {"id": bonus_id}
        assert bonus_id not in coordinator.bonuses_data

    async def test_update_bonus_requires_identifier(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Require a stable UUID for update operations."""
        with pytest.raises(vol.Invalid):
            await hass.services.async_call(
                DOMAIN,
                SERVICE_UPDATE_BONUS,
                {"points": 10},
                blocking=True,
            )


class TestPenaltyCatalogCrudServices:
    """Validate penalty CRUD schemas and manager-backed persistence."""

    async def test_create_penalty_normalizes_points_negative(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Store a positive service value as a negative point deduction."""
        coordinator = scenario_full.coordinator
        persist_mock = MagicMock()
        with patch.object(coordinator, "_persist", new=persist_mock):
            response = await hass.services.async_call(
                DOMAIN,
                SERVICE_CREATE_PENALTY,
                {
                    "name": "Careless Damage",
                    "points": 12,
                    "description": "Damaged an item through carelessness",
                    "icon": "mdi:alert",
                    "labels": ["property"],
                },
                blocking=True,
                return_response=True,
            )

        persist_mock.assert_called_once_with(immediate=True)
        penalty_id = response["id"]
        penalty = coordinator.penalties_data[penalty_id]
        assert penalty["name"] == "Careless Damage"
        assert penalty["points"] == -12
        assert penalty["penalty_labels"] == ["property"]

    async def test_update_penalty_by_id_preserves_negative_storage(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Normalize a positive update value to a negative deduction."""
        coordinator = scenario_full.coordinator
        penalty_id = scenario_full.penalty_ids["Missed Chore"]
        with patch.object(coordinator, "_persist", new=MagicMock()):
            response = await hass.services.async_call(
                DOMAIN,
                SERVICE_UPDATE_PENALTY,
                {"id": penalty_id, "points": 8},
                blocking=True,
                return_response=True,
            )

        assert response == {"id": penalty_id}
        assert coordinator.penalties_data[penalty_id]["points"] == -8

    async def test_delete_penalty_by_id(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Delete an existing penalty by stable UUID."""
        coordinator = scenario_full.coordinator
        penalty_id = scenario_full.penalty_ids["Sibling Fight"]
        with patch.object(coordinator, "_persist", new=MagicMock()):
            response = await hass.services.async_call(
                DOMAIN,
                SERVICE_DELETE_PENALTY,
                {"id": penalty_id},
                blocking=True,
                return_response=True,
            )

        assert response == {"id": penalty_id}
        assert penalty_id not in coordinator.penalties_data

    async def test_delete_penalty_requires_identifier(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Require a stable UUID for delete operations."""
        with pytest.raises(vol.Invalid):
            await hass.services.async_call(
                DOMAIN,
                SERVICE_DELETE_PENALTY,
                {},
                blocking=True,
            )
