IP=$1

set -e

# Prepare the server (fix directories, install docker, stop tmux sessions, install make)
ssh -oStrictHostKeyChecking=no -i ~/.ssh/aws5-ap-southeast-2.pem ubuntu@"$IP" bash < ./bin/remote_prepare.sh

# Copy the files over
scp -oStrictHostKeyChecking=no -i ~/.ssh/aws5-ap-southeast-2.pem -r . ubuntu@"$IP":~/codequest/repo

# Remove unwanted files and run script in tmux
ssh -oStrictHostKeyChecking=no -i ~/.ssh/aws5-ap-southeast-2.pem ubuntu@"$IP" bash < ./bin/remote_run.sh
