# Debugging the Game Execution

Place the game server, game client and the game communication system folders at the same level

folder/
├─ game-client-2/
├─ game-client-1/
├─ game-communication-system/
├─ game-server/
├─ cq-game-worker-23/

Use the following command to build the client and server docker images and run the game worker:

```sh
bin/debug_run.sh <<cq-server-folder>> <<cq-client1-folder>> <<cq-client2-folder>> <<cq-gcs-folder>>
```
