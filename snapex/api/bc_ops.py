import pybcs
import tempfile
import polls.db_ops as db_ops
from snapex.settings import BCS_SETTINGS
from polls.models import *
from django.core.files.uploadedfile import *

HOST = "http://bcs.duapp.com/"
AK = "4vvtke0DV3yR9bIYcGyDvKBC"
SK = "1B65i354OUTyyyVxMhI9IlgBxFztCp84"

def put_photo_for_answer(filename, data, answer):
    #bucket_name = "snapex-photos"
    #return put_object_direct(bucket_name, filename, data)
    suf = SimpleUploadedFile(filename, data, content_type="image/jpg")
    media = MediaEntry(answer = answer, bucket_name=BCS_SETTINGS["BUCKET_LIST"]["default"], object_name=filename, content=suf)
    media.save()
    return media

def put_audio_for_answer(filename, data, answer):
    #bucket_name = "snapex-audios"
    suf = SimpleUploadedFile(filename, data, content_type="audio/aac")
    media = MediaEntry(answer = answer, bucket_name=BCS_SETTINGS["BUCKET_LIST"]["default"], object_name=filename, content=suf)
    media.save()
    return media
    #return put_object_direct(bucket_name, filename, data)

def put_object_direct(bucket_name, object_name, data, db_store = True):
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
    bbcs = pybcs.BCS(HOST, AK, SK, pybcs.HttplibHTTPC)
    bucket = bbcs.bucket(bucket_name)
    bucketObject = bucket.object(object_name)
    return bucketObject.get_url

def get_media_url(media):
    bucket_name = media.bucket_name
    object_name = media.object_name
    return get_object_url(bucket_name, object_name)