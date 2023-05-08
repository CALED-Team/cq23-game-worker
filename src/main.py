import json
import subprocess
import sys
import time
import os
import shutil

import api
import docker_tools


GCS_DIR = "game-communication-system/src"
CLIENTS_FILE_ADDRESS = "_cq-gcs-clients.json"
MATCH_TIMEOUT_SECONDS = 12 * 60


def run_gcs(match):
    clients_file_content = []
    for submission in match["submissions"]:
        clients_file_content.append({
            "id": submission["team_id"],
            "name": submission["team_name"],
            "image": docker_tools.get_submission_image_tag(submission["id"])
        })

    with open(GCS_DIR + "/" + CLIENTS_FILE_ADDRESS, "w") as f:
        f.write(json.dumps(clients_file_content))

    subprocess_args = [
        sys.executable,
        "controller.py",
        docker_tools.get_server_image_tag(),
        CLIENTS_FILE_ADDRESS
    ]
    subprocess.run(subprocess_args, timeout=MATCH_TIMEOUT_SECONDS, cwd=GCS_DIR)
    os.remove(GCS_DIR + "/" + CLIENTS_FILE_ADDRESS)


if __name__ == "__main__":
    print("Starting the main loop...")
    while True:
        # match = api.get_pending_match()
        match = {'id': 8, 'submissions': [{'id': 2, 'team_id': 1, 'team_name': 'Test Team 1'}, {'id': 3, 'team_id': 3, 'team_name': 'Test TEAM 2'}], 'context': {'map': 'map2.txt', 'game': 'game2'}, 'last_requested_at': '2023-05-08T21:36:49.460208+10:00', 'played_status': 'playing', 'play_attempts': 2, 'results': None, 'match_group': 1}
        print("Received match:")
        print(match)

        if match:
            fetch_result = docker_tools.pull_latest_game_server()
            for sub in match["submissions"]:
                sub["id"] = 2
            fetch_result &= docker_tools.pull_submissions(match["submissions"])

            if not fetch_result:
                print("Something went wrong with pulling the images! Going to the next match...")
                continue

            print("Running the GCS...")
            run_gcs(match)

            print("All done! Copying the replay files...")
            copy_result = docker_tools.copy_replay_files()
            if not copy_result:
                print("Match failed - we'll retry later...")
                continue
            else:
                print("Replay files copied.")

            # shutil.rmtree("replay_files")
            break

        else:
            time.sleep(30)
