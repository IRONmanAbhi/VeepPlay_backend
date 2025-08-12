from flask import current_app


def generate_presigned_url(s3_key):
    s3 = current_app.s3_client
    bucket_name = current_app.config["AWS_BUCKET_NAME"]

    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": s3_key},
        ExpiresIn=3600,
    )
