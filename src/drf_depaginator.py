# coding: utf-8

from cgi import parse_qs

import logging
from urllib.parse import urlsplit


"""
Used by Django rest framework API consumers to depaginate API results

"""

# TODO: asynchronous versions of the depaginator.


logger = logging.getLogger(__name__)


class AutoDepaginator:
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
        self.count = 0

    def __iter__(self):
        while True:
            page = self.fetcher(**self.params)
            try:
                next_url = page['next']
            except (TypeError, KeyError):
                logger.warning('Received a non-paginated result for {}. Check the system version on the remote site'.format(self.fetcher.__name__))
                results = page
                self.count = len(results)
                next_url = None
            else:
                self.count = int(page['count'])
                results = page['results']

            yield from results

            if next_url:
                query_params = parse_qs(urlsplit(next_url).query)

                self.params['limit'] = int(query_params['limit'][0])
                self.params['offset'] = int(query_params['offset'][0])
            else:
                break

    def __len__(self):
        return self.count

