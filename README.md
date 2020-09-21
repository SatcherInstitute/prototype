## Deploying functions manually
This may be useful either:
- until terraform and fully automated deployment is set up
- for manual testing. Different cloud functions can be deployed from the same source code, so you can deploy to a test function without affecting the main thing.

### One-time setup
Install Cloud SDK ([Quickstart](https://cloud.google.com/sdk/docs/quickstart))

### Creating a function
Although a function can be created via the `gcloud functions deploy` command, there are some options you need to configure the first time it is deployed. It is much easier to create the function from the cloud console, and then use the command line to deploy source code updates.

### Deploying a function
Once a function is created, to deploy it from the command line:
1. Navigate to the directory the `main.py` function is in
2. Run `gcloud functions deploy fn_name`

Note that this **deploys the contents of the current directory** to the **cloud function specified by fn_name**. Be careful as this will overwrite the contents of `fn_name` with the contents of the current directory. You can use this for testing and development by deploying the source code to a test function.

### Deploying other resources
I haven't tried deploying resources other than functions from the command line. Resources like GCS buckets and topics are pretty easy to create from the cloud console though, so it's probably easiest to set those up manually.

### Changing function configuration
To change configuration details, you have to specify these options in the `deploy` command. For example:
- If you need to change the entrypoint, use the `--entry-point` option.
- If you need to change the trigger topic, use the `--trigger-topic` option.

A full list of options can be found [here](https://cloud.google.com/sdk/gcloud/reference/functions/deploy). Changing configuration of the function is usually easier from the cloud console UI.

## Testing functions
To test a function triggered by a topic, run
`gcloud pubsub topics publish projects/fellowship-test-internal/topics/your_topic_name --message "your_message"`
- your_topic_name is the name of the topic the function specified as a trigger.
- your_message is the json message that will be serialized and passed to the `'data'` property of the event.

### Testing example
For example, you can use the following command to trigger ingestion for the list of state names and state codes (note that backslashes are required on Windows because Windows is weird and messes up serialization if you don't. OS X or Linux may not require backslashes, I'm not sure).

`gcloud pubsub topics publish projects/fellowship-test-internal/topics/aaron-test-pubsub --message "{\"id\":\"STATE_NAMES\", \"url\":\"https://api.census.gov/data/2010/dec/sf1\", \"gcs_bucket\":\"population_bucket\", \"filename\":\"state_names.json\"}"`

## Python function dependencies
When developing, if a new dependency is needed:
1. Add it to requirements.in
2. Run  `pip-compile requirements.in`. This will generate a requirements.txt file
3. Run `pip install -r requirements.txt`

During development you can also just run `pip install new_dep`, but remember to add it to requirements.in and run `pip-compile requirements.in` before checking in code or deploying the function.

## Python environment setup
TODO instructions for us all to be on the same python virtual environment setup.