rm -rf ~/codequest || echo "codequest directory doesn't exist, creating it..."
mkdir -p ~/codequest/repo
cd ~/codequest || exit

sudo apt install -y make python3-pip

curl -fsSL https://get.docker.com -o get-docker.sh
docker -v || sudo sh get-docker.sh

tmux kill-server || echo "Tmux already not running"
