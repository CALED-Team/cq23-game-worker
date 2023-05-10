# CQ23 Game Worker

The game worker is responsible for:

1. Fetching a match from the teams portal
2. Downloading the clients of that match and the latest game server
3. Running the match by connecting the clients and game server through GCS
4. Sending the results back to the teams portal

### Required Env Vars

Env vars are stored in `.envs/.local` and `.envs/.prod`. Here's a template to fill your local with:
```shell
export USER_TOKEN=
export API_URL=http://localhost:8000
export ECR_REGISTRY=
export SUBMISSIONS_ECR_REPO=
export GAME_SERVER_ECR_REPO=
export IMAGE_TAG_PREFIX=debug-
```

Variable definitions:
- API_URL: the API url. Set `http://localhost:8000` for local dev and `https://api.codequest.club` for production (or whatever the URL is when you use this).
- USER_TOKEN: there should be a user created for this app in Teams Portal. Put that user's token here so it can log into the API.
- ECR_REGISTRY: the ECR Registry URL (looks like public.ecr.aws/<id>/)
- SUBMISSIONS_ECR_REPO: the ECR repo used for the submissions
- GAME_SERVER_ECR_REPO: the ECR repo used for the game server image
- IMAGE_TAG_PREFIX: Optional - prefix to the tag of images. It's useful when running from your local and want to use special images like "test-".

### Deployment

The AWS role connected to this service needs `ecr:GetAuthorizationToken` permission to be able to login to the ECR (or `AmazonEC2ContainerRegistryFullAccess`) and full access to S3 to upload the replay files.

In order to deploy new workers, create an EC2 instance, apply the required roles and permissions (above) then run:
```shell
make deploy ip=....
```

Where `ip` is the ip of the new instance. Correct ssh keys should be used. This is defined in `bin/deploy.sh`.
