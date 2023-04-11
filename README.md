# CQ Game Worker 23

This repo is used to run a game between two clients and the game server

## Usage

Place the game server, game client and the game communication system folders at the same level

ws/
├─ game-client-2/
├─ game-client-1/
├─ game-communication-system/
├─ game-server/
├─ game-worker/

Use the following command to build the client and server docker images and run the game worker

```sh
bin/debug_run.sh <<cq-server-folder>> <<cq-client1-folder>> <<cq-client2-folder>> <<cq-gcs-folder>>
```
