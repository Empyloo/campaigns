import pytest
import functions_framework

def test_create_task(mocker):
    request = {"action": "create_task",
               "schedule_time": "2022-01-01 12:00:00",
               "payload": {"message": "test message"},
               "queue_name": "test_queue"}
    create_task_mock = mocker.patch.object(CampaignService, "create_task")
    main(request)
    create_task_mock.assert_called_with(request["payload"], 
                                        dt.datetime(2022, 1, 1, 12, 0, 0), 
                                        request["queue_name"])

def test_edit_task(mocker):
    request = {"action": "edit_task",
               "payload": {"message": "test message", "id": 123}}
    edit_task_mock = mocker.patch.object(CampaignService, "edit_task")
    main(request)
    edit_task_mock.assert_called_with(request["payload"])

def test_delete_task(mocker):
    request = {"action": "delete_task",
               "payload": {"id": 123}}
    delete_task_mock = mocker.patch.object(CampaignService, "delete_task")
    main(request)
    delete_task_mock.assert_called_with(request["payload"])

def test_edit_schedule(mocker):
    request = {"action": "edit_schedule",
               "payload": {"id": 123, "new_schedule_time": "2022-01-01 12:00:00"}}
    edit_schedule_mock = mocker.patch.object(CampaignService, "edit_schedule")
    main(request)
    edit_schedule_mock.assert_called_with(request["payload"])

def test_delete_schedule(mocker):
    request = {"action": "delete_schedule",
               "payload": {"id": 123}}
    delete_schedule_mock = mocker.patch.object(CampaignService, "delete_schedule")
    main(request)
    delete_schedule_mock.assert_called_with(request["payload"])

def test_invalid_action(mocker):
    request = {"action": "invalid_action"}
    logger_mock = mocker.patch.object(logging, "error")
    main(request)
    logger_mock.assert_called_with("Invalid action provided: %s", "invalid_action")
