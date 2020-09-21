import logging
from google.cloud import pubsub_v1


def notify_data_ingested(id, gcs_bucket, filename):
  """Publishes a notification on the notify-data-ingested topic indicating that
     some data was ingested.

     id: The id of the source that was ingested
     gcs_bucket: The name of the bucket the data is located in
     filename: The name of the file that was uploaded"""
  topic = 'notify-data-ingested'
  notify_topic(topic, id=id, gcs_bucket=gcs_bucket, filename=filename)


def notify_topic(topic, **attrs):
  """Publishes a notification on the specified topic using the provided
     attributes

     topic: The name of the topic to notify on
     attrs: The attributes to pass through to the message"""
  publisher = pubsub_v1.PublisherClient()
  # For some reason topic_path doesn't show up as a member, but is used in the
  # official documentation:
  # https://googleapis.dev/python/pubsub/latest/publisher/api/client.html?highlight=topic_path#google.cloud.pubsub_v1.publisher.client.Client.publish
  # pylint: disable=no-member
  topic_path = publisher.topic_path('fellowship-test-internal', topic)

  # Not sure if anything here is necessary since we can add attributes
  # directly. For now just adding a message to log.
  data = 'Notifying data ingested'
  data = data.encode('utf-8')
  future = publisher.publish(topic_path, data, **attrs)

  try:
    future.result()
  except Exception as e:
    logging.warning(
        'Error publishing message on topic {}: {}'.format(topic, e))
