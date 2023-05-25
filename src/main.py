import json
import os
import shutil
import subprocess
import sys
import time

import api
import aws
import docker_tools

GCS_DIR = "game-communication-system/src"
CLIENTS_FILE_ADDRESS = "_cq-gcs-clients.json"
MATCH_TIMEOUT_SECONDS = 12 * 60
DEBUG = True


def run_gcs(match):
    clients_file_content = []
    for submission in match["submissions"]:
        clients_file_content.append(
            {
                "id": submission["team_id"],
                "name": submission["team_name"],
                "image": docker_tools.get_submission_image_tag(submission["id"]),
            }
        )

    with open(GCS_DIR + "/" + CLIENTS_FILE_ADDRESS, "w") as f:
        f.write(json.dumps(clients_file_content))

    subprocess_args = [
        sys.executable,
        "controller.py",
        docker_tools.get_server_image_tag(),
        CLIENTS_FILE_ADDRESS,
    ]
    match_context = match["context"]
    if type(match_context) == dict and "map" in match_context:
        subprocess_args.append("--server-arg")
        subprocess_args.append(match_context["map"])

    gcs_logs = subprocess.run(
        subprocess_args,
        timeout=MATCH_TIMEOUT_SECONDS,
        cwd=GCS_DIR,
        capture_output=True,
        text=True,
    )
    print(gcs_logs.stdout)
    print(gcs_logs.stderr)

    os.remove(GCS_DIR + "/" + CLIENTS_FILE_ADDRESS)
    return gcs_logs


def print_gcs_logs_in_replay_volume(gcs_logs):
    if gcs_logs.stdout:
        with open("_replay_files/gcs_logs.out", "w") as f:
            f.write(gcs_logs.stdout)

    if gcs_logs.stderr:
        with open("_replay_files/gcs_logs.err", "w") as f:
            f.write(gcs_logs.stderr)


def copy_container_logs_to_replay_volume():
    src_directory = os.path.join(GCS_DIR, "container_logs")
    dst_directory = "_replay_files"
    for filename in os.listdir(src_directory):
        src_file = os.path.join(src_directory, filename)
        dst_file = os.path.join(dst_directory, filename)
        # Copy the file to the destination directory
        shutil.copy2(src_file, dst_file)


if __name__ == "__main__":
    print("Starting the main loop...")
    while True:
        if DEBUG:
            match = {
                "id": 8,
                "submissions": [
                    {"id": 2, "team_id": 1, "team_name": "Test Team 1"},
                    {"id": 2, "team_id": 3, "team_name": "Test TEAM 2"},
                ],
                "context": {"map": "map2.txt", "game": "game2"},
                "last_requested_at": "2023-05-08T21:36:49.460208+10:00",
                "played_status": "playing",
                "play_attempts": 2,
                "results": None,
                "match_group": 1,
            }
        else:
            match = api.get_pending_match()

        print("Received match:")
        print(match)

        if match:
            print("Pulling game server image...")
            fetch_result = docker_tools.pull_latest_game_server()
            print("Pulling clients image...")
            fetch_result &= docker_tools.pull_submissions(match["submissions"])

            if not fetch_result:
                print(
                    "Something went wrong with pulling the images! Going to the next match..."
                )
                continue

            print("Running the GCS...")
            gcs_logs = run_gcs(match)

            print("All done! Copying the replay files...")
            copy_result = docker_tools.copy_replay_files()
            if not copy_result:
                print("Match failed - we'll retry later...")
                continue
            else:
                print("Replay files copied.")

            print_gcs_logs_in_replay_volume(gcs_logs)
            copy_container_logs_to_replay_volume()
            aws.move_replay_volume_to_s3(match)
            api.send_match_results_back(match)
            shutil.rmtree("_replay_files")

            if DEBUG:
                break

        else:
            time.sleep(30)
