import base64
import os
import pathlib
import shutil

import boto3
import docker
from docker.errors import APIError, ImageNotFound, NotFound

AWS_REGION = "us-east-1"
ECR_REGISTRY = os.environ.get("ECR_REGISTRY")
SUBMISSIONS_ECR_REPO = os.environ.get("SUBMISSIONS_ECR_REPO")
GAME_SERVER_ECR_REPO = os.environ.get("GAME_SERVER_ECR_REPO")
IMAGE_TAG_PREFIX = os.environ.get("IMAGE_TAG_PREFIX", "")

if SUBMISSIONS_ECR_REPO is None or ECR_REGISTRY is None:
    print("ECR details should be provided in the env vars, bye.")
    quit()

ECR_CLIENT = boto3.client("ecr-public", region_name=AWS_REGION)

# Authenticate Docker to ECR registry
token = ECR_CLIENT.get_authorization_token()
username, password = (
    base64.b64decode(token["authorizationData"]["authorizationToken"])
    .decode()
    .split(":")
)

DOCKER_CLIENT = docker.from_env()
DOCKER_CLIENT.login(username, password, registry=ECR_REGISTRY)


def get_submission_image_tag(submission_id):
    return (
        f"{ECR_REGISTRY}/{SUBMISSIONS_ECR_REPO}:{IMAGE_TAG_PREFIX}{str(submission_id)}"
    )


def get_server_image_tag():
    return f"{ECR_REGISTRY}/{GAME_SERVER_ECR_REPO}:latest"


def pull_latest_game_server():
    game_server_image = get_server_image_tag()
    try:
        DOCKER_CLIENT.images.pull(game_server_image)
    except APIError:
        print("Failed to pull the game server!")
        return False
    return True


def pull_submissions(submissions: list):
    """
    Makes sure all submission images are available in the local host. If any of them fails, it will return False.
    Otherwise it will return True.
    """
    for submission in submissions:
        submission_image = get_submission_image_tag(submission["id"])
        try:
            DOCKER_CLIENT.images.get(submission_image)
            print(f"Image for submission {str(submission['id'])} already exists.")
        except ImageNotFound:
            print(
                f"Image for submission {str(submission['id'])} doesn't exist, pulling... ",
                end="",
            )
            DOCKER_CLIENT.images.pull(submission_image)
            print("done!")
        except NotFound:
            print(
                f"Image for submission {str(submission['id'])} not found! Match failed."
            )
            return False

    return True


def copy_replay_files():
    volume_name = "cq-game-replay"
    local_dir = "_replay_files"

    # Ensure the local directory exists and is empty
    os.makedirs(local_dir, exist_ok=True)
    for root, dirs, files in os.walk(local_dir):
        # Delete all files in the current directory
        for file in files:
            os.remove(os.path.join(root, file))
        # Delete all subfolders and their contents
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))

    # Get the Docker volume and its associated container
    try:
        DOCKER_CLIENT.volumes.get(volume_name)
    except NotFound:
        print("Volume does not exist! Something has failed.")
        return False

    cmd = ["/bin/sh", "-c", f"cp -r /data/* /{local_dir}"]
    pwd = pathlib.Path(__file__).parent.parent.resolve()
    DOCKER_CLIENT.containers.run(
        "busybox",
        cmd,
        detach=True,
        remove=True,
        volumes={
            volume_name: {"bind": "/data", "mode": "ro"},
            f"{pwd}/{local_dir}": {"bind": f"/{local_dir}", "mode": "rw"},
        },
    )

    return True
