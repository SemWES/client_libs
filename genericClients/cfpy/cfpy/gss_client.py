"""Lightweight SOAP client to communicate with GSS"""
import os
import urllib2

from cfpy import SoapClient


class GssClient(SoapClient):
    """Lightweight GSS SOAP client

    Create by passing a WSDL URL:
        gss = GssClient(<wsdl>)
    """

    def __init__(self, wsdl_url):
        super(GssClient, self).__init__(wsdl_url)

    def get_resource_information(self, gss_ID, session_token):
        """Queries the resource information for a GSS ID."""
        return self.method_call('getResourceInformation',
                                [gss_ID, session_token])

    def list_files(self, gss_ID, session_token):
        """Lists contents of a folder defined by gss_ID."""
        return self.method_call('listFiles',
                                [gss_ID, session_token])

    def list_files_minimal(self, gss_ID, session_token):
        """Lists minimal contents of a folder defined by gss_ID.

        The minimal listing does not contain any request description objects.
        """
        return self.method_call('listFilesMinimal',
                                [gss_ID, session_token])

    def create_folder(self, gss_ID, session_token):
        """Creates a folder specified by gss_ID."""
        return self.method_call('createFolder',
                                [gss_ID, session_token])

    def delete_folder(self, gss_ID, session_token):
        """Deletes the folder specified by gss_ID."""
        return self.method_call('deleteFolder',
                                [gss_ID, session_token])

    def contains_file(self, gss_ID, session_token):
        """Returns true if the given GSS ID exists."""
        return self.method_call('containsFile',
                                [gss_ID, session_token])

    def get_direct_interaction_endpoint(self, gss_ID, session_token):
        """Returns the storage-solution end point the gss ID points to."""
        return self.method_call('getDirectInteractionEndpoint',
                                [gss_ID, session_token])

    def download_to_file(self, gss_ID, session_token, out_filename):
        """Downloads from a GSS ID to a file."""
        res_info = self.get_resource_information(gss_ID, session_token)
        read_desc = res_info.readDescription

        if not read_desc.supported:
            raise AttributeError('Read operation not allowed')

        headers = {h.key: h.value for h in read_desc.headers}

        request = urllib2.Request(url=read_desc.url, headers=headers)
        with open(out_filename, 'wb') as out_file:
            result = urllib2.urlopen(request)
            while True:
                buffer = result.read()
                if not buffer:
                    break
                out_file.write(buffer)

    def upload(self, gss_ID, session_token, in_filename):
        """Uploads from a file to a new, nonexisting GSS ID."""
        res_info = self.get_resource_information(gss_ID, session_token)
        create_desc = res_info.createDescription

        if not create_desc.supported:
            raise AttributeError('Create operation not allowed')

        return self._create_or_update(gss_ID, session_token, in_filename,
                                      res_info, create_desc)

    def update(self, gss_ID, session_token, in_filename):
        """Updates an existing GSS ID from a file."""
        res_info = self.get_resource_information(gss_ID, session_token)
        update_desc = res_info.updateDescription

        if not update_desc.supported:
            raise AttributeError('Update operation not allowed')

        return self._create_or_update(gss_ID, session_token, in_filename,
                                      res_info, update_desc)

    def _create_or_update(self, gss_ID, session_token, in_filename, res_info,
                          req_desc):
        """Utility function for general upload"""
        headers = {h.key: h.value for h in req_desc.headers}
        headers["Content-Length"] = "%d" % os.stat(in_filename).st_size

        with open(in_filename, "r") as in_file:
            request = urllib2.Request(url=req_desc.url, data=in_file,
                                      headers=headers)
            request.get_method = lambda: req_desc.httpMethod
            result = urllib2.urlopen(request)

        if res_info.queryForName:
            return result.info()["filename"]
        else:
            return gss_ID

    def delete(self, gss_ID, session_token):
        """Deletes a file or folder specified by gss_ID."""
        res_info = self.get_resource_information(gss_ID, session_token)
        delete_desc = res_info.deleteDescription

        if not delete_desc.supported:
            raise AttributeError('Delete operation not allowed')

        headers = {h.key: h.value for h in delete_desc.headers}

        request = urllib2.Request(url=delete_desc.url, headers=headers)
        request.get_method = lambda: delete_desc.httpMethod
        result = urllib2.urlopen(request)

        return result