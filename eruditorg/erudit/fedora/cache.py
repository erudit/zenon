# -*- coding: utf-8 -*-
import typing
import random
import requests
import structlog

from django.conf import settings
from django.core.cache import caches, cache
from django.utils.translation import get_language
from requests.exceptions import HTTPError, ConnectionError
from sentry_sdk import configure_scope

from ..conf import settings as erudit_settings
from erudit.cache import cache_set
from django_redis.cache import RedisCache

logger = structlog.getLogger(__name__)


def cache_fedora_result(method, duration=settings.LONG_TTL):
    """Cache the result of a method called on a FedoraMixin object

    Assumes that the method is bound to a FedoraMixin object, or at least that the object has a
    ``localidentifier`` attribute.

    If the value of ``localidentifier`` is ``None``, cache will not be queried and the decorated
    method will be called directly.

    This decorator assumes that the localidentifier is unique for ALL Fedora objects.

    Will cache the result for the value of ``duration``, plus or minus ``duration`` * 0.25. This
    is to avoid expiring all the cached resources at the same time.

    :param method: the method to decorate
    :param duration: expected duration of result cache
    :return: the decorated method
    """

    def wrapper(self, *args, **kwargs):

        if not self.localidentifier:
            return method(self, *args, **kwargs)

        key = "fedora_result-{lang}-{localidentifier}-{method_name}".format(
            lang=get_language(), localidentifier=self.localidentifier, method_name=method.__name__
        )

        val = cache.get(key)

        if not val:
            duration_deviation = random.randint(-(duration // 4), duration // 4)
            val = method(self, *args, **kwargs)
            cache_set(
                cache,
                key,
                val,
                duration + duration_deviation,
                pids=[self.pid],
            )
        return val

    return wrapper


def get_datastream_file_cache() -> RedisCache:
    return caches[erudit_settings.FEDORA_FILEBASED_CACHE_NAME]


def get_cached_datastream_content(
    pid: str, datastream_name: str, cache_key: typing.Optional[str] = None
) -> bytes:
    """Given a Fedora object pid and a datastream name, returns the content of the datastream.

    Note that this content can be cached in a file-based cache!
    """
    if not cache_key:
        content_key = f"erudit-fedora-file-{pid}-{datastream_name}"
    else:
        content_key = cache_key

    content = cache.get(content_key)

    if content is None:
        try:
            response = requests.get(
                settings.FEDORA_ROOT + f"objects/{pid}/datastreams/{datastream_name}/content",
            )
            response.raise_for_status()
            content = response.content

            cache_set(
                cache,
                content_key,
                content,
                settings.FEDORA_CACHE_TIMEOUT,
                pids=[pid],
            )
        except (HTTPError, ConnectionError):  # pragma: no cover
            with configure_scope() as scope:
                scope.fingerprint = ["fedora-warnings"]
                logger.warning("fedora.exception", pid=pid, datastream=datastream_name)
    return content
