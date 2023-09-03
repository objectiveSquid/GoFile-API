from requests import RequestException
from typing import Callable, Any


class InvalidTokenException(ValueError):
    ...


class InvalidFolderException(ValueError):
    ...


class RateLimitException(Exception):
    ...


class CannotReachAPIException(Exception):
    ...


class InvalidResponseException(Exception):
    ...


class GetServerException(Exception):
    ...


class UploadFileException(Exception):
    ...


class GetContentException(Exception):
    ...


class CreateAccountException(Exception):
    ...


class CreateFolderException(Exception):
    ...


class GetAccountDetailsException(Exception):
    ...


class CopyContentException(Exception):
    ...


class SetOptionException(Exception):
    ...
