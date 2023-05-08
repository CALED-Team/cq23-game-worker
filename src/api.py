import os

import requests as r

USER_TOKEN = os.environ.get("USER_TOKEN")
API_URL = os.environ.get("API_URL")
DEFAULT_REQUEST_PARAMS = {"headers": {"Authorization": f"Token {USER_TOKEN}"}}

if USER_TOKEN is None or API_URL is None:
    print("Env vars not set properly, good bye.")
    quit()

if API_URL[-1] == "/":
    API_URL = API_URL[:-1]

FETCH_PENDING_ENDPOINT = API_URL + "/api/matches/fetch_pending/"
SAVE_RESULTS_ENDPOINT = API_URL + "/api/matches/{id}/save_match_results/"


def get_pending_match():
    """
    Requests the API for a match waiting to be played. If a match is not returned, it will return None.
    :return: The serialized match object if there is any. None otherwise.
    """
    try:
        response = r.get(FETCH_PENDING_ENDPOINT, **DEFAULT_REQUEST_PARAMS)
        data = response.json()
    except Exception as e:
        print("Error while requesting new match:", str(e))
        return None

    if data.get("message", "") is None:
        print("No more pending matches for now.")
        return None

    if not data.get("id", None):
        print("Error while fetching new match (no id):", data.get("message", None))
        return None

    return data


# def set_submission_build_status(submission_id, status):
#     try:
#         response = r.post(
#             UPDATE_STATUS_ENDPOINT.format(id=submission_id),
#             json={"status": status},
#             **DEFAULT_REQUEST_PARAMS,
#         )
#         data = response.json()
#         print(f"Set build status for submission {submission_id}: {data['message']}")
#     except Exception as e:
#         print(f"Error when setting submission status for id {submission_id}:", str(e))
