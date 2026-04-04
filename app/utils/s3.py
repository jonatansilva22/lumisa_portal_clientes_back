import boto3
from botocore.exceptions import ClientError
import os
from typing import Optional

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )

def generate_presigned_url(bucket: str, key: str, content_type: str, expires_in: int = 3600) -> Optional[str]:
    """
    Genera una URL presignada para subir un archivo a S3.
    """
    s3 = get_s3_client()
    try:
        url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=expires_in
        )
        return url
    except ClientError:
        return None