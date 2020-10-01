import os

import owncloud


def login():
    oc = owncloud.Client(os.environ.get("DRIVE_URL"))
    oc.login(os.environ.get("DRIVE_USERNAME"), os.environ.get("DRIVE_PASSWORD"))
    return oc


def make_directory(dirname):
    oc = login()
    try:
        oc.mkdir(dirname)
        oc.logout()
    except Exception as e:
        oc.logout()
        print(e)


def upload_file(dirname, uploadedFilename, file):
    oc = login()
    oc.put_file("%s/%s" % (dirname, uploadedFilename), file)
    link_info = oc.share_file_with_link("%s/%s" % (dirname, uploadedFilename))
    oc.logout()
    return link_info.get_link()
