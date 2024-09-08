from websockets.sync.client import connect
from moolticutepy import schemas
from moolticutepy.log import log
from pydantic import TypeAdapter
from threading import Thread
import queue
from typing import *


class MoolticuteException(Exception):
    pass


class MoolticuteTimeoutException(MoolticuteException):
    pass


class MoolticuteClient(Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True)

        self._params = dict()
        self._status = schemas.StatusEnum.Locked
        self._msg_in = queue.Queue()
        self._management = False

        self._ws = connect("ws://localhost:30035")
        self.start()

    def run(self):
        response_adapter = TypeAdapter(schemas.ResponseMessageType)
        while True:
            data = self._ws.recv()
            response = None

            try:
                response = response_adapter.validate_json(data)
            except:
                response = schemas.UnhandledResponse.model_validate_json(data)

            if isinstance(response, schemas.UnhandledResponse):
                if response.data is not None:
                    log.info(f"UnhandledResponse event received: {response}")
            elif isinstance(response, schemas.ParamChangedResponse):
                self._params[response.data.parameter] = response.data.value
            elif isinstance(response, schemas.StatusChangedResponse):
                self._status = response.data
            elif isinstance(response, schemas.FailedMemoryManagementResponse):
                self._management = False
            elif isinstance(response, schemas.MemoryManagementChange):
                self._management = response.data
            elif isinstance(response, schemas.ProgressDetailedResponse):
                log_message = response.data.progress_message
                if response.data.progress_message_args:
                    for idx, arg in enumerate(response.data.progress_message_args):
                        log_message = log_message.replace(f"%{idx+1}", arg)

                log.info(
                    f"{log_message}. {response.data.progress_current}/{response.data.progress_total}"
                )
            else:
                log.debug(f"Not implemented message {type(response)}: {response}")

            self._msg_in.put(response)

    def _wait_for_response(
        self,
        client_id: Optional[str] = None,
        msg_type: Optional[Type] = None,
        timeout: Optional[float] = None,
    ) -> Union[schemas.ResponseMessageType, schemas.UnhandledResponse]:
        if client_id is None and msg_type is None:
            raise ValueError("need to specify one of `client_id` or `msg_type`")

        while True:
            message = None

            try:
                message = self._msg_in.get(timeout=timeout)
            except queue.Empty:
                raise MoolticuteTimeoutException("timeout to read from mooltipass")

            match_client = client_id is None
            if client_id is not None and message.client_id == client_id:
                match_client = True

            match_type = msg_type is None
            if msg_type is not None:
                target_type = msg_type
                if get_origin(msg_type) is Union:
                    target_type = get_args(msg_type)

                if isinstance(message, target_type):
                    match_type = True

            if match_client and match_type:
                return message

    @property
    def is_unlocked(self):
        return self._status == schemas.StatusEnum.Unlocked

    @property
    def is_locked(self):
        return self._status == schemas.StatusEnum.Locked

    def wait_for_unlock(self, timeout=None):
        while self.is_locked:
            self._wait_for_response(
                msg_type=schemas.StatusChangedResponse, timeout=timeout
            )

    def _send(self, msg: schemas.BaseModel):
        self._ws.send(msg.model_dump_json())

    def _enter_memory_mgmnt(
        self, timeout=None
    ) -> Union[
        schemas.FailedMemoryManagementResponse, schemas.MemoryManagementDataResponse
    ]:
        msg = schemas.StartMemoryManagement()
        self._send(msg)

        response = self._wait_for_response(msg.client_id, timeout=timeout)
        if isinstance(response, schemas.FailedMemoryManagementResponse):
            return response

        response = self._wait_for_response(
            msg_type=schemas.MemoryManagementDataResponse
        )
        return response

    def _exit_memory_mgmnt(self):
        self._send(schemas.ExitMemoryManagement())

    def get_all_logins(
        self, timeout: Optional[float] = None
    ) -> List[schemas.MemoryManagementLoginNode]:
        response = self._enter_memory_mgmnt(timeout)
        if response.data.failed:
            raise MoolticuteException(
                f"Error entering memory management: {response.data.error_message}"
            )

        self._exit_memory_mgmnt()

        return response.data.login_nodes

    def get_password(
        self,
        service: str,
        fallback_service: Optional[str] = None,
        login: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        msg = schemas.AskPassword(
            data=schemas.AskPasswordData(
                service=service, fallback_service=fallback_service, login=login
            )
        )

        self._send(msg)

        response = self._wait_for_response(msg.client_id, timeout=timeout)

        if response.data.failed:
            raise MoolticuteException(
                f"Error getting credential: {response.data.error_message}"
            )
        return response

    def set_password(
        self,
        service: str,
        password: str,
        login: Optional[str] = None,
        description: Optional[str] = None,
        wait_confirmation: bool = False,
        timeout: Optional[float] = None,
    ) -> Optional[schemas.SetCredentialsResponse]:
        msg = schemas.SetCredential(
            data=schemas.SetCredentialData(
                service=service, login=login, description=description, password=password
            )
        )

        self._send(msg)

        if wait_confirmation:
            response = self._wait_for_response(client_id=msg.client_id, timeout=timeout)
            #TODO: Handle response on error?
            return response
        
        return None

        
