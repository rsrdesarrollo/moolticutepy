from typing import *
from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4


## REQUESTS
######################


class BaseRequest(BaseModel):
    client_id: Optional[str] = Field(default_factory=lambda: uuid4().hex)


class GetBattery(BaseRequest):
    msg: Literal["get_battery"] = "get_battery"


class GetBleName(BaseRequest):
    msg: Literal["get_ble_name"] = "get_ble_name"


class GetUserCategories(BaseRequest):
    msg: Literal["get_user_categories"] = "get_user_categories"


class StartMemoryManagementData(BaseModel):
    want_data: bool = False
    want_fido: bool = False


class StartMemoryManagement(BaseRequest):
    msg: Literal["start_memorymgmt"] = "start_memorymgmt"
    data: StartMemoryManagementData = StartMemoryManagementData()


class ExitMemoryManagement(BaseRequest):
    msg: Literal["exit_memorymgmt"] = "exit_memorymgmt"


class AskPasswordData(BaseModel):
    login: Optional[str] = None
    service: Optional[str] = None
    fallback_service: Optional[str] = None


class AskPassword(BaseRequest):
    msg: Literal["ask_password"] = "ask_password"
    data: AskPasswordData


class SetCredentialData(BaseModel):
    description: Optional[str] = ""
    login: Optional[str] = None
    password: str
    service: str
    saveManualCredential: Literal[1] = 1 


class SetCredential(BaseRequest):
    msg: Literal["set_credential"] = "set_credential"
    data: SetCredentialData

class SetCredentialsData(BaseModel):
    address: List[int]
    category: int
    description: Optional[str] = ""
    favorite: Optional[int] = -1
    key_after_login: Optional[int] = 65535 
    key_after_pwd: Optional[int] = 65535
    login: str
    multiple_domains: Optional[str] = ""    # Coma list of tlds for example .com,.es
    password: Optional[str] = ""            # keep blank to keep current password
    pointed_to_child: List[int]
    service: str


class SetCredentials(BaseRequest):          # Used in management mode tu update multiple credentials. Allows to link credentials
    msg: Literal["set_credentials"] = "set_credentials"
    data: SetCredentialsData


## RESPONSES
######################


class BaseResponse(BaseModel):
    client_id: Optional[str] = None


class MemoryManagementLoginNodeChild(BaseModel):
    address: List[int]
    category: str
    date_created: str
    date_last_used: str
    description: str
    favorite: int
    key_after_login: str
    key_after_pwd: str
    login: str
    password_enc: List[int] = Field(..., exclude=True)
    pointed_to_child: List[int]
    pwd_blank_flag: str
    totp_code_size: Optional[str] = None
    totp_time_step: Optional[str] = None


class MemoryManagementLoginNode(BaseModel):
    childs: List[MemoryManagementLoginNodeChild]
    multiple_domains: str
    service: str


class MemoryManagementDataResponseData(BaseModel):
    data_nodes: List
    fido_nodes: List
    login_nodes: List[MemoryManagementLoginNode]
    notes_nodes: List
    failed: Optional[bool] = False


class MemoryManagementDataResponse(BaseResponse):
    msg: Literal["memorymgmt_data"]
    data: MemoryManagementDataResponseData


class FailedMemoryManagementResponseData(BaseModel):
    error_code: int
    error_message: str
    failed: bool


class FailedMemoryManagementResponse(BaseResponse):
    msg: Literal["failed_memorymgmt"]
    data: FailedMemoryManagementResponseData


class MemoryManagementChange(BaseResponse):
    msg: Literal["memorymgmt_changed"]
    data: bool


class AskPasswordResponseData(BaseModel):
    desc: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = Field(None, exclude=True)
    service: Optional[str] = None
    third: Optional[str] = None
    failed: Optional[bool] = False
    error_message: Optional[str] = None


class AskPasswordResponse(BaseResponse):
    msg: Literal["ask_password"]
    data: AskPasswordResponseData


class SetCredentialsResponseData(BaseModel):
    desc: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = Field(None, exclude=True)
    service: Optional[str] = None
    failed: Optional[bool] = False
    error_message: Optional[str] = None


class SetCredentialsResponse(BaseResponse):
    msg: Literal["set_credential"]
    data: SetCredentialsResponseData


class ParamChangedResponseData(BaseModel):
    parameter: str
    value: Union[str, int, bool, float]


class ParamChangedResponse(BaseResponse):
    msg: Literal["param_changed"]
    data: ParamChangedResponseData


class StatusEnum(str, Enum):
    Locked = "Locked"
    Unlocked = "Unlocked"


class StatusChangedResponse(BaseResponse):
    msg: Literal["status_changed"]
    data: StatusEnum


class ProgressDetailedResponseData(BaseModel):
    progress_current: int
    progress_message: str
    progress_message_args: Optional[List[str]] = None
    progress_total: int


class ProgressDetailedResponse(BaseResponse):
    msg: Literal["progress_detailed"]
    data: ProgressDetailedResponseData


class UnhandledResponse(BaseResponse):
    msg: str
    data: Optional[Union[str, bool, int, float, Dict[str, Any]]] = None


ResponseMessageType = Union[
    MemoryManagementDataResponse,
    AskPasswordResponse,
    SetCredentialsResponse,
    ParamChangedResponse,
    StatusChangedResponse,
    FailedMemoryManagementResponse,
    MemoryManagementChange,
    ProgressDetailedResponse,
]
