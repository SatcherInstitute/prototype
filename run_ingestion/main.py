import base64
import json
import logging
from common.gcf_household_income import upload_household_income
from common.di_url_file_to_gcs import url_file_to_gcs
from flask import Flask, request
app = Flask(__name__)


# Data source name literals. These correspond to a specific data ingestion workflow.
_HOUSEHOLD_INCOME = 'HOUSEHOLD_INCOME'
_CDC_COVID_DEATHS = 'CDC_COVID_DEATHS'

@app.route('/', methods=['POST'])
def ingest_data():
  """Main function for data ingestion. Receives Pub/Sub trigger and triages to the
     appropriate data ingestion workflow and returns 400 for a bad request or 204 for success."""
    envelope = request.get_json()
    if not envelope:
        logging.error('No Pub/Sub message received.')
        return ('', 400)

    if not isinstance(envelope, dict) or 'message' not in envelope:
        logging.error('Invalid Pub/Sub message format')
        return ('', 400)

    data = envelope['message']
    logging.info(f"message: {data}")

    try:
        if 'data' not in data:
            logging.warning("PubSub message missing 'data' field")
            return ('', 400)
        data = base64.b64decode(data['data']).decode('utf-8')
        event_dict = json.loads(data)
    except json.JSONDecodeError as err:
        logging.error("Could not load json object: %s", err)
        return ('', 400)

    if 'id' not in event_dict:
        logging.error(f"PubSub data missing 'id' field: {event_dict}")
        return ('', 400)
    if 'url' not in event_dict or 'gcs_bucket' not in event_dict or 'filename' not in event_dict:
        logging.error("Pubsub data must contain fields 'url', 'gcs_bucket', and 'filename'")
        return ('', 400)
    
    data_id = event_dict['id']
    logging.info(f'Ingesting {data_id} data')
    if data_id == _HOUSEHOLD_INCOME:
        upload_household_income(event_dict['url'], event_dict['gcs_bucket'], event_dict['filename'])
    else:
        url_file_to_gcs(event_dict['url'], {}, event_dict['gcs_bucket'], event_dict['filename'])

    return ('', 204)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))