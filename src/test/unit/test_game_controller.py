#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests — GameController."""

import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@pytest.fixture
def controller_with_mocks():
    import game.game_controller as gc_mod

    with patch.object(gc_mod, "GameModel") as MockGameModel, patch.object(gc_mod, "CourtMeetingSystem") as MockCourtMeeting:
        model = MagicMock()
        model.get_resources.return_value = {"gold": 100}
        model.get_game_info.return_value = {"day": 2, "month": 1, "year": 190, "season": 1}
        model.get_factions.return_value = {"wei": {"name": "魏"}}
        model.get_cities.return_value = {"a": {"name": "长安"}}
        model.get_generals.return_value = {"caocao": {"name": "曹操"}}

        cms = MagicMock()
        cms.can_hold_meeting.return_value = True
        cms.start_meeting.return_value = {"success": True}
        cms.get_meeting_data.return_value = {"id": "m1"}
        cms.get_monthly_meeting_data.return_value = {"type": "monthly"}
        cms.get_emergency_meeting_data.return_value = {"type": "emergency"}
        cms.get_participant_info.return_value = {"id": "caocao"}
        cms.get_participants_for_meeting.return_value = [{"id": "caocao"}]
        cms.make_monthly_decision.return_value = {"resource_changes": {"gold": 10}}
        cms.make_emergency_decision.return_value = {"resource_changes": {"food": 5}}
        cms.make_decision.return_value = {"resource_changes": {"soldiers": -1}}
        cms.meeting_completed = MagicMock()
        cms.meeting_completed.connect = MagicMock()

        MockGameModel.return_value = model
        MockCourtMeeting.return_value = cms

        controller = gc_mod.GameController()
        yield controller, model, cms, MockGameModel, MockCourtMeeting


def test_getters_delegate_to_model(controller_with_mocks):
    controller, model, _, _, _ = controller_with_mocks
    assert controller.get_game_info()["day"] == 2
    assert controller.get_resources()["gold"] == 100
    assert "wei" in controller.get_factions()
    assert "a" in controller.get_cities()
    assert "caocao" in controller.get_generals()
    model.get_game_info.assert_called()


def test_request_court_meeting_true(controller_with_mocks):
    controller, _, cms, _, _ = controller_with_mocks
    assert controller.request_court_meeting() is True
    cms.can_hold_meeting.assert_called_once()


def test_request_court_meeting_false(controller_with_mocks):
    controller, _, cms, _, _ = controller_with_mocks
    cms.can_hold_meeting.return_value = False
    assert controller.request_court_meeting() is False


def test_advance_time_triggers_monthly_signal_on_day_rollover(controller_with_mocks):
    controller, model, _, _, _ = controller_with_mocks
    # before advance: day=30, after advance: day=1
    calls = [{"day": 30, "month": 1, "year": 190, "season": 1}, {"day": 1, "month": 2, "year": 190, "season": 1}]
    model.get_game_info.side_effect = calls
    controller.monthly_court_due = MagicMock()
    controller.monthly_court_due.emit = MagicMock()
    controller.time_advanced = MagicMock()
    controller.time_advanced.emit = MagicMock()
    controller.game_updated = MagicMock()
    controller.game_updated.emit = MagicMock()

    controller.advance_time()

    controller.monthly_court_due.emit.assert_called_once()
    controller.time_advanced.emit.assert_called_once()
    controller.game_updated.emit.assert_called_once()


def test_decision_paths_update_resources(controller_with_mocks):
    controller, model, _, _, _ = controller_with_mocks
    controller.resources_updated = MagicMock()
    controller.resources_updated.emit = MagicMock()

    controller.make_monthly_decision("a")
    controller.make_emergency_decision("b")
    controller.make_court_decision("c")

    assert model.update_resources.call_count == 3
    assert controller.resources_updated.emit.call_count == 3


def test_start_new_game_and_reset_recreate_dependencies(controller_with_mocks):
    controller, _, _, MockGameModel, MockCourtMeeting = controller_with_mocks
    controller.game_updated = MagicMock()
    controller.game_updated.emit = MagicMock()
    controller.resources_updated = MagicMock()
    controller.resources_updated.emit = MagicMock()

    controller.start_new_game()
    controller.reset_game()

    assert MockGameModel.call_count >= 3
    assert MockCourtMeeting.call_count >= 3


def test_load_and_save_delegate(controller_with_mocks):
    controller, model, _, _, _ = controller_with_mocks
    controller.game_updated = MagicMock()
    controller.game_updated.emit = MagicMock()
    controller.resources_updated = MagicMock()
    controller.resources_updated.emit = MagicMock()

    controller.save_game("save.json")
    controller.load_game("save.json")

    model.save_game.assert_called_once_with("save.json")
    model.load_game.assert_called_once_with("save.json")


def test_court_data_and_participant_accessors(controller_with_mocks):
    controller, _, cms, _, _ = controller_with_mocks
    assert controller.start_court_meeting()["success"] is True
    assert controller.get_court_meeting_data()["id"] == "m1"
    assert controller.get_monthly_court_data()["type"] == "monthly"
    assert controller.get_emergency_court_data()["type"] == "emergency"
    assert controller.get_participant_info("caocao")["id"] == "caocao"
    assert controller.get_participants_for_meeting()[0]["id"] == "caocao"
    cms.start_meeting.assert_called_once()


def test_on_court_meeting_completed_records_and_emits(controller_with_mocks):
    controller, model, _, _, _ = controller_with_mocks
    controller.game_updated = MagicMock()
    controller.game_updated.emit = MagicMock()

    controller._on_court_meeting_completed({"id": "m1"})

    model.add_court_meeting.assert_called_once_with({"id": "m1"})
    controller.game_updated.emit.assert_called_once()
