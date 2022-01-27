import celery


class BaseTask(celery.Task):
    """
    This base task supplies the logger to the underlying worker on init.
    The logger may then be used like this: `self.logger.info("Hi")`
    """

    def __init__(self):
        import logging

        self.logger = logging.getLogger(__name__)
