from celery.utils.log import get_task_logger
from datetime import datetime
from celery import group
from importer.base import Consumer
from celery.exceptions import Reject, MaxRetriesExceededError
from importer.base import Importer
from sqlalchemy.orm import Session
from importer.core.db import engine
from importer.core.celery import celery
from importer.models import Event

RECORDS_PER_TASK = 100
RECORD_TTL = 7200
LIST_KEYS = ('1a2d7ebf82')

consumer = Consumer()
importer = Importer()


logger = get_task_logger(__name__)


@celery.task(acks_late=True, max_retries=3, rate_limit=10)
def importer_task_wrapper(list_key, offset=0, count=10, since_last_changed=None):
    try:
        logger.debug(
            f'Get {list_key} offset {offset}, count {count}, since_last_changed {since_last_changed}')
        req_session = importer.create_session()
        members, _ = importer.get_members(
            req_session, list_key, offset, count, since_last_changed)
        imported = consumer.run(members)
        if len(members) != imported:
            raise Reject(Exception(
                f'The external count of records ({len(members)}) differs from the ones accepted at the API ({imported}).'), requeue=False)
        return imported
        # No domain specific exception handling was added for the sake of simplicity
    except Exception as exc:
        try:
            # Retries the task after 60 seconds
            importer_task_wrapper.retry(countdown=60)
        except MaxRetriesExceededError:
            raise Reject(exc, requeue=False)


@celery.task
def on_finish(results, event_id):
    with Session(engine) as db_session:
        event = db_session.get(Event, event_id)
        event.end_dt = datetime.now()
        event.count = sum(results)
        db_session.commit()


def run(list_key, since_last_changed=None):
    with (
        Session(engine) as db_session,
        importer.create_session() as req_session
    ):
        last_event = db_session.query(Event).order_by(
            Event.start_dt.desc()).first()
        if last_event:
            if last_event.end_dt is None:
                logger.error('There is an import in progress. Halting run.')
                return
            logger.info(
                f'Found last event from {last_event.start_dt}. Resuming onwards...')
        else:
            logger.info('No events found yet. Running a full import.')
        event = Event()
        db_session.add(event)
        db_session.commit()

        since_last_changed = since_last_changed or last_event and last_event.start_dt
        _, total = importer.get_members(
            req_session, list_key, offset=0, count=1, since_last_changed=since_last_changed)
        logger.info(
            f'Importing {total} records in a total of {round(total / RECORDS_PER_TASK)} tasks.')
        task_group = group(importer_task_wrapper.s(
            list_key,
            offset=i,
            count=RECORDS_PER_TASK,
            since_last_changed=since_last_changed)
            for i in range(0, total, RECORDS_PER_TASK))
        task_group.link(on_finish.s(event.id))
        task_group()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    for list_key in LIST_KEYS:
        sender.add_periodic_task(3600.0, run.s(
            list_key), name=f'import every hour ({list_key})')
