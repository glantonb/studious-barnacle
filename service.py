# -*- coding: utf-8 -*-
"""
This is spike-code for generating QR codes

The intent is for this to be generated on-request by the Comms System. This code might be re-used
"""
import io
import os

import qrcode
import base64

from typing import Dict

from qrcode.image.pil import PilImage
import PIL.Image


def generate_target_uri(event: Dict[str, str]) -> str:
    """
    Generate a URI
    :param event:
    :return:
    """
    user_id = event['user_id']
    postcode = event['postcode']
    campaign = event['campaign']
    LANDING_URL = os.environ.get('LANDING_URI') # https://d2lhzte9uh4t98.cloudfront.net/ for 'PR'

    return f"{LANDING_URL}?id={user_id}&campaign={campaign}&postcode={postcode}"


def generate_qr(uri) -> PilImage:
    qr_code_builder = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_code_builder.add_data(uri)
    qr_code_builder.make(fit=True)

    return qr_code_builder.make_image(fill_color="black", back_color="white").get_image()


def build_return(image: PilImage):
    byte_arr = io.BytesIO()

    image.save(byte_arr, format='PNG')

    return {
        'headers': { "Content-Type": "image/png" },
        'statusCode': 200,
        'body': base64.b64encode(byte_arr.getvalue()).decode('utf-8'),
        'isBase64Encoded': True
    }


def handler(event=None, _=None):
    """
    I'm the stand-in for a real AWS event handler.

    I am successful when I extract a user_id, postcode and campaign id from the event ID I'm passed in and then
    return a base-64 encoded PNG image. I get the URL for our landing page from an Env Variable (so that's a constant
    across Lambda invocations within a single deployment. This is because we don't want to have our calling contexts
    polluted with know about that. If the URI changes, it's probably has the 'universal' nature, but matters most here.

    That PNG image is the encoding of a QR code which will point our Players to something like:
    https://www.postcodelottery.co.uk/qr-landing/?id={uuid}&campaign={campaign:str[10]}&postcde={postcode:str}
    :return:
    """
    uri = generate_target_uri(event)

    image = generate_qr(uri)

    return build_return(image)
