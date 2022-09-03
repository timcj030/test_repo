import datetime

from airflow import models
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator
from airflow.utils.dates import days_ago

bucket_path = models.Variable.get("bucket_path")
project_id = models.Variable.get("project_id")
gce_zone = models.Variable.get("gce_zone")
gce_region= models.Variable.get("gce_region")


default_args = {
    # Tell airflow to start one day ago, so that it runs as soon as you upload it
    "start_date": days_ago(1),
    "dataflow_default_options": {
        "project": project_id,
        # Set to your zone
         "location": gce_region,
        "zone": gce_zone,
        # This is a subfolder for storing temporary files, like the staged pipeline job.
        "tempLocation": bucket_path + "/tmp/",
    },
}

# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.
with models.DAG(
    # The id you will see in the DAG airflow page
    "composer_dataflow_dag",
    default_args=default_args,
    # The interval with which to schedule the DAG
    schedule_interval=datetime.timedelta(days=1),  # Override to match your needs
) as dag:

    start_template_job = DataflowTemplatedJobStartOperator(
        # The task id of your job
        task_id="dataflow_operator_pbsb_subscription_to_bq",
        # The name of the template. Below is a list of all the templates you can use.
        # For versions in non-production environments, use the subfolder 'latest'
        # https://cloud.google.com/dataflow/docs/guides/templates/provided-batch#gcstexttobigquery
        template="gs://dataflow-templates/latest/PubSub_Subscription_to_BigQuery",
        # Use the link above to specify the correct parameters for your template.
        parameters={
            "inputSubscription": "projects/" + project_id + "/subscriptions/priv-equity-sub",
            "outputTableSpec": project_id + ":private_equity.raw_priv_equi",
            "outputDeadletterTable": project_id + ":private_equity.error_raw_priv_equi",
        },
    )
