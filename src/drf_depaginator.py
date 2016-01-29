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
        self.limit = params.get('limit', None)
        self.offset = params.get('offset', 0)
        self._results_yielded = 0
        self.params = params
        self._count = None
        self._ready = False
        self._iteration_messed = False
        self._previous_next_url = None

    def _read_next_page(self):
        self._results_offset = self.params.get('offset', 0)
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
        if self.limit is not None:
            return min(self._count, self.limit)
        return self._count

    def __iter__(self):
        while True:
            if not self._ready:
                self._read_next_page()
            for i, result in enumerate(self._results[:]):
                if self._iteration_messed:

                    # a getitem on this object was called while iterating on
                    # self
                    self._next_url = self._previous_next_url
                    self._previous_next_url = None
                    self._iteration_messed = False
                if self.limit is not None and self._results_yielded >= self.limit:
                    raise StopIteration
                yield result
                self._results_yielded += 1
            self._ready = False

            if self._next_url:
                query_params = parse_qs(urlsplit(self._next_url).query)

                self.params['limit'] = int(query_params['limit'][0])
                self.params['offset'] = int(query_params['offset'][0])
            else:
                break

    def __getitem__(self, index):
        if not isinstance(index, (int, slice)):
            raise TypeError('Results index must be an integer')
        if isinstance(index, slice):
            return [self[i] for i in range(index.start or 0, index.stop or len(self), index.step or 1)]
        if index < 0:
            index += len(self)
        if index >= len(self):
            raise IndexError('Result index out of range')
        # Latest absolute fetched offset (on the backend)  minus configured
        # starting offset (on this client)
        current_results_relative_offset = self._results_offset - self.offset
        if current_results_relative_offset + index >= len(self._results):
            if not self._previous_next_url:
                self._previous_next_url = self._next_url
            self._iteration_messed = True
            self.params['offset'] = self.offset + index
            self._read_next_page()
            current_results_relative_offset = self._results_offset - self.offset

        return self._results[index - current_results_relative_offset]


    def __len__(self):
        return self.count

