import os

# IBM Cloud Object Storage configurations
IBM_COS_API_KEY_ID = "oNuqXQTjfZ_e1Y4EGwRM35Y1_HroFsHI1UgcMI9PIxdT"
IBM_COS_INSTANCE_CRN = 'crn:v1:bluemix:public:cloud-object-storage:global:a/bc7bd1cb83ac43c58f7d78f0ea6a252f:ce4e9a2d-3688-4bbc-8fdb-2d0b131f95e5::'
IBM_COS_ENDPOINT = 'https://s3.jp-tok.cloud-object-storage.appdomain.cloud'
IBM_COS_BUCKET_NAME = "cloudcollab-main"

# IBM Db2 configurations
DB2_USERNAME = 'mdb63481'
DB2_PASSWORD = 'wbOfYSgR89QY9Z5L'
DB2_HOST = '54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud'
DB2_PORT = '32733'
DB2_DATABASE = 'bludb'

# Flask configurations
SECRET_KEY = os.urandom(24)
DEBUG = True