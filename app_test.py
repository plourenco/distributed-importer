from unittest.mock import ANY, patch
from pytest import raises
from app import importer_task_wrapper
from celery.exceptions import Reject, MaxRetriesExceededError


@patch('app.importer.get_members', return_value=[[], 0])
@patch('app.consumer.run', return_value=0)
def test_success(consumer_run, importer_get_members):
    list_key = 'foo'
    importer_task_wrapper(list_key, offset=0, count=1, since_last_changed=None)
    importer_get_members.assert_called_with(ANY, list_key, 0, 1, None)
    consumer_run.assert_called_with([])


@patch('app.importer.get_members')
@patch('app.consumer.run', return_value=0)
def test_failure(consumer_run, importer_get_members):
    list_key = 'foo'
    members = [{}, {}]
    importer_get_members.return_value = [members, 100]
    with raises(Exception):
        importer_task_wrapper(list_key, offset=0, count=1,
                              since_last_changed=None)
    importer_get_members.assert_called_with(ANY, list_key, 0, 1, None)
    consumer_run.assert_called_with(members)


@patch('app.importer_task_wrapper.retry')
@patch('app.importer.get_members')
def test_failure_reject(importer_get_members, importer_task_wrapper_retry):
    list_key = 'foo'
    importer_get_members.side_effect = Exception('test')
    importer_task_wrapper_retry.side_effect = MaxRetriesExceededError('test')
    with raises(Reject):
        importer_task_wrapper(list_key, offset=0, count=1,
                              since_last_changed=None)
