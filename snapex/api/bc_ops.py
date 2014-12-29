import pybcs
import tempfile
import polls.db_ops as db_ops

HOST = "http://bcs.duapp.com/"
AK = "4vvtke0DV3yR9bIYcGyDvKBC"
SK = "1B65i354OUTyyyVxMhI9IlgBxFztCp84"

def put_photo(filename, data):
    bucket_name = "snapex-photos"
    return put_object(bucket_name, filename, data)

def put_audio(filename, data):
    bucket_name = "snapex-audios"
    return put_object(bucket_name, filename, data)

def put_object(bucket_name, object_name, data, db_store = True):
    tempMediaFile = tempfile.NamedTemporaryFile()
    tempMediaFile.write(data)
    bbcs = pybcs.BCS(HOST, AK, SK, pybcs.HttplibHTTPC)
    bucket = bbcs.bucket(bucket_name)
    bucketObject = bucket.object(object_name)
    bucketObject.put_file(tempMediaFile.name)
    if db_store:
        media = MediaEntry(bucket_name=bucket_name, object_name=object_name)
        media.save()
        return media
    else:
        return

def get_object_url(bucket_name, object_name):
    return