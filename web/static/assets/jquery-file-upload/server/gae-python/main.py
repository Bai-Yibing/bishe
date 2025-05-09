# -*- coding: utf-8 -*-
#
# jQuery File Upload Plugin GAE Python Example 2.0
# https://github.com/blueimp/jQuery-File-Upload
#
# Copyright 2011, Sebastian Tschan
# https://blueimp.net
#
# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT
#

from __future__ import with_statement
from google.appengine.api import files, images
from google.appengine.ext import blobstore, deferred
from google.appengine.ext.webapp import blobstore_handlers
import json, re, urllib, webapp2

WEBSITE = 'http://blueimp.github.com/jQuery-File-Upload/'
MIN_FILE_SIZE = 1  # bytes
MAX_FILE_SIZE = 5000000  # bytes
IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')
ACCEPT_FILE_TYPES = IMAGE_TYPES
THUMBNAIL_MODIFICATOR = '=s80'  # max width / height
EXPIRATION_TIME = 300  # seconds


def cleanup(blob_keys):
    blobstore.delete(blob_keys)


class UploadHandler(webapp2.RequestHandler):

    def initialize(self, request, response):
        super(UploadHandler, self).initialize(request, response)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers[
            'Access-Control-Allow-Methods'
        ] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'

    def validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'File is too big'
        elif not ACCEPT_FILE_TYPES.match(file['type']):
            file['error'] = 'Filetype not allowed'
        else:
            return True
        return False

    def get_file_size(self, file):
        file.seek(0, 2)  # Seek to the end of the file
        size = file.tell()  # Get the position of EOF
        file.seek(0)  # Reset the file position to the beginning
        return size

    def write_blob(self, data, info):
        blob = files.blobstore.create(
            mime_type=info['type'],
            _blobinfo_uploaded_filename=info['name']
        )
        with files.open(blob, 'a') as f:
            f.write(data)
        files.finalize(blob)
        return files.blobstore.get_blob_key(blob)

    def handle_upload(self):
        results = []
        blob_keys = []
        for name, fieldStorage in self.request.POST.items():
            if type(fieldStorage) is unicode:
                continue
            result = {}
            result['name'] = re.sub(r'^.*\\', '',
                                    fieldStorage.filename)
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            if self.validate(result):
                blob_key = str(
                    self.write_blob(fieldStorage.value, result)
                )
                blob_keys.append(blob_key)
                result['delete_type'] = 'DELETE'
                result['delete_url'] = self.request.host_url + \
                                       '/?key=' + urllib.quote(blob_key, '')
                if (IMAGE_TYPES.match(result['type'])):
                    try:
                        result['url'] = images.get_serving_url(
                            blob_key,
                            secure_url=self.request.host_url \
                                .startswith('https')
                        )
                        result['thumbnail_url'] = result['url'] + \
                                                  THUMBNAIL_MODIFICATOR
                    except:  # Could not get an image serving url
                        pass
                if not 'url' in result:
                    result['url'] = self.request.host_url + \
                                    '/' + blob_key + '/' + urllib.quote(
                        result['name'].encode('utf-8'), '')
            results.append(result)
        deferred.defer(
            cleanup,
            blob_keys,
            _countdown=EXPIRATION_TIME
        )
        return results

    def options(self):
        pass

    def head(self):
        pass

    def get(self):
        self.redirect(WEBSITE)

    def post(self):
        if (self.request.get('_method') == 'DELETE'):
            return self.delete()
        result = {'files': self.handle_upload()}
        s = json.dumps(result, separators=(',', ':'))
        redirect = self.request.get('redirect')
        if redirect:
            return self.redirect(str(
                redirect.replace('%s', urllib.quote(s, ''), 1)
            ))
        if 'application/json' in self.request.headers.get('Accept'):
            self.response.headers['Content-Type'] = 'application/json'
        self.response.write(s)

    def delete(self):
        blobstore.delete(self.request.get('key') or '')


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, key, filename):
        if not blobstore.get(key):
            self.error(404)
        else:
            # Cache for the expiration time:
            self.response.headers['Cache-Control'] = \
                'public,max-age=%d' % EXPIRATION_TIME
            self.send_blob(key, save_as=filename)


app = webapp2.WSGIApplication(
    [
        ('/', UploadHandler),
        ('/([^/]+)/([^/]+)', DownloadHandler)
    ],
    debug=True
)
