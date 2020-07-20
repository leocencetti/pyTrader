###
# File created by Leonardo Cencetti on 7/19/20
###
import logging
from queue import Queue


class TopicNotFound(Exception):
    pass


class TopicExistsAlready(Exception):
    pass


class Topic(Queue):
    def __init__(self, topic_name):
        super().__init__()
        self._logger = logging.getLogger(topic_name)
        self._name = topic_name

    def close(self, no_wait=False):
        """
        Closes the topic queue.
        :param bool no_wait: do not wait for the queue to be empty before closing.
        """
        if no_wait:
            self._logger.debug('Closing topic immediately, all data will be flushed.')
            with self.mutex:
                self.queue.clear()
                self.all_tasks_done.notify_all()
                self.unfinished_tasks = 0
        else:
            self._logger.debug('Waiting for queue to be emptied.')
            self.join()
        self._logger.debug('Topic closed.')


class BusManager:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._topics = dict()

    def add_topic(self, topic_name, exists_ok=False):
        """
        Creates a topic.
        :param str topic_name: name of the topic to be created.
        :param bool exists_ok: raise exception if topic exists already.
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

        return self

    def remove_topic(self, topic_name, no_wait=False, missing_ok=True):
        """
        Removes a specific topic.
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

    def get_topic(self, topic_name, create_if_missing=False):
        """
        Retrieves a topic handle.
        :param str topic_name: name of the topic to be retrieved.
        :param bool create_if_missing: creates the topic if not found.
        :return: Topic: topic instance.
        """
        if topic_name not in self._topics:
            if create_if_missing:
                self._logger.warning('Bus "{}" does not exists, creating it.'.format(topic_name))
                self.add_topic(topic_name)
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
