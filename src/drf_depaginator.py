# coding: utf-8

from cgi import parse_qs

import logging
try:
    from urllib.parse import urlsplit
except ImportError:
    from urlparse import urlsplit


"""
Used by Django rest framework API consumers to depaginate API results

"""

# TODO: asynchronous versions of the depaginator.


logger = logging.getLogger(__name__)


class AutoDepaginator(object):
    def __init__(self, fetcher, **params):
        """
        fetcher: a callable that returns the json returned by the default
        Django's "rest_framework.pagination.LimitOffsetPagination":
        the root dictionary contains a 'next' url with 'limit' and 'offset' parameters,
        and the 'resuls' key contain the results for a page.

        Iterate over this instance to make API calls as needed and get all results
        one by one.

        Pass starting 'offset' and 'limit' parameters if values different from the defaults
        on the remote API are desired.
        NB: 'limit' won't return the number of entries fetched: just the number
        of results to be returned by the remote API for each request.

        """
        self.fetcher = fetcher
        self.params = params
        self._count = None
        self._ready = False

    def _read_next_page(self):
        page = self._page = self.fetcher(**self.params)
        try:
            self._next_url = page['next']
        except (TypeError, KeyError):
            logger.warning('Received a non-paginated result for {}. Check the system version on the remote site'.format(self.fetcher.__name__))
            self._results = page
            self._count = len(self._results)
            self._next_url = None
        else:
            self._count = int(page['count'])
            self._results = page['results']
        self._ready = True



    @property
    def count(self):
        if self._count is None:
            self._read_next_page()
        return self._count

    def __iter__(self):
        while True:
            if not self._ready:
                self._read_next_page()
            # This would be the case for yield from, but we
            # need Python 2.x compatibility
            for result in self._results:
                yield result
            self._ready = False

            if self._next_url:
                query_params = parse_qs(urlsplit(self._next_url).query)

                self.params['limit'] = int(query_params['limit'][0])
                self.params['offset'] = int(query_params['offset'][0])
            else:
                break

    def __len__(self):
        return self.count

