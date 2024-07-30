from rest_framework import status
from rest_framework.exceptions import APIException


class APIPaidEventCantBeChangedToFreeEventException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Arrangementet er et betalt arrangement med påmeldte deltagere, og kan ikke endres til et gratis arrangement"


class APIEventCantBeChangedToPaidEventException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Arrangementet er et gratis arrangement med påmeldte deltagere, og kan ikke endres til et betalt arrangement"


class APIUserAlreadyAttendedEvent(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Brukeren har allerede ankommet"


class APIEventSignOffDeadlineHasPassed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Du kan ikke melde deg av etter avmeldingsfristen"


class APIUnansweredFormException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        "Du har ubesvarte evalueringsskjemaer som må besvares før du kan melde deg på"
    )


class APIHasStrikeException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Kan ikke melde deg på fordi du har en eller flere prikker"


class APIEventIsFullException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Du kan ikke flytte opp en fra ventelisten når arrangementet er fullt. Flytt en bruker ned først."


class EventSignOffDeadlineHasPassed(ValueError):
    pass


class StrikeError(ValueError):
    pass


class UnansweredFormError(ValueError):
    pass


class EventIsFullError(ValueError):
    pass


class RefundFailedError(ValueError):
    pass


class FeideError(ValueError):
    def __init__(
        self,
        message="Det skjedde en feil under registrering av din bruker ved hjelp av Feide.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.status_code = status_code


class FeideTokenNotFoundError(FeideError):
    def __init__(
        self,
        message="Fikk ikke tak i Feide token for din bruker. Prøv igjen eller registrer deg manuelt.",
    ):
        self.message = message
        super().__init__(self.message, status_code=status.HTTP_404_NOT_FOUND)


class FeideUserInfoNotFoundError(FeideError):
    def __init__(
        self,
        message="Fikk ikke tak i brukerinformasjon om deg fra Feide. Prøv igjen eller registrer deg manuelt.",
    ):
        self.message = message
        super().__init__(self.message, status_code=status.HTTP_404_NOT_FOUND)


class FeideUsernameNotFoundError(FeideError):
    def __init__(
        self,
        message="Fikk ikke tak i brukernavn fra Feide. Prøv igjen eller registrer deg manuelt.",
    ):
        self.message = message
        super().__init__(self.message, status_code=status.HTTP_404_NOT_FOUND)


class FeideUserGroupsNotFoundError(FeideError):
    def __init__(
        self,
        message="Fikk ikke tak i dine gruppetilhørigheter fra Feide. Prøv igjen eller registrer deg manuelt.",
    ):
        self.message = message
        super().__init__(self.message, status_code=status.HTTP_404_NOT_FOUND)


class FeideGetTokenError(FeideError):
    def __init__(
        self,
        message="Fikk ikke tilgang til Feide sitt API for å hente ut din token. Prøv igjen eller registrer deg manuelt.",
    ):
        self.message = message
        super().__init__(
            self.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class FeideUsedUserCode(FeideError):
    def __init__(
        self,
        message="Feide innloggings kode har allerede blitt brukt. Prøv å registrere deg på nytt.",
    ):
        self.message = message
        super().__init__(self.message, status_code=status.HTTP_409_CONFLICT)


class FeideGetUserInfoError(FeideError):
    def __init__(
        self,
        message="Fikk ikke tilgang til Feide sitt API for å hente ut din brukerinfo. Prøv igjen eller registrer deg manuelt.",
    ):
        self.message = message
        super().__init__(
            self.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class FeideGetUserGroupsError(FeideError):
    def __init__(
        self,
        message="Fikk ikke tilgang til Feide sitt API for å hente ut dine utdanninger. Prøv igjen eller registrer deg manuelt.",
    ):
        self.message = message
        super().__init__(
            self.message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class FeideParseGroupsError(FeideError):
    def __init__(
        self,
        message="Vi fant ingen utdanningen du tilhører som er en del av TIHLDE. Hvis du mener dette er feil så kan du opprette en bruker manuelt og sende mail til hs@tihlde.org for å den godkjent.",
    ):
        self.message = message
        super().__init__(self.message, status_code=status.HTTP_404_NOT_FOUND)


class FeideUserExistsError(FeideError):
    def __init__(self, message="Det finnes allerede en bruker med dette brukernavnet."):
        self.message = message
        super().__init__(self.message, status_code=status.HTTP_409_CONFLICT)
