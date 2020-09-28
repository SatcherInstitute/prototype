## Deploying functions manually
This may be useful either:
- until terraform and fully automated deployment is set up
- for manual testing/experimentation. Different cloud functions can be deployed from the same source code, so you can deploy to a test function without affecting any of the other resources.

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
`gcloud pubsub topics publish projects/temporary-sandbox-290223/topics/your_topic_name --message "your_message"`
- your_topic_name is the name of the topic the function specified as a trigger.
- your_message is the json message that will be serialized and passed to the `'data'` property of the event.

### Testing example
For example, you can use the following command to trigger ingestion for the list of state names and state codes (note that backslashes are required on Windows because Windows is weird and messes up serialization if you don't. OS X or Linux may not require backslashes, I'm not sure).

`gcloud pubsub topics publish projects/temporary-sandbox-290223/topics/{upload_to_gcs_topic_name} --message "{\"id\":\"STATE_NAMES\", \"url\":\"https://api.census.gov/data/2010/dec/sf1\", \"gcs_bucket\":{gcs_landing_bucket}, \"filename\":\"state_names.json\"}"`

where `upload_to_gcs_topic_name` and `gcs_landing_bucket` are the same as the terraform variables of the same name

## Python function dependencies
When developing, if a new dependency is needed:
1. Add it to requirements.in
2. Run  `pip-compile requirements.in`. This will generate a requirements.txt file
3. Run `pip install -r requirements.txt`

During development you can also just run `pip install new_dep`, but remember to add it to requirements.in and run `pip-compile requirements.in` before checking in code or deploying the function.

## Python environment setup
TODO instructions for us all to be on the same python virtual environment setup.

## Building a Cloud Run image manually

Run `gcloud builds submit --tag gcr.io/{PROJECT_ID}/{YOUR_IMAGE_NAME}` from the directory which contains the Dockerfile for the service

Then set the service's image path variable in the terraform configuration to the tag. 

TODO: Local docker build instructions

## Cloud Run local testing with an emulator

The [Cloud Code](https://cloud.google.com/code) plugin for
[VS Code](https://code.visualstudio.com/) and [JetBrains IDEs](https://www.jetbrains.com/)
lets you locally run and debug your container image in a Cloud Run
emulator within your IDE. The emulator allows you configure an environment that is
representative of your service running on Cloud Run.

### Installation
1. Install Cloud Run for [VS Code](/code/docs/vscode/install) or a [JetBrains IDE](/code/docs/intellij/install).
0. Follow the instructions for locally developing and debugging within your IDE.
   - **VS Code**: Locally [developing](/code/docs/vscode/developing-a-cloud-run-app) and [debugging](/code/docs/intellij/debugging-a-cloud-run-app)
   - **IntelliJ**: Locally [developing](/code/docs/vscode/developing-a-cloud-run-app) and [debugging](/code/docs/intellij/debugging-a-cloud-run-app)

### Running the emualtor
1. After installing the VS Code plugin, a `Cloud Code` entry should be added to the bottom toolbar of your editor.
2. Clicking on this and selecting the `Run on Cloud Run emulator` option will begin the process of setting up the configuration for your Cloud Run service.
3. Give your service a name
4. Set the service container image url with the following format: `gcr.io/<PROJECT_ID>/<NAME>`
5. Make sure the builder is set to `Docker` and the correct Dockerfile path is selected, `prototype/run_ingestion/Dockerfile`
7. Ensure the `Automatically re-build and re-run on changes` checkbox is selected for hot reloading.
6. Click run

### Sending requests
After your Docker container successfully builds and is running locally you can start sending requests.

1. Open a terminal
2. Send curl requests in the following format: 

```DATA=$(printf '{"id":<INGESTION_ID>,"url":<INGESTION_URL>,"gcs_bucket":<BUCKET_NAME>,"filename":<FILE_NAME>}' |base64) && curl --header "Content-Type: application/json" -d '{"message":{"data":"'$DATA'"}}' http://localhost:8080```

### Accessing Google Cloud Services
1. [Create a service account in Pantheon](https://cloud.google.com/docs/authentication/getting-started)
2. Using IAM, grant the appropriate permissions to the service account
3. Inside the `launch.json` file, set the `configuration->service->serviceAccountName` attribute to the service account email you just created.

## Deploying your own instance with terraform
To run the pipeline with terraform, create your own `terraform.tfvars` file in the same directory as the other terraform files. For each variable declared in `prototype_variables.tf` that doesn't have a default, add your own for testing. Typically your own variables should be unique and can just be prefixed with your name or ldap. There are some that have specific requirements like project ids, code paths, and image paths.

Currently the setup deploys both a data ingestion cloud funtion and a data ingestion cloud run instance. These are duplicates of each other. Once we get the cloud run one fully working we will delete the cloud fuction, but for now if you want to not have a duplicate while developing you can just comment out the setup for whichever one you don't want to use in `prototype.tf`

Note that currently terraform doesn't diff the contents of the functions/cloud run service, so to get them to redeploy you can either
1. Call `terraform destroy` every time before `terraform apply`, or
2. Use [`terraform taint`](https://www.terraform.io/docs/commands/taint.html) to mark a resource as requiring redeploy
