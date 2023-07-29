import json
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


def send_match_results_back(match):
    results_file = "_replay_files/results.json"
    try:
        with open(results_file) as f:
            results = json.loads(f.read())
    except FileNotFoundError:
        print("Results file not found!")
        return

    try:
        winner = str(results["victor"][0]) if len(results["victor"]) > 0 else None
        losers = list(map(str, results["vanquished"]))
    except (IndexError, KeyError):
        print("Results file is invalid, not sending it back to teams portal.")
        return

    valid_team_ids = [str(x["team_id"]) for x in match["submissions"]]
    if (winner is not None and winner not in valid_team_ids) or any(
        [loser not in valid_team_ids for loser in losers]
    ):
        print(
            "Team ids in results file do not match the ids in match object, not sending back to teams portal."
        )
        return

    try:
        res = {}
        for loser in losers:
            res[loser] = 0
        if winner is not None:
            res[winner] = 1
        response = r.post(
            SAVE_RESULTS_ENDPOINT.format(id=match["id"]),
            json=res,
            **DEFAULT_REQUEST_PARAMS,
        )
        data = response.json()
        print(f"Saved match results for id {match['id']}: {data['message']}")
    except Exception as e:
        print(f"Error when saving match results for id {match['id']}:", str(e))
