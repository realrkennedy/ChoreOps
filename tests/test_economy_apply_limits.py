"""Tests for bonus and penalty apply limits and the helper fields (fork)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.core import Context
from homeassistant.exceptions import HomeAssistantError
import pytest
import voluptuous as vol

from custom_components.choreops import const
from tests.helpers import (
    DOMAIN,
    SERVICE_CREATE_BONUS,
    SERVICE_CREATE_PENALTY,
    SERVICE_UPDATE_BONUS,
    SetupResult,
    get_dashboard_helper,
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


async def _create(hass: HomeAssistant, service: str, data: dict[str, Any]) -> str:
    response = await hass.services.async_call(
        DOMAIN, service, data, blocking=True, return_response=True
    )
    await hass.async_block_till_done()
    return str(response["id"])


def _helper_entry(hass: HomeAssistant, kind: str, name: str) -> dict[str, Any]:
    entries = get_dashboard_helper(hass, "zoe")[kind]
    return next(entry for entry in entries if entry["name"] == name)


class TestApplyLimitCrud:
    """Limits are stored, kept on partial updates and validated."""

    async def test_create_stores_limits_and_flag(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        coordinator = scenario_full.coordinator
        with patch.object(coordinator, "_persist", new=MagicMock()):
            bonus_id = await _create(
                hass,
                SERVICE_CREATE_BONUS,
                {
                    "name": "Bonus Objective",
                    "points": 10,
                    "max_per_day": 2,
                    "max_per_month": 10,
                    "perfect_day_check": True,
                },
            )
        bonus = coordinator.bonuses_data[bonus_id]
        assert bonus["max_per_day"] == 2
        assert bonus["max_per_week"] == 0
        assert bonus["max_per_month"] == 10
        assert bonus["perfect_day_check"] is True

    async def test_defaults_are_no_limit(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        coordinator = scenario_full.coordinator
        with patch.object(coordinator, "_persist", new=MagicMock()):
            bonus_id = await _create(
                hass, SERVICE_CREATE_BONUS, {"name": "Initiative", "points": 5}
            )
        bonus = coordinator.bonuses_data[bonus_id]
        assert (bonus["max_per_day"], bonus["max_per_week"], bonus["max_per_month"]) == (
            0,
            0,
            0,
        )
        assert bonus["perfect_day_check"] is False

    async def test_update_without_limits_keeps_them(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        coordinator = scenario_full.coordinator
        with patch.object(coordinator, "_persist", new=MagicMock()):
            bonus_id = await _create(
                hass,
                SERVICE_CREATE_BONUS,
                {"name": "Heavy Lift", "points": 20, "max_per_week": 1},
            )
            await hass.services.async_call(
                DOMAIN,
                SERVICE_UPDATE_BONUS,
                {"id": bonus_id, "name": "Heavy Lifting", "points": 25},
                blocking=True,
            )
        bonus = coordinator.bonuses_data[bonus_id]
        assert bonus["name"] == "Heavy Lifting"
        assert bonus["max_per_week"] == 1

    async def test_update_can_clear_a_limit(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        coordinator = scenario_full.coordinator
        with patch.object(coordinator, "_persist", new=MagicMock()):
            bonus_id = await _create(
                hass,
                SERVICE_CREATE_BONUS,
                {"name": "Above Spec", "points": 5, "max_per_day": 1},
            )
            await hass.services.async_call(
                DOMAIN,
                SERVICE_UPDATE_BONUS,
                {"id": bonus_id, "max_per_day": 0},
                blocking=True,
            )
        assert coordinator.bonuses_data[bonus_id]["max_per_day"] == 0

    async def test_negative_limit_is_rejected(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        with pytest.raises(vol.Invalid):
            await hass.services.async_call(
                DOMAIN,
                SERVICE_CREATE_PENALTY,
                {"name": "Extra Prompt", "points": 2, "max_per_day": -1},
                blocking=True,
            )

    async def test_existing_definitions_read_as_unlimited(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        """Definitions stored before this change have no limit fields."""
        coordinator = scenario_full.coordinator
        assignee_id = scenario_full.assignee_ids["Zoë"]
        bonus_id = scenario_full.bonus_ids["Extra Effort"]
        coordinator.bonuses_data[bonus_id].pop("max_per_day", None)
        status = coordinator.economy_manager.get_apply_limit_status(
            assignee_id, const.ITEM_TYPE_BONUS, bonus_id
        )
        assert status["max_per_day"] == 0
        assert status[const.ATTR_LIMIT_REACHED] is None


class TestApplyLimitEnforcement:
    """A used-up limit refuses manual applies but not automatic ones."""

    async def test_daily_bonus_limit_refuses_second_apply(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        coordinator = scenario_full.coordinator
        assignee_id = scenario_full.assignee_ids["Zoë"]
        with patch.object(coordinator, "_persist", new=MagicMock()):
            bonus_id = await _create(
                hass,
                SERVICE_CREATE_BONUS,
                {"name": "Clutch Assist", "points": 5, "max_per_day": 1},
            )
        with patch.object(
            coordinator.notification_manager, "notify_assignee", new=AsyncMock()
        ):
            balance = await coordinator.economy_manager.apply_bonus(
                "Approver", assignee_id, bonus_id
            )
            await hass.async_block_till_done()
            with pytest.raises(HomeAssistantError) as err:
                await coordinator.economy_manager.apply_bonus(
                    "Approver", assignee_id, bonus_id
                )
        assert err.value.translation_key == const.TRANS_KEY_ERROR_APPLY_LIMIT_REACHED
        assert err.value.translation_placeholders["period"] == "day"
        assert err.value.translation_placeholders["limit"] == "1"
        points = coordinator.assignees_data[assignee_id][const.DATA_USER_POINTS]
        assert points == balance

    async def test_weekly_limit_counts_across_days(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        coordinator = scenario_full.coordinator
        assignee_id = scenario_full.assignee_ids["Zoë"]
        with patch.object(coordinator, "_persist", new=MagicMock()):
            bonus_id = await _create(
                hass,
                SERVICE_CREATE_BONUS,
                {"name": "Heavy Lift", "points": 20, "max_per_week": 1},
            )
        week_key = coordinator.stats.get_period_keys()[const.PERIOD_WEEKLY]
        coordinator.assignees_data[assignee_id].setdefault(
            const.DATA_USER_BONUS_APPLIES, {}
        )[bonus_id] = {
            const.DATA_USER_BONUS_PERIODS: {
                const.PERIOD_WEEKLY: {
                    week_key: {const.DATA_USER_BONUS_PERIOD_APPLIES: 1}
                },
            }
        }
        status = coordinator.economy_manager.get_apply_limit_status(
            assignee_id, const.ITEM_TYPE_BONUS, bonus_id
        )
        assert status["applied_today"] == 0
        assert status["applied_week"] == 1
        assert status[const.ATTR_LIMIT_REACHED] == const.PERIOD_WEEKLY
        with pytest.raises(HomeAssistantError):
            await coordinator.economy_manager.apply_bonus(
                "Approver", assignee_id, bonus_id
            )

    async def test_gamification_bonus_ignores_limit(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        coordinator = scenario_full.coordinator
        assignee_id = scenario_full.assignee_ids["Zoë"]
        with patch.object(coordinator, "_persist", new=MagicMock()):
            bonus_id = await _create(
                hass,
                SERVICE_CREATE_BONUS,
                {"name": "Badge Extra", "points": 5, "max_per_day": 1},
            )
        with patch.object(
            coordinator.notification_manager, "notify_assignee", new=AsyncMock()
        ):
            for _ in range(2):
                await coordinator.economy_manager.apply_bonus(
                    "Badge Award",
                    assignee_id,
                    bonus_id,
                    gamification_originated=True,
                )
                await hass.async_block_till_done()

    async def test_penalty_limit_and_badge_bypass(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        coordinator = scenario_full.coordinator
        assignee_id = scenario_full.assignee_ids["Zoë"]
        with patch.object(coordinator, "_persist", new=MagicMock()):
            penalty_id = await _create(
                hass,
                SERVICE_CREATE_PENALTY,
                {"name": "Reset Required", "points": 5, "max_per_day": 1},
            )
        with patch.object(
            coordinator.notification_manager, "notify_assignee", new=AsyncMock()
        ):
            await coordinator.economy_manager.apply_penalty(
                "Approver", assignee_id, penalty_id
            )
            await hass.async_block_till_done()
            with pytest.raises(HomeAssistantError) as err:
                await coordinator.economy_manager.apply_penalty(
                    "Approver", assignee_id, penalty_id
                )
            await coordinator.economy_manager.apply_penalty(
                "Badge Award", assignee_id, penalty_id, enforce_limit=False
            )
        assert err.value.translation_key == const.TRANS_KEY_ERROR_APPLY_LIMIT_REACHED

    async def test_button_press_is_refused_at_limit(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
        mock_hass_users: dict[str, Any],
    ) -> None:
        coordinator = scenario_full.coordinator
        with patch.object(coordinator, "_persist", new=MagicMock()):
            await _create(
                hass,
                SERVICE_CREATE_BONUS,
                {"name": "Initiative", "points": 5, "max_per_day": 1},
            )
        await hass.async_block_till_done()
        eid = _helper_entry(hass, "bonuses", "Initiative")["eid"]
        assert eid
        context = Context(user_id=mock_hass_users["approver1"].id)
        with patch.object(
            coordinator.notification_manager, "notify_assignee", new=AsyncMock()
        ):
            await hass.services.async_call(
                "button", "press", {"entity_id": eid}, blocking=True, context=context
            )
            await hass.async_block_till_done()
            with pytest.raises(HomeAssistantError):
                await hass.services.async_call(
                    "button",
                    "press",
                    {"entity_id": eid},
                    blocking=True,
                    context=context,
                )


class TestHelperFields:
    """The dashboard helper lists limits, this period's use and the flag."""

    async def test_helper_reports_limits_use_and_flag(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        coordinator = scenario_full.coordinator
        assignee_id = scenario_full.assignee_ids["Zoë"]
        with patch.object(coordinator, "_persist", new=MagicMock()):
            bonus_id = await _create(
                hass,
                SERVICE_CREATE_BONUS,
                {
                    "name": "Bonus Objective",
                    "points": 10,
                    "description": "A genuinely extra task",
                    "icon": "mdi:target",
                    "max_per_day": 1,
                    "perfect_day_check": True,
                },
            )
        entry = _helper_entry(hass, "bonuses", "Bonus Objective")
        assert entry["description"] == "A genuinely extra task"
        assert entry["icon"] == "mdi:target"
        assert entry["perfect_day_check"] is True
        assert entry["max_per_day"] == 1
        assert entry["applied_today"] == 0
        assert entry["limit_reached"] is None

        with patch.object(
            coordinator.notification_manager, "notify_assignee", new=AsyncMock()
        ):
            await coordinator.economy_manager.apply_bonus(
                "Approver", assignee_id, bonus_id
            )
            await hass.async_block_till_done()
        coordinator.async_update_listeners()
        await hass.async_block_till_done()
        entry = _helper_entry(hass, "bonuses", "Bonus Objective")
        assert entry["applied_today"] == 1
        assert entry["applied_week"] == 1
        assert entry["applied_month"] == 1
        assert entry["limit_reached"] == const.PERIOD_DAILY

    async def test_helper_penalty_entry_has_fields(
        self, hass: HomeAssistant, scenario_full: SetupResult
    ) -> None:
        coordinator = scenario_full.coordinator
        with patch.object(coordinator, "_persist", new=MagicMock()):
            await _create(
                hass,
                SERVICE_CREATE_PENALTY,
                {"name": "Extra Prompt", "points": 2, "max_per_week": 3},
            )
        entry = _helper_entry(hass, "penalties", "Extra Prompt")
        assert entry["max_per_week"] == 3
        assert entry["perfect_day_check"] is False
        assert entry["limit_reached"] is None
