# Adapted from: https://github.com/encode/httpx/blob/master/httpx/_models.py,
# which is licensed under the BSD License.
# See https://github.com/encode/httpx/blob/master/LICENSE.md

__all__ = ["Cookies"]

import re
import time
import typing
from http.cookiejar import Cookie, CookieJar
from urllib.parse import urlparse
from dataclasses import dataclass

from .errors import CookieConflict, RequestsError

CookieTypes = typing.Union[
    "Cookies", CookieJar, typing.Dict[str, str], typing.List[typing.Tuple[str, str]]
]


@dataclass
class CurlMorsel:
    name: str
    value: str
    hostname: str = ""
    subdomains: bool = False
    path: str = "/"
    secure: bool = False
    expires: int = 0
    http_only: bool = False

    @staticmethod
    def parse_bool(s):
        return s == "TRUE"

    @staticmethod
    def dump_bool(s):
        return "TRUE" if s else "FALSE"

    @classmethod
    def from_curl_format(cls, set_cookie_line: bytes):
        (
            hostname,
            subdomains,
            path,
            secure,
            expires,
            name,
            value,
        ) = set_cookie_line.decode().split("\t")
        if hostname and hostname[0] == "#":
            http_only = True
            # e.g. #HttpOnly_postman-echo.com
            domain = hostname[10:]  # len("#HttpOnly_") == 10
        else:
            http_only = False
            domain = hostname
        return cls(
            hostname=domain,
            subdomains=cls.parse_bool(subdomains),
            path=path,
            secure=cls.parse_bool(secure),
            expires=int(expires),
            name=name,
            value=value,
            http_only=http_only,
        )

    def to_curl_format(self):
        if not self.hostname:
            raise RequestsError(
                "Domain not found for cookie {}={}".format(self.name, self.value)
            )
        return "\t".join(
            [
                self.hostname,
                self.dump_bool(self.subdomains),
                self.path,
                self.dump_bool(self.secure),
                str(self.expires),
                self.name,
                self.value,
            ]
        )

    @classmethod
    def from_cookiejar_cookie(cls, cookie: Cookie):
        return cls(
            name=cookie.name,
            value=cookie.value or "",
            hostname=cookie.domain,
            subdomains=cookie.domain_initial_dot,
            path=cookie.path,
            secure=cookie.secure,
            expires=int(cookie.expires or 0),
            http_only=False,
        )

    def to_cookiejar_cookie(self) -> Cookie:
        # the leading dot actually does not mean anything nowadays
        # https://stackoverflow.com/a/20884869/1061155
        # https://github.com/python/cpython/blob/d6555abfa7384b5a40435a11bdd2aa6bbf8f5cfc/Lib/http/cookiejar.py#L1535
        return Cookie(
            version=0,
            name=self.name,
            value=self.value,
            port=None,
            port_specified=False,
            domain=self.hostname,
            domain_specified=True,
            domain_initial_dot=bool(self.hostname.startswith(".")),
            path=self.path,
            path_specified=bool(self.path),
            secure=self.secure,
            # using if explicitly to make it clear.
            expires=None if self.expires == 0 else self.expires,
            discard=True if self.expires == 0 else False,
            comment=None,
            comment_url=None,
            rest=dict(http_only=self.http_only),  # type: ignore
            rfc2109=False,
        )


cut_port_re = re.compile(r":\d+$", re.ASCII)
IPV4_RE = re.compile(r"\.\d+$", re.ASCII)


class Cookies(typing.MutableMapping[str, str]):
    """
    HTTP Cookies, as a mutable mapping.
    """

    def __init__(self, cookies: typing.Optional[CookieTypes] = None) -> None:
        if cookies is None or isinstance(cookies, dict):
            self.jar = CookieJar()
            if isinstance(cookies, dict):
                for key, value in cookies.items():
                    self.set(key, value)
        elif isinstance(cookies, list):
            self.jar = CookieJar()
            for key, value in cookies:
                self.set(key, value)
        elif isinstance(cookies, Cookies):
            self.jar = CookieJar()
            for cookie in cookies.jar:
                self.jar.set_cookie(cookie)
        else:
            self.jar = cookies

    def _eff_request_host(self, request) -> str:
        """
        Almost equivalent to the eff_request_host function in:
            https://github.com/python/cpython/blob/3.11/Lib/http/cookiejar.py#L636
        """
        host = urlparse(request.url)[1]
        if host == "":
            host = request.headers.get("Host", "")

        # remove port, if present
        host = cut_port_re.sub("", host, 1)
        host = host.lower()
        if host.find(".") == -1 and not IPV4_RE.search(host):
            host += ".local"
        return host

    def get_cookies_for_curl(self, request) -> typing.List[CurlMorsel]:
        """the process is similar to `cookiejar.add_cookie_header`, but load all cookies"""
        self.jar._cookies_lock.acquire()  # type: ignore
        morsels = []
        try:
            self.jar._policy._now = self._now = int(time.time())  # type: ignore
            for cookie in self.jar:
                morsel = CurlMorsel.from_cookiejar_cookie(cookie)
                if not morsel.hostname:
                    morsel.hostname = self._eff_request_host(request)
                morsels.append(morsel)
        finally:
            self.jar._cookies_lock.release()  # type: ignore

        self.jar.clear_expired_cookies()
        return morsels

    def update_cookies_from_curl(self, morsels: typing.List[CurlMorsel]):
        for morsel in morsels:
            cookie = morsel.to_cookiejar_cookie()
            self.jar.set_cookie(cookie)
        self.jar.clear_expired_cookies()

    def set(self, name: str, value: str, domain: str = "", path: str = "/") -> None:
        """
        Set a cookie value by name. May optionally include domain and path.
        """
        kwargs = {
            "version": 0,
            "name": name,
            "value": value,
            "port": None,
            "port_specified": False,
            "domain": domain,
            "domain_specified": bool(domain),
            "domain_initial_dot": domain.startswith("."),
            "path": path,
            "path_specified": bool(path),
            "secure": False,
            "expires": None,
            "discard": True,
            "comment": None,
            "comment_url": None,
            "rest": {"HttpOnly": None},
            "rfc2109": False,
        }
        cookie = Cookie(**kwargs)  # type: ignore
        self.jar.set_cookie(cookie)

    def get(  # type: ignore
        self,
        name: str,
        default: typing.Optional[str] = None,
        domain: typing.Optional[str] = None,
        path: typing.Optional[str] = None,
    ) -> typing.Optional[str]:
        """
        Get a cookie by name. May optionally include domain and path
        in order to specify exactly which cookie to retrieve.
        """
        value = None
        matched_domain = ""
        for cookie in self.jar:
            if cookie.name == name:
                if domain is None or cookie.domain == domain:
                    if path is None or cookie.path == path:
                        # if cookies on two different domains do not share a same value
                        if (
                            value is not None
                            and not matched_domain.endswith(cookie.domain)
                            and not str(cookie.domain).endswith(matched_domain)
                            and value != cookie.value
                        ):
                            message = (
                                f"Multiple cookies exist with name={name} on "
                                f"{matched_domain} and {cookie.domain}"
                            )
                            raise CookieConflict(message)
                        value = cookie.value
                        matched_domain = cookie.domain or ""

        if value is None:
            return default
        return value

    def delete(
        self,
        name: str,
        domain: typing.Optional[str] = None,
        path: typing.Optional[str] = None,
    ) -> None:
        """
        Delete a cookie by name. May optionally include domain and path
        in order to specify exactly which cookie to delete.
        """
        if domain is not None and path is not None:
            return self.jar.clear(domain, path, name)

        remove = [
            cookie
            for cookie in self.jar
            if cookie.name == name
            and (domain is None or cookie.domain == domain)
            and (path is None or cookie.path == path)
        ]

        for cookie in remove:
            self.jar.clear(cookie.domain, cookie.path, cookie.name)

    def clear(
        self, domain: typing.Optional[str] = None, path: typing.Optional[str] = None
    ) -> None:
        """
        Delete all cookies. Optionally include a domain and path in
        order to only delete a subset of all the cookies.
        """
        args = []
        if domain is not None:
            args.append(domain)
        if path is not None:
            assert domain is not None
            args.append(path)
        self.jar.clear(*args)

    def update(self, cookies: typing.Optional[CookieTypes] = None) -> None:  # type: ignore
        cookies = Cookies(cookies)
        for cookie in cookies.jar:
            self.jar.set_cookie(cookie)

    def __setitem__(self, name: str, value: str) -> None:
        return self.set(name, value)

    def __getitem__(self, name: str) -> str:
        value = self.get(name)
        if value is None:
            raise KeyError(name)
        return value

    def __delitem__(self, name: str) -> None:
        return self.delete(name)

    def __len__(self) -> int:
        return len(self.jar)

    def __iter__(self) -> typing.Iterator[str]:
        return (cookie.name for cookie in self.jar)

    def __bool__(self) -> bool:
        for _ in self.jar:
            return True
        return False

    def __repr__(self) -> str:
        cookies_repr = ", ".join(
            [
                f"<Cookie {cookie.name}={cookie.value} for {cookie.domain} />"
                for cookie in self.jar
            ]
        )

        return f"<Cookies[{cookies_repr}]>"
