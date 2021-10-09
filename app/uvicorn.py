from uvicorn.workers import UvicornWorker as DefaultUvicornWorker

class UvicornWorker(DefaultUvicornWorker):
    """ Custom UvicornWorker-class used to turn of lifespan as it isn't supported by Django """
    CONFIG_KWARGS = {"lifespan": "off"}
