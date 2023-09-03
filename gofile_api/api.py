from requests import RequestException, post, put, get
from typing import Iterable, NoReturn, Literal
from os.path import split as file_path_split
from random import choices
from exceptions import (
    InvalidResponseException,
    CannotReachAPIException,
    InvalidFolderException,
    InvalidTokenException,
    RateLimitException,
)
from exceptions import (
    GetAccountDetailsException,
    CreateAccountException,
    CreateFolderException,
    CopyContentException,
    UploadFileException,
    GetContentException,
    GetServerException,
    SetOptionException,
)


class GoFileSession:
    """Class for communicating with the GoFile API."""

    def __init__(
        self, max_retries: int = 5, raw_output: bool = False, token: str | None = None
    ) -> None:
        self.__max_retries = max_retries
        self.__retry_count = 0
        self.__raw = raw_output
        if token == None:
            self.__token = self.create_account()
        self.refresh_account_info()

    def get_server(self, raw: bool | None = None) -> str | dict:
        """raw: Return raw json."""
        if raw == None:
            raw = self.__raw
        try:
            response = get("https://api.gofile.io/getServer")
        except RequestException:
            self.__next_retry("getting available server")
            return self.get_server(raw)
        self.__reset_retry_count()
        response_json: dict = response.json()
        status = response_json.get("status")
        match response.status_code:
            case 200:
                if status == "ok":
                    if raw:
                        return response_json
                    return response_json["data"]["server"]
                elif status == "noServer":
                    raise GetServerException(
                        "no server was available, the gofile api is probably down, or under heavy load"
                    )
                else:
                    raise GetServerException(
                        f"error while getting server, status: {status}"
                    )
            case _:
                raise GetServerException(
                    f"error while getting server, status: {status}\nresponse code: {response.status_code}"
                )

    def upload_file(
        self,
        file_path: str,
        raw: bool | None = None,
        parent_folder_id: str | None = None,
        parent_folder_name: str | None = None,
        parent_folder_public: bool = True,
        parent_folder_password: str | None = None,
        expiration_timestamp: float | int | None = None,
        parent_folder_description: str | None = None,
        parent_folder_tags: Iterable[str] | None = None,
    ) -> str | dict:
        """file_path: The path to the file that will be uploaded.\n
        parent_folder_id: The parent folder ID. If None is given, a new folder is created to recieve the file.\n
        raw: Return raw json.\n
        parent_folder_name: The parent folder name. If None is given, a random name is generated.\n
        parent_folder_public: Should the parent folder be public for all users to see. Default is True.\n
        parent_folder_password: The password for the parent folder.\n
        expiration_timestamp: When the parent folder should expire, in unix-time.\n
        description: Description of the parent folder.\n
        tags: The tags for the parent folder.\n
        """
        if raw == None:
            raw = self.__raw
        if parent_folder_id == None:
            parent_folder_id = self.create_folder(
                folder_name=parent_folder_name,
                parent_folder_id=self.__root_folder,
                public=parent_folder_public,
                folder_password=parent_folder_password,
                expiration_timestamp=expiration_timestamp,
                description=parent_folder_description,
                tags=parent_folder_tags,
            )
            parent_folder_id = self.__root_folder
        payload = {"token": self.__token}
        payload["folderId"] = parent_folder_id
        headers = {"Content-Type": "application/json"}
        with open(file_path, "r") as file_opened:
            try:
                response = post(
                    f"https://{self.get_server()}.gofile.io/uploadFile",
                    json=payload,
                    headers=headers,
                    files={"file": file_opened},
                )
            except RequestException:
                self.__next_retry(f"uploading file ({file_path}) to {parent_folder_id}")
                return self.upload_file(
                    file_path=file_path,
                    raw=raw,
                    parent_folder_id=parent_folder_id,
                    parent_folder_name=parent_folder_name,
                    parent_folder_public=parent_folder_public,
                    parent_folder_password=parent_folder_password,
                    expiration_timestamp=expiration_timestamp,
                    parent_folder_description=parent_folder_description,
                    parent_folder_tags=parent_folder_tags,
                )
        self.__reset_retry_count()
        response_json: dict = response.json()
        status = response_json.get("status")
        match response.status_code:
            case 200:
                if status == "ok":
                    self.set_option(parent_folder_id, "public", parent_folder_public)
                    if parent_folder_password != None:
                        self.set_option(
                            parent_folder_id, "password", parent_folder_password
                        )
                    if expiration_timestamp != None:
                        self.set_option(
                            parent_folder_id, "expire", float(expiration_timestamp)
                        )
                    if parent_folder_tags != None:
                        self.set_option(parent_folder_id, "tags", parent_folder_tags)
                    if parent_folder_description != None:
                        self.set_option(
                            parent_folder_id, "description", parent_folder_description
                        )
                    if raw:
                        return response_json
                    return response_json["data"]["downloadPage"]
                else:
                    raise UploadFileException(
                        f"error while uploading file, status: {status}"
                    )
            case 401 | 403:
                raise InvalidTokenException(
                    "invalid token, maybe this function requires a gofile premium subscription?"
                )
            case _:
                raise UploadFileException(
                    f"error while uploading file, status: {status}\nresponse code: {response.status_code}"
                )

    def get_content(
        self, content_id: str, raw: bool | None = None
    ) -> list[str] | bytes | dict:
        """content_id: Content ID to get the contents of.\n
        raw: Return raw json."""
        if raw == None:
            raw = self.__raw
        params = {"token": self.__token, "contentId": content_id}
        headers = {"Content-Type": "application/json"}
        try:
            response = get(
                "https://api.gofile.io/getContent", params=params, headers=headers
            )
        except RequestException:
            self.__next_retry("getting contents of: " + content_id)
            return self.get_content(content_id=content_id, raw=raw)
        self.__reset_retry_count()
        response_json: dict = response.json()
        status = response_json.get("status")
        match response.status_code:
            case 200:
                if status == "ok":
                    if raw:
                        return response_json
                    data = response_json["data"]
                    childs = data["childs"]
                    if len(childs) != 1:
                        return childs
                    return get(data["contents"][childs[0]]["directLink"]).content
                else:
                    raise GetContentException(
                        f"error while getting content(s) of {content_id}\nstatus: {status}"
                    )
            case 401 | 403:
                raise InvalidTokenException(
                    "invalid token, maybe this function requires a gofile premium subscription?"
                )
            case _:
                raise GetContentException(
                    f"error while getting content(s) of {content_id}\nresponse code: {response.status_code}"
                )

    def create_account(self, raw: bool | None = None) -> str:
        """raw: Return raw json."""
        if raw == None:
            raw = self.__raw
        try:
            response = get("https://api.gofile.io/createAccount")
        except RequestException:
            self.__next_retry("creating account")
            return self.create_account(raw)
        self.__reset_retry_count()
        response_json: dict = response.json()
        status = response_json.get("status")
        match response.status_code:
            case 200:
                if status == "ok":
                    if raw:
                        return response_json
                    return response_json["data"]["token"]
                else:
                    raise CreateAccountException(
                        f"error while creating account, status: {status}"
                    )
            case 429:
                raise RateLimitException(
                    "rate limited (too many requests) while creating new account"
                )
            case _:
                raise CreateAccountException(
                    f"error while creating account, response code: {response.status_code}\nstatus: {status}"
                )

    def create_folder(
        self,
        raw: bool | None = None,
        folder_name: str | None = None,
        parent_folder_id: str | None = None,
        public: bool = True,
        folder_password: str | None = None,
        expiration_timestamp: float | int | None = None,
        description: str | None = None,
        tags: Iterable[str] | None = None,
    ) -> str | dict:
        """folder_name: The folder name. If None is given, a random name is generated.\n
        parent_folder_id: The parent folder ID. If None is given, the root folder will be used.\n
        public: Should the folder be public for all users to see. Default is True.\n
        folder_password: The password for the folder.\n
        expiration_timestamp: When the folder should expire, in unix-time.\n
        description: Description of the folder.\n
        tags: The tags for the folder."""
        if raw == None:
            raw = self.__raw
        if parent_folder_id == None:
            parent_folder_id = self.__root_folder
        if folder_name == None:
            folder_name = "".join(choices("abcdefghijklmnopqrstuvwxyz1234567890", k=5))
        payload = {
            "token": self.__token,
            "folderName": folder_name,
            "parentFolderId": parent_folder_id,
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = put(
                "https://api.gofile.io/createFolder", json=payload, headers=headers
            )
        except RequestException:
            self.__next_retry(
                f"creating folder {folder_name}\nparent folder id: {parent_folder_id}"
            )
            return self.create_folder(
                raw=raw,
                folder_name=folder_name,
                parent_folder_id=parent_folder_id,
                public=public,
                folder_password=folder_password,
                expiration_timestamp=expiration_timestamp,
                description=description,
                tags=tags,
            )
        self.__reset_retry_count()
        response_json: dict = response.json()
        status = response_json.get("status")
        match response.status_code:
            case 200:
                content_id = response_json["data"]["id"]
                if status == "ok":
                    self.set_option(content_id, "public", public)
                    if folder_password != None:
                        self.set_option(content_id, "password", folder_password)
                    if expiration_timestamp != None:
                        self.set_option(
                            content_id, "expire", float(expiration_timestamp)
                        )
                    if tags != None:
                        self.set_option(content_id, "tags", ",".join(tags))
                    if description != None:
                        self.set_option(content_id, "description", description)
                    if raw:
                        return response_json
                    return content_id
                else:
                    raise CreateFolderException(
                        f"error while creating folder {folder_name}\nparent folder id: {parent_folder_id}"
                    )
            case 401 | 403:
                raise InvalidTokenException(
                    "invalid token, maybe this function requires a gofile premium subscription?"
                )
            case _:
                raise CreateFolderException(
                    f"error while creating folder {folder_name}\nparent folder id: {parent_folder_id}\nresponse code: {response.status_code}"
                )

    def get_account_details(self, raw: bool | None = None) -> dict:
        """raw: return raw json"""
        if raw == None:
            raw = self.__raw
        params = {"token": self.__token}
        headers = {"Content-Type": "application/json"}
        try:
            response = get(
                "https://api.gofile.io/getAccountDetails",
                params=params,
                headers=headers,
            )
        except RequestException:
            self.__next_retry(f"getting account details for token: {params['token']}")
            return self.get_account_details(raw=raw)
        self.__reset_retry_count()
        response_json: dict = response.json()
        status = response_json.get("status")
        match response.status_code:
            case 200:
                if status == "ok":
                    if raw:
                        return response_json
                    return response_json["data"]
                else:
                    raise GetAccountDetailsException(
                        f"error while getting account details for token: {params['token']}\nstatus: {status}"
                    )
            case 401 | 403:
                raise InvalidTokenException(
                    "invalid token, maybe this function requires a gofile premium subscription?"
                )
            case _:
                raise GetAccountDetailsException(
                    f"error while getting account details for token: {params['token']}\nstatus: {status}\nresponse code: {response.status_code}"
                )

    def copy_content(
        self, sources: Iterable[str], destination: str, raw: bool | None = None
    ) -> None | dict:
        """sources: Iterable of source content IDs\n
        destination: Content ID of destination folder\n
        raw: Return raw json"""
        if raw == None:
            raw = self.__raw
        sources_string = ",".join(sources)
        payload = {
            "token": self.__token,
            "contentsId": sources_string,
            "folderIdDest": destination,
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = put(
                "https://api.gofile.io/copyContent", json=payload, headers=headers
            )
        except RequestException:
            self.__next_retry(f"copying content from {sources_string} to {destination}")
            return self.copy_content(sources=sources, destination=destination, raw=raw)
        self.__reset_retry_count()
        response_json: dict = response.json()
        status = response_json.get("status")
        match response.status_code:
            case 200:
                if status == "ok":
                    if raw:
                        return response_json
                    return
                else:
                    raise CopyContentException(
                        f"error while copying content from {sources_string} to {destination}\nstatus: {status}"
                    )
            case 401 | 403:
                raise InvalidTokenException(
                    "invalid token, maybe this function requires a gofile premium subscription?"
                )
            case _:
                raise CopyContentException(
                    f"error while copying content from {sources_string} to {destination}\nstatus: {status}\nresponse code: {response.status_code}"
                )

    def set_option(
        self,
        content_id: str,
        option_type: Literal[
            "public", "password", "description", "expire", "tags", "directLink"
        ],
        value: bool | str | float | int | Iterable[str],
        raw: bool | None = None,
    ) -> None:
        """If option_type is "public", value must be a `bool`, and the content_id must be a folder.\n
        If option_type is "password", value must be a `str`, and the content_id must be a folder.\n
        If option_type is "description", value must be a `str`, and the content_id must be a folder.\n
        If option_type is "expire", value must be a `float` or an `int`, and the content_id must be a folder.\n
        If option_type is "tags", value must be an `Iterable[str]`, and the content_id must be a folder.\n
        If option_type is "directLink", value must be a `bool`, and the content_id must be a file.\n

        raw: Return raw json
        """
        if raw == None:
            raw = self.__raw
        if option_type in ("public", "directLink"):
            if value:
                value = "true"
            else:
                value = "false"
        if option_type == "tags":
            value = ",".join(value)
        payload = {
            "token": self.__token,
            "contentId": content_id,
            "option": option_type,
            "value": value,
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = put(
                "https://api.gofile.io/setOption", json=payload, headers=headers
            )
        except RequestException:
            self.__next_retry(
                f"setting option for content id/response status: {content_id}"
            )
            return self.set_option(
                content_id=content_id, option_type=option_type, value=value, raw=raw
            )
        self.__reset_retry_count()
        response_json: dict = response.json()
        status = response_json.get("status")
        match response.status_code:
            case 200:
                if status == "ok":
                    if raw:
                        return response_json
                    return
                else:
                    raise SetOptionException(
                        f"error while setting option for content id: {content_id}\nstatus: {status}"
                    )
            case 401 | 403:
                raise InvalidTokenException(
                    "invalid token, maybe this function requires a gofile premium subscription?"
                )
            case _:
                raise SetOptionException(
                    f"error while setting option for content id: {content_id}\nstatus: {status}\nstatus code: {response.status_code}"
                )

    def set_token(self, new_token: str) -> None:
        self.__token = new_token
        self.refresh_account_info()

    def reset_account(self) -> None:
        self.__token = self.create_account()
        self.refresh_account_info()

    def refresh_account_info(self) -> None:
        account_details = self.get_account_details()
        self.__root_folder: str = account_details["rootFolder"]
        self.__tier: str = account_details["tier"]

    def __reset_retry_count(self) -> None:
        self.__retry_count = 0

    def __increase_retry_count(self, amount: int = 1) -> None:
        self.__retry_count += amount

    def __next_retry(self, while_doing: str | None = None) -> None:
        if self.__retry_count == self.__max_retries:
            self.__reset_retry_count()
            self.__raise_max_retries(while_doing)
        self.__increase_retry_count()

    @staticmethod
    def __raise_max_retries(while_doing: str | None = None) -> NoReturn:
        if while_doing == None:
            raise TimeoutError("max retries hit")
        raise TimeoutError("max retries hit while " + while_doing)

    @property
    def max_retries(self) -> int:
        return self.__max_retries

    @property
    def token(self) -> str:
        return self.__token

    @property
    def root_folder(self) -> str:
        return self.__root_folder

    @property
    def raw(self) -> bool:
        return self.__raw

    @property
    def tier(self) -> str:
        return self.__tier

    @property
    def is_guest(self) -> bool:
        return self.__tier == "guest"

    @property
    def is_standard(self) -> bool:
        return self.__tier == "standard"

    @property
    def is_premium(self) -> bool:
        return self.__tier == "premium"


s = GoFileSession()
fid = s.create_folder(folder_name="TestFolder")
print(fid)
print(s.upload_file("C:\\Users\\magnu\\Desktop\\test.txt", parent_folder_id=fid))
