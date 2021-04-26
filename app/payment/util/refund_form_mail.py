import base64
import functools
import io
import operator
import os
import tempfile
from datetime import datetime

from django.core.mail import EmailMultiAlternatives

import pyheif
from fpdf import FPDF
from pdf2image import convert_from_path
from PIL import Image


class UnsupportedFileException(Exception):
    pass


field_title_map = {
    "date": "Dato:",
    "committee": "Gruppe/Utvalg/Person:",
    "name": "Navn:",
    "accountNumber": "Kontonummer:",
    "amount": "Beløp:",
    "occasion": "Anledning/arrangement:",
    "comment": "Kommentar:",
}

mailto = "okonomi@tihlde.org" if os.environ.get("PROD") else "test@tihlde.org"


def data_is_valid(data):
    fields = [
        "images",
        "date",
        "amount",
        "name",
        "accountNumber",
        "mailfrom",
    ]
    return [field for field in fields if field not in data or not len(data[field])]


class PDF(FPDF):
    def header(self):
        self.image("app/static/logo/TIHLDE_LOGO_BLÅ.png", 10, 10, 33)
        self.set_font("Arial", "B", 15)
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Side {str(self.page_no())}/{{nb}}", 0, 0, "C")


def image_to_byte_array(image: Image, fmt=None):
    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format=fmt if fmt is not None else image.format)
    img_byte_array = img_byte_array.getvalue()
    return img_byte_array


def create_image_file(image):
    """
    Take an image in BASE64 format and return a NamedTemporaryFile containing the image.
    Will handle PNG, JPEG and GIF without any changes, as FPDF will handle those files
    without problem. For PDFs we use pdf2image to convert each page to an image. For HEIC
    pictures we use pyheif to convert it to a jpeg.
    """

    if "image/" not in image and "application/pdf" not in image:
        raise UnsupportedFileException(image[:30])
    parts = image.split(";base64,")
    decoded = base64.b64decode(parts[1])
    suffix = "pdf" if "application/pdf" in image else parts[0].split("image/")[1]
    suffix = suffix.lower()
    file = tempfile.NamedTemporaryFile(suffix=f".{suffix}")
    file.write(decoded)
    file.flush()

    """
    FPDF does not support pdf files as input, therefore convert file:pdf to array[image:jpg]
    """
    if suffix == "pdf":
        files = []
        pil_images = convert_from_path(file.name, fmt="jpeg")
        for img in pil_images:
            file = tempfile.NamedTemporaryFile(suffix=f".{suffix}")
            file.write(image_to_byte_array(img))
            files.append({"file": file, "type": "jpeg"})
            file.flush()
        return files

    """
    FPDF does not support heic files as input, therefore we covert a image:heic image:jpg
    """
    if suffix == "heic":
        fmt = "JPEG"
        heif_file = pyheif.read(file.name)
        img = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        file = tempfile.NamedTemporaryFile(suffix=f".{fmt}")
        file.write(image_to_byte_array(img, fmt))
        file.flush()
        return [{"file": file, "type": fmt}]

    return [{"file": file, "type": suffix.upper()}]


def format_image_data(data):
    images = data.pop("images", None)

    data["images"] = functools.reduce(
        operator.iconcat, [create_image_file(img) for img in images], []
    )

    return data


def create_pdf(data):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    images = data.pop("images")

    pdf.cell(0, 14, "Refusjonsskjema", ln=1)

    pdf.set_font("Arial", "", 12)
    for key in field_title_map.keys():
        pdf.set_font("", "B")
        pdf.cell(90, 8, txt=field_title_map[key])
        pdf.set_font("", "")
        if key == "date":
            pdf.multi_cell(
                0,
                8,
                txt=datetime.strptime(data["date"], "%Y-%m-%d").strftime("%d %b %Y"),
            )
        else:
            pdf.multi_cell(0, 8, txt=data[key])

    pdf.set_font("", "B")
    pdf.cell(0, 5, txt="", ln=1)
    pdf.cell(0, 20, txt="Vedlegg:", ln=1)
    max_img_width = 190
    max_img_height = 220
    for image in images:
        img = Image.open(image["file"].name)
        width, height = img.size
        img.close()

        size = (
            {"w": max_img_width}
            if width / height >= max_img_width / max_img_height
            else {"h": max_img_height}
        )

        pdf.image(image["file"].name, **size, type=image["type"])
        image["file"].close()
    return pdf.output(dest="S")


def format_mail(data):
    text = ""
    text += (
        f'Dato: {datetime.strptime(data["date"], "%Y-%m-%d").strftime("%d %b %Y")}\n'
    )
    text += f'Gruppe/Utvalg/Person: {data["committee"]}\n'
    text += f'Navn: {data["name"]}\n'
    text += f'Kontonummer: {data["accountNumber"]}\n'
    text += f'Beløp: {data["amount"]}\n'
    text += f'Anledning/arrangement: {data["occasion"]}\n'
    text += f'Kommentar: {data["comment"]}\n\n'
    text += "Refusjonsskjema er generert og vedlagt. Ved spørsmål ta kontakt med okonomi@tihlde.org!"
    return text


def send_refund_mail(data, file):
    subject, text, from_email, to = (
        f'Refusjonsskjema - {data["name"]}',
        format_mail(data),
        data["mailfrom"],
        [mailto, data["mailfrom"]],
    )
    msg = EmailMultiAlternatives(subject, text, from_email, to)
    msg.attach(f'{data["date"]}_Attachment_{data["name"]}.pdf', file, "application/pdf")
    msg.send()
