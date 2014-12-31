from django.core.files.storage import Storage
from django.core.files import locks, File
from datetime import *
from dateutil.parser import *
import os, tempfile
import pybcs
from snapex.settings import BCS_SETTINGS

class BAEStorage(Storage):

    def __init__(self, domain=None, bucket=None):
        if domain is None:
            domain = BCS_SETTINGS["HOST"]
        if bucket is None:
            bucket = BCS_SETTINGS["BUCKET_LIST"]["default"]
        self.domain = domain
        self.AK = BCS_SETTINGS["AK"]
        self.SK = BCS_SETTINGS["SK"]
        self.bbcs = pybcs.BCS(self.domain, self.AK, self.SK, pybcs.HttplibHTTPC)
        self.bucket = self.bbcs.bucket(bucket)

    def _open(self, name, mode='rb'):
        """
        not allow in bae, or maybe get the object content and store in memery using StringIO is a good idea. 
        """
        raise NotImplementException()

    def _save(self, name, content):
        print content.size
        print content.__class__
        name = str(name)
        #Write the content to a temporary file
        if hasattr(content, 'temporary_file_path'):
            self.bucket.object(name).put_file(content.temporary_file_path())
        else:
            _file = None
            try:
                for chunk in content.chunks():
                    if _file is None:
                        mode = 'wb' if isinstance(chunk, bytes) else 'wt'
                        _file = tempfile.NamedTemporaryFile(mode=mode, delete=False)
                    _file.write(chunk)
            finally:
                if _file is not None:
                    _file.close()
                    self.bucket.object(name).put_file(_file.name)
                    os.unlink(_file.name)
        return name

    def delete(self, name):
        name = str(name)
        return self.bucket.object(name).delete()

    def exists(self, name):
        name = str(name)
        return name in [ob.object_name for ob in self.bucket.list_objects()]

    def listdir(self, path):
        """
        path should start with "/"
        """

        return [ob.object_name for ob in self.bucket.list_objects(prefix=path)]

    def path(self, name):  
        """
        return url instead
        """   
        name = str(name)
        return self.url

    def size(self, name):
        name = str(name)
        obj = self.bucket.object(name)
        meta_data = obj.head()
        return int(obj.head()["header"]["content-length"])

    def url(self, name): 
        name = str(name)       
        url = self.bucket.object(name).get_url
        return url

    def accessed_time(self, name):
        name = str(name)
        return self.modified_time(name) 

    def created_time(self, name):
        name = str(name)
        return self.modified_time(name)

    def modified_time(self, name):
        name = str(name)
        obj = self.bucket.object(name)
        meta_data = obj.head()
        return parse(obj.head()["header"]["last-modified"])   

    def get_available_name(self, name):
        """
        name is generally unique
        """
        name = str(name)
        return name
    