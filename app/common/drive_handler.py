import logging
import os
import uuid

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import URLValidator

import owncloud
import requests

logger = logging.getLogger(__name__)


def login():
    oc = owncloud.Client(os.environ.get("DRIVE_URL"))
    oc.login(os.environ.get("DRIVE_USERNAME"), os.environ.get("DRIVE_PASSWORD"))
    return oc


def make_directory(dirname):
    oc = login()

    try:
        oc.mkdir(dirname)
    except Exception as e:
        logger.error(e.message)
    finally:
        oc.logout()


def upload_bytes(to_dir, file_data, file_extension):
    """
    Uploads raw bytes or chunks <file_data> to path /<to_dir>/<random uuid4><file_extension> in cloud and returns shared link.
    """
    if "." not in file_extension:
        file_extension = "." + file_extension

    file_name = uuid.uuid4()
    cloud_file_path = f"{ to_dir }/{ file_name }{ file_extension }"
    local_file_path = f"app/util/temp{ file_extension }"

    with open(local_file_path, "wb") as f:
        if type(file_data) == InMemoryUploadedFile:
            for chunk in file_data.chunks():
                f.write(chunk)
        else:
            f.write(file_data)

        f.close()

    oc = login()
    failed = False
    try:
        # During testing, the function oc.share_file_with_link(c) started crashing when returning the share_info object.
        # Since the function consistantly does what it is supposed to (share the file) we catch the exception.
        oc.put_file(cloud_file_path, local_file_path)
        share_info = oc.share_file_with_link(cloud_file_path)
    except Exception:
        # This workaround uses a function that does not have the same issue as oc.share_file_with_link(c).
        # It gets all shares for the newly uploaded file and returns the first element, which in practice is the same as above.
        share_list = oc.get_shares(cloud_file_path)
        if share_list:
            share_info = share_list[0]
        else:
            failed = True
    finally:
        oc.logout()
        os.remove(local_file_path)

    if failed:
        raise ValueError(
            "Unable to get shared link from cloud. (Most likely because of a bug in the pyocclient package.)"
        )

    return f"{ share_info.get_link() }/preview#file{ file_extension }"


def is_url(data):
    validator = URLValidator()
    try:
        validator(data)
        return True
    except ValidationError:
        return False


def get_cloud_link_from_url(file_url, file_extension, to_dir):
    """
    Takes the file url and file extension and uploads file to cloud.
    """
    if not is_url(file_url):
        raise ValueError("Given data has to be a url to a file.")

    file_data = requests.get(file_url).content

    if type(file_data) != bytes:
        file_data = bytes(file_data, "utf-8")

    return upload_bytes(to_dir, file_data, file_extension)


def get_cloud_links_from_files(request, to_dir):
    """
    Uploads the files in request.FILES to <to_dir> and returns dict of cloud links with original filenames as keys.
    """

    replaced_files = {}

    for file in request.FILES:
        _, file_extension = os.path.splitext(file.name)
        replaced_files[file.name] = upload_bytes(to_dir, file, file_extension)

    return replaced_files


def get_cloud_link_from_single_file(request, to_dir):
    """
    Uploads the file in request.FILES to <to_dir> and returns the cloud link.
    """

    if len(request.FILES) > 1:
        raise ValueError("This function can only handle a single uploaded file.")

    key = list(request.FILES.keys())[0]
    file = request.FILES[key]

    _, file_extension = os.path.splitext(file.name)

    return upload_bytes(to_dir, file, file_extension)


def upload_and_replace_image_with_cloud_link(request, to_dir):
    """
    Takes request, and cloud directory. Uploads file and updates request.data["image"] with cloud url.
    """

    image = request.data.get("image", None)
    image_extension = request.data.get("image_extension", None)

    try:
        if image and image_extension:
            request.data["image"] = get_cloud_link_from_url(
                image, image_extension, to_dir
            )
        elif request.FILES:
            request.data["image"] = get_cloud_link_from_single_file(request, to_dir)
    except ValueError as e:
        logger.error(e.message)


def upload_and_replace_url_with_cloud_link(request, to_dir):
    """
    Takes request, and cloud directory. Uploads file and updates request.data["url"] with cloud url.
    """

    url = request.data.get("url", None)
    file_extension = request.data.get("file_extension", None)

    try:
        if url and file_extension:
            request.data["url"] = get_cloud_link_from_url(url, file_extension, to_dir)
        elif request.FILES:
            request.data["url"] = get_cloud_link_from_single_file(request, to_dir)
    except ValueError as e:
        logger.error(e.message)
