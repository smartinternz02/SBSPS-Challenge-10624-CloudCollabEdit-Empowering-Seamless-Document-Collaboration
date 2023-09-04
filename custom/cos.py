import ibm_db
from .config import IBM_COS_API_KEY_ID,IBM_COS_BUCKET_NAME,IBM_COS_ENDPOINT,IBM_COS_INSTANCE_CRN
import ibm_boto3
from ibm_botocore.client import Config


def cos_connect():
    cos = ibm_boto3.client(
        "s3",
        ibm_api_key_id=IBM_COS_API_KEY_ID,
        ibm_service_instance_id=IBM_COS_INSTANCE_CRN,
        config=Config(signature_version="oauth"),
        endpoint_url=IBM_COS_ENDPOINT
    )
    return cos