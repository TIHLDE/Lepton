import os

MAIL_HS = "hs@tihlde.org" if os.environ.get("PROD") else "test+hs@tihlde.org"
MAIL_ECONOMY = (
    "okonomi@tihlde.org" if os.environ.get("PROD") else "test+okonomi@tihlde.org"
)
MAIL_INDEX = "index@tihlde.org" if os.environ.get("PROD") else "test+index@tihlde.org"
MAIL_NOK_LEADER = (
    "naeringslivsminister@tihlde.org"
    if os.environ.get("PROD")
    else "test+naeringslivminister@tihlde.org"
)
MAIL_NOK = "nok@tihlde.org" if os.environ.get("PROD") else "test+nok@tihlde.org"
MAIL_NOK_ADS = (
    "stillingsannonser@tihlde.org"
    if os.environ.get("PROD")
    else "test+stillingsannonser@tihlde.org"
)

SLACK_BEDPRES_OG_KURS_CHANNEL_ID = "C01DCSJ8X2Q"
SLACK_ARRANGEMENTER_CHANNEL_ID = "C01LFEFJFV3"

MAX_GALLERY_SIZE = 50

# TODO: Create api-urls as constants which then can be used in for example tests and urls.py files
