try:
    import s3fs
    import os

    fs = s3fs.S3FileSystem(client_kwargs={"endpoint_url":os.environ["S3_ENDPOINT"]})
    fs.mkdir("metaflow-data")
except:
    pass