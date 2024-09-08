import getpass
import logging
from functools import update_wrapper
from typing import *

import click
import sys

import moolticutepy
from moolticutepy.log import log

CLIENT_CTX = "CLIENT_CTX"


def pass_client(fn: Callable[[moolticutepy.MoolticuteClient, Any, Any], Any]):
    @click.pass_context
    def _wrapp(ctx: click.Context, *args, **kwargs):
        client = ctx.obj[CLIENT_CTX]
        return ctx.invoke(fn, client, *args, **kwargs)

    return update_wrapper(_wrapp, fn)


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def main(ctx: click.Context, debug: bool):
    if debug:
        log.setLevel(logging.DEBUG)

    ctx.ensure_object(dict)

    mooltipass = moolticutepy.MoolticuteClient()

    try:
        mooltipass.wait_for_unlock(timeout=1)
    except moolticutepy.MoolticuteTimeoutException:
        if mooltipass.is_locked():
            print("Waiting for mooltipass to unlock .... ", end="")
            mooltipass.wait_for_unlock()
            print("[OK]")

    ctx.obj[CLIENT_CTX] = mooltipass


@main.command()
@pass_client
def list_logins(moolticuted: moolticutepy.MoolticuteClient):
    try:
        print("Entering management mode. Please approve prompt on device ...", end="")
        data = moolticuted.get_all_logins()
        print("[OK]")

        for login in data:
            print(f"- {login.service} [{login.multiple_domains}]:")
            for child in login.childs:
                print(f"\t * {child.model_dump()}")
    except moolticutepy.MoolticuteException as ex:
        log.fatal(f"{ex}")


@main.command()
@pass_client
@click.argument("service")
@click.option("--fallback-service", "-f", required=False, default=None)
@click.option("--login", "-l", required=False, default=None)
def get(
    moolticuted: moolticutepy.MoolticuteClient,
    service: str,
    fallback_service: str,
    login: str,
):
    try:
        response = moolticuted.get_password(
            service=service, fallback_service=fallback_service, login=login, timeout=20
        )
        print(response.data.password)
    except moolticutepy.MoolticuteException as ex:
        log.fatal(f"{ex}")


@main.command()
@pass_client
@click.argument("service")
@click.option("-l", "--login", required=False, default=None)
@click.option("-p", "--password", required=False, default=None)
@click.option("-d", "--description", required=False, default=None)
def set(
    moolticuted: moolticutepy.MoolticuteClient,
    service: str,
    login: Optional[str],
    password: Optional[str],
    description: Optional[str],
):
    if password is None:
        password = getpass.getpass(f"new password [{service}]:")
        password_confirm = getpass.getpass(f"confirm password [{service}]:")

        if password_confirm != password:
            log.error("Confirm password and password must be the same")
            sys.exit(1)

    error_message = None
    try:
        response = moolticuted.set_password(
            service,
            password=password,
            login=login,
            description=description,
            wait_confirmation=True,
            timeout=20,
        )
        error_message = response.data.error_message
    except moolticutepy.MoolticuteException as ex:
        error_message = str(ex)

    if error_message is not None:
        log.error(f"Error storing credentials: {error_message}")
        sys.exit(1)

    log.info(f"Credentials stored for {service} [OK]")


if __name__ == "__main__":
    main()
