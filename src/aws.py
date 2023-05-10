import os

import boto3


def move_replay_volume_to_s3(match):
    local_dir = "_replay_files"

    # Set the S3 bucket details
    bucket_name = "cq-match-replays"

    # Create an S3 client
    s3 = boto3.client("s3")

    # Iterate through all files in the local folder
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            # Set the local file path
            local_file_path = os.path.join(root, file)

            # Set the S3 object key (destination file path in S3)
            s3_object_key = f"match-{str(match['id'])}-{match['play_attempts']}/{file}"

            # Upload the file to S3
            s3.upload_file(local_file_path, bucket_name, s3_object_key)

            print(
                f"Uploaded: {local_file_path} to S3 bucket: {bucket_name} as: {s3_object_key}"
            )

    print("All files uploaded to S3 successfully.")
