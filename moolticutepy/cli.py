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
        if mooltipass.is_locked:
            print("Waiting for mooltipass to unlock .... ", end="")
            mooltipass.wait_for_unlock()
            print("[OK]")

    ctx.obj[CLIENT_CTX] = mooltipass


@main.command()
@pass_client
@click.option(
    "-o",
    "--out-format",
    required=False,
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="text",
)
@click.option(
    "--linked",
    is_flag=True,
    show_default=True,
    default=False,
    help="Show only linked accounts",
)
@click.option(
    "--resolve-links",
    is_flag=True,
    show_default=True,
    default=False,
    help="Resolve links of accounts",
)
def list_logins(
    moolticuted: moolticutepy.MoolticuteClient,
    out_format: str,
    linked: bool,
    resolve_links: bool,
):
    if out_format == "json" and resolve_links:
        raise click.UsageError("Cannot use --resolve-links with json format")

    try:
        print(
            "Entering management mode. Please approve prompt on device ...",
            end="",
            file=sys.stderr,
        )
        sys.stderr.flush()
        data = moolticuted.get_all_logins()
        print("[OK]", file=sys.stderr)
        sys.stderr.flush()

        resolve_links_dict = dict()
        if resolve_links:
            for login in data:
                service = login.service
                for child in login.childs:
                    resolve_links_dict[str(child.address)] = dict(
                        service=service, login=child.login
                    )

        if out_format == "text":
            for login in data:

                has_linked = any(
                    map(lambda child: child.pointed_to_child != [0, 0], login.childs)
                )
                if linked and not has_linked:
                    continue

                print(f"- {login.service} [{login.multiple_domains}]:")
                for child in login.childs:
                    if linked and child.pointed_to_child == [0, 0]:
                        continue

                    print(f"\t * {child.login}:")
                    for k, v in child.model_dump(exclude=["login"]).items():
                        if k == "pointed_to_child" and resolve_links:
                            resolved_pointer = resolve_links_dict[str(v)]
                            print(f"\t\t - {k}: {v} -> {resolved_pointer}")
                        else:
                            print(f"\t\t - {k}: {v}")
        elif out_format == "json":
            for login in data:
                print(login.model_dump_json(exclude_none=False))

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
