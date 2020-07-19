###
# File created by Leonardo Cencetti on 7/19/20
###
from queue import Queue
import logging


class TopicNotFound(Exception):
    pass


class TopicExistsAlready(Exception):
    pass


class Topic:
    def __init__(self, topic_name):
        self._bus = Queue()
        self._logger = logging.getLogger(topic_name)
        self._name = topic_name

    def get(self, no_wait=False):
        """
        Gets the next item in the topic queue.
        :param bool no_wait: do not wait for item to be available in the queue.
        :return: item of the queue.
        """
        if no_wait:
            return self._bus.get_nowait()
        else:
            return self._bus.get()

    def put(self, item, no_wait=False):
        """
        Adds an item to the topic queue.
        :param item: item to be added.
        :param bool no_wait: do not wait for an empty slot in the queue.
        """
        if no_wait:
            self._bus.put_nowait(item)
        else:
            self._bus.put(item)

    def close(self, no_wait=False):
        """
        Closes the topic queue.
        :param bool no_wait: do not wait for the queue to be empty before closing.
        """
        if no_wait:
            self._logger.debug('Closing topic immediately, all data will be flushed.')
            with self._bus.mutex:
                self._bus.queue.clear()
                self._bus.all_tasks_done.notify_all()
                self._bus.unfinished_tasks = 0
            self._bus = None
        else:
            self._logger.debug('Waiting for queue to be emptied.')
            self._bus.join()
            self._bus = None
        self._logger.debug('Topic closed.')


class BusManager:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._topics = dict()

    def add_bus(self, topic_name, exists_ok=False):
        """
        Adds a bus.
        :param str topic_name: name of the topic to be created.
        :param bool exists_ok: raise exception if topic exists already.
        :return: Topic: topic instance.
        """
        if topic_name in self._topics:
            if exists_ok:
                self._logger.info('Bus "{}" exists already: overwriting.'.format(topic_name))
                self._topics[topic_name] = Topic(topic_name)
            else:
                msg = 'Bus "{}" exists already: skipping creation.'.format(topic_name)
                self._logger.error(msg)
                raise TopicExistsAlready(msg)
        else:
            self._logger.debug('Created bus "{}".'.format(topic_name))
            self._topics[topic_name] = Topic(topic_name)

        return self._topics[topic_name]

    def remove_bus(self, topic_name, no_wait=False, missing_ok=True):
        """
        Removes a specific bus.
        :param str topic_name: name of the topic to be removed.
        :param bool no_wait: do not wait for the topic to be empty before closing.
        :param bool missing_ok: raise exception if topic is not found.
        """
        if topic_name in self._topics:
            self._topics[topic_name].close(no_wait)
            del self._topics[topic_name]
            self._logger.debug('Bus "{}" deleted.'.format(topic_name))
            return

        if missing_ok:
            self._logger.warning('Bus "{}" does not exists, skipping.'.format(topic_name))
            return
        else:
            msg = 'Bus "{}" does not exists.'.format(topic_name)
            self._logger.error(msg)
            raise TopicNotFound(msg)

    def get_bus(self, topic_name, create_if_missing=False):
        """
        Retrieves a topic handle.
        :param str topic_name: name of the topic to be retrieved.
        :param bool create_if_missing: creates the topic if not found.
        :return: Topic: topic instance.
        """
        if topic_name not in self._topics:
            if create_if_missing:
                self._logger.warning('Bus "{}" does not exists, creating it.'.format(topic_name))
                self.add_bus(topic_name)
            else:
                msg = 'Bus "{}" does not exists.'.format(topic_name)
                self._logger.error(msg)
                raise TopicNotFound(msg)

        return self._topics[topic_name]

    def close(self, no_wait=False):
        """
        Closes all topics on the bus.
        :param bool no_wait:  do not wait for topics to be empty before closing.
        """
        for topic in self._topics.values():
            topic.close(no_wait)
