from unittest.mock import ANY, patch
from pytest import raises
import pytest
from celery.exceptions import Reject, MaxRetriesExceededError
from importer.task import importer_task_wrapper


@patch('importer.task.importer.get_members', return_value=[[], 0])
@patch('importer.task.consumer.run', return_value=0)
def test_success(consumer_run, importer_get_members):
    list_key = 'foo'
    importer_task_wrapper(list_key, offset=0, count=1, since_last_changed=None)
    importer_get_members.assert_called_with(ANY, list_key, 0, 1, None)
    consumer_run.assert_called_with([])


@patch('importer.task.importer.get_members')
@patch('importer.task.consumer.run', return_value=0)
@pytest.mark.parametrize("members", [([{}, {}])])
def test_failure(consumer_run, importer_get_members, members):
    list_key = 'foo'
    importer_get_members.return_value = [members, len(members)]
    with raises(Exception):
        importer_task_wrapper(list_key, offset=0, count=1,
                              since_last_changed=None)
    importer_get_members.assert_called_with(ANY, list_key, 0, 1, None)
    consumer_run.assert_called_with(members)


@patch('importer.task.importer_task_wrapper.retry')
@patch('importer.task.importer.get_members')
def test_failure_reject(importer_get_members, importer_task_wrapper_retry):
    list_key = 'foo'
    importer_get_members.side_effect = Exception('test')
    importer_task_wrapper_retry.side_effect = MaxRetriesExceededError('test')
    with raises(Reject):
        importer_task_wrapper(list_key, offset=0, count=1,
                              since_last_changed=None)
