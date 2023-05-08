cd ~/codequest/repo || exit

rm -rf .idea
rm -rf .git
rm -rf _submission*
rm -rf replay_files
rm .python-version

source .envs/.prod
tmux new-session -d -s my_session 'cd ~/codequest/repo || exit; make prod; bash'
