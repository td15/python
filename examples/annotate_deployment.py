"""
This example covers the following:
    - Create a Kubernetes Deployment
    - Annotate the Deployment
"""

from kubernetes import client, config
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def create_deployment_object():
    """Creates a Kubernetes Deployment object for an Nginx pod."""
    container = client.V1Container(
        name="nginx-sample",
        image="nginx",
        image_pull_policy="IfNotPresent",
        ports=[client.V1ContainerPort(container_port=80)],
    )

    # Define Pod Template
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "nginx"}),
        spec=client.V1PodSpec(containers=[container])
    )

    # Define Deployment Spec
    spec = client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(match_labels={"app": "nginx"}),
        template=template
    )

    # Create Deployment
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="deploy-nginx"),
        spec=spec
    )

    return deployment


def create_deployment(apps_v1_api, deployment_object, namespace="default"):
    """Creates a deployment in the specified Kubernetes namespace."""
    try:
        apps_v1_api.create_namespaced_deployment(
            namespace=namespace, body=deployment_object
        )
        logging.info(f"Deployment 'deploy-nginx' created in namespace '{namespace}'.")
    except client.exceptions.ApiException as e:
        logging.error(f"Error creating deployment: {e}")


def annotate_deployment(apps_v1_api, deployment_name, namespace, new_annotations):
    """Adds annotations to an existing Kubernetes deployment."""
    try:
        deployment = apps_v1_api.read_namespaced_deployment(deployment_name, namespace)
        existing_annotations = deployment.metadata.annotations or {}

        # Merge existing annotations with new ones
        updated_annotations = {**existing_annotations, **new_annotations}

        patch_body = {
            "metadata": {
                "annotations": updated_annotations
            }
        }

        apps_v1_api.patch_namespaced_deployment(
            name=deployment_name, namespace=namespace, body=patch_body
        )

        logging.info(f"Annotations updated for deployment '{deployment_name}'.")
    except client.exceptions.ApiException as e:
        logging.error(f"Error annotating deployment: {e}")


def main():
    """Main function to create and annotate a Kubernetes Deployment."""
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    namespace = "default"

    deployment_obj = create_deployment_object()
    create_deployment(apps_v1_api, deployment_obj, namespace)

    # Wait for deployment to be created
    time.sleep(2)

    deployment = apps_v1_api.read_namespaced_deployment("deploy-nginx", namespace)
    logging.info(f"Before annotation: {deployment.metadata.annotations}")

    # New Annotations
    new_annotations = {
        "deployment.kubernetes.io/str": "nginx",
        "deployment.kubernetes.io/int": "5"
    }

    annotate_deployment(apps_v1_api, "deploy-nginx", namespace, new_annotations)
    time.sleep(2)

    updated_deployment = apps_v1_api.read_namespaced_deployment("deploy-nginx", namespace)
    logging.info(f"After annotation: {updated_deployment.metadata.annotations}")


if __name__ == "__main__":
    main()
