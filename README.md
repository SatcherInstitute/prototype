## One-time setup
Install Cloud SDK ([Quickstart](https://cloud.google.com/sdk/docs/quickstart))  
Install Terraform ([Getting started](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/gcp-get-started))  
Install Docker Desktop ([Get Docker](https://docs.docker.com/get-docker/)) 

gcloud config set project temporary-sandbox-290223

### Python environment setup

1. Create a virtual environment, for example: `python3 -m venv ../my-virutal-environment`
2. Activate the venv: `source ../my-virutal-environment/bin/activate`
3. Install pip-tools and other packages as needed: `pip install pip-tools`

## Deploying functions manually
This may be useful either:
- until terraform and fully automated deployment is set up
- for manual testing/experimentation. Different cloud functions can be deployed from the same source code, so you can deploy to a test function without affecting any of the other resources.

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

## Testing Pub/Sub triggers
To test a Cloud Function or Cloud Run service triggered by a Pub/Sub topic, run
`gcloud pubsub topics publish projects/<project-id>/topics/<your_topic_name> --message "your_message"`
- your_topic_name is the name of the topic the function specified as a trigger.
- your_message is the json message that will be serialized and passed to the `'data'` property of the event.  

Note that this method will work for the upload to GCS function or service, which expects to read information from the `'data'` field. The GCS-to-BQ function or service expects to read from the `'attributes'` field, so the `--attribute` flag should be used instead. See [Documentation](https://cloud.google.com/sdk/gcloud/reference/pubsub/topics/publish) for details.

### Testing example
For example, you can use the following command to trigger ingestion for the list of state names and state codes (note that backslashes are required on Windows because Windows is weird and messes up serialization if you don't. OS X or Linux may not require backslashes, I'm not sure).

`gcloud pubsub topics publish projects/temporary-sandbox-290223/topics/{upload_to_gcs_topic_name} --message "{\"id\":\"STATE_NAMES\", \"url\":\"https://api.census.gov/data/2010/dec/sf1\", \"gcs_bucket\":{gcs_landing_bucket}, \"filename\":\"state_names.json\"}"`

where `upload_to_gcs_topic_name` and `gcs_landing_bucket` are the same as the terraform variables of the same name

## Python function dependencies

When developing, if a new dependency is needed:
1. Add it to requirements.in
2. Run  `pip-compile requirements.in`. This will generate a requirements.txt file
3. Run `pip install -r requirements.txt`

During development you can also just run `pip install new_dep`, but remember to add it to requirements.in and run `pip-compile requirements.in` before checking in code or deploying the function. Note, you'll need to have followed the python environment setup described above (Python environment setup) to complete these steps.

## Cloud Run local testing with an emulator

The [Cloud Code](https://cloud.google.com/code) plugin for
[VS Code](https://code.visualstudio.com/) and [JetBrains IDEs](https://www.jetbrains.com/)
lets you locally run and debug your container image in a Cloud Run
emulator within your IDE. The emulator allows you configure an environment that is
representative of your service running on Cloud Run.

### Installation
1. Install Cloud Run for [VS Code](https://cloud.google.com/code/docs/vscode/install) or a [JetBrains IDE](https://cloud.google.com/code/docs/intellij/install).
0. Follow the instructions for locally developing and debugging within your IDE.
   - **VS Code**: Locally [developing](https://cloud.google.com/code/docs/vscode/developing-a-cloud-run-app) and [debugging](https://cloud.google.com/code/docs/vscode/debugging-a-cloud-run-app)
   - **IntelliJ**: Locally [developing](https://cloud.google.com/code/docs/intellij/developing-a-cloud-run-app) and [debugging](https://cloud.google.com/code/docs/intellij/debugging-a-cloud-run-app)

### Running the emulator
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
Before deploying, make sure you have installed Terraform and a Docker client (e.g. Docker Desktop). See [One time setup](#one-time-setup) above.
1. Create your own `terraform.tfvars` file in the same directory as the other terraform files. For each variable declared in `prototype_variables.tf` that doesn't have a default, add your own for testing. Typically your own variables should be unique and can just be prefixed with your name or ldap. There are some that have specific requirements like project ids, code paths, and image paths.
2. Configure docker to use credentials through gcloud.  
```gcloud auth configure-docker```
3. On the command line, navigate to your project directory and initialize terraform.  
   ```cd path/to/your/project
   terraform init
   ```
4. Build and push your Docker images to Google Container Registry. Select any unique identifier for `your-[ingestion|gcs-to-bq]-image-name`.
   ```bash
   # Build the images locally
   docker build -t gcr.io/<project-id>/<your-ingestion-image-name> run_ingestion/
   docker build -t gcr.io/<project-id>/<your-gcs-to-bq-image-name> run_gcs_to_bq/
   
   # Upload the image to Google Container Registry
   docker push gcr.io/<project-id>/<your-ingestion-image-name>
   docker push gcr.io/<project-id>/<your-gcs-to-bq-image-name>
   ```
5. Deploy via Terraform.  
   ```bash
   # Get the latest image digests
   export TF_VAR_run_ingestion_image_path=$(gcloud container images describe gcr.io/<project-id>/<your-ingestion-image-name> \
   --format="value(image_summary.fully_qualified_digest)")
   export TF_VAR_run_gcs_to_bq_image_path=$(gcloud container images describe gcr.io/<project-id>/<your-gcs-to-bq-image-name> \
   --format="value(image_summary.fully_qualified_digest)")
   
   # Deploy via terraform, providing the paths to the latest images so it knows to redeploy
   terraform apply -var="run_ingestion_image_path=$TF_VAR_run_ingestion_image_path" \
   -var="run_gcs_to_bq_image_path=$TF_VAR_run_gcs_to_bq_image_path
   ```
6. To redeploy, e.g. after making changes to a Cloud Run service, repeat steps 4-5. Make sure you run the commands from your base project dir.

Note: Currently the setup deploys both a cloud funtion and a cloud run instance for each pipeline. These are duplicates of each other. Eventually, we will delete the cloud fuctions, but for now you can just comment out the setup for whichever one you don't want to use in `prototype.tf`

Note: Terraform doesn't diff the contents of the functions/cloud run service, so to redeploy them you can either
1. Call `terraform destroy` every time before `terraform apply`, 
2. Use [`terraform taint`](https://www.terraform.io/docs/commands/taint.html) to mark a resource as requiring redeploy, or
3. In the case of Cloud Run, use the fully qualified digest as the image path as described in Step 5.
