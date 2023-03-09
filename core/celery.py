import os
from celery import Celery, bootsteps
from kombu import Exchange, Queue

__all__ = ('celery')

CELERY_BROKER = os.getenv('CELERY_BROKER')


class DeadLetterQueue(bootsteps.StartStopStep):
    """
    Create a DL exchange and queue before the worker starts processing tasks
    """
    requires = {'celery.worker.components:Pool'}

    def start(self, worker):
        dlx = Exchange('dlx', type='direct')

        dead_letter_queue = Queue(
            'dead_letter', dlx, routing_key='dead_letter')

        with worker.app.pool.acquire() as conn:
            dead_letter_queue.bind(conn).declare()


celery = Celery('tasks', broker=CELERY_BROKER,
                backend='db+sqlite:///celery.db', include=['app'])
DLQ_OPTIONS = {
    'x-dead-letter-exchange': 'dlx',
    'x-dead-letter-routing-key': 'dead_letter'
}
default_exchange = Exchange('default', type='direct')
dlx_exchange = Exchange('dlx', type='direct')
default_queue = Queue('default',
                      default_exchange,
                      routing_key='default',
                      queue_arguments=DLQ_OPTIONS)
dead_letter_queue = Queue('dead_letter', dlx_exchange,
                          routing_key='dead_letter')
celery.conf.task_queues = (default_queue,)

celery.steps['worker'].add(DeadLetterQueue)

celery.conf.task_default_queue = 'default'
celery.conf.task_default_exchange = 'default'
celery.conf.task_default_routing_key = 'default'
