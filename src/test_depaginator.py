# coding: utf-8

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

import pytest

from drf_depaginator import AutoDepaginator


result = {
    'count': 3,
    'next': 'http://localhost:8010/v1/packages/?limit=2&offset=2',
    'previous': None,
    'results': [
        {'somekey': 'somecontent'},
        {'somekey': 'another content'}
    ]
}


def real_fetcher(limit=2, offset=0):
        results = [{0: 0}, {1: 1}, {2: 2}, {3: 3}]
        if offset + limit < len(results):
            next_ = '/?limit={}&offset={}'.format(limit, offset + limit)
        else:
            next_ = None
        return {'count': len(results), 'next': next_, 'results': results[offset: offset + limit]}


def test_depaginator_calls_fetcher():
    fetcher = Mock()
    fetcher.side_effect = [result]
    paginator = iter(AutoDepaginator(fetcher))
    next(paginator)
    fetcher.assert_called_with()


def test_depaginator_returns_results():
    fetcher = Mock()
    fetcher.side_effect = [result]
    paginator = iter(AutoDepaginator(fetcher))
    r0 = next(paginator)
    fetcher.assert_called_with()
    r1 = next(paginator)
    assert r0 == result['results'][0]
    assert r1 == result['results'][1]


def test_depaginator_requests_next_api_page():
    fetcher = Mock()
    fetcher.side_effect = [result, {'next': None, 'count': 3, 'results': [{'somekey': 'yet another content'}]}]
    paginator = iter(AutoDepaginator(fetcher))
    r0 = next(paginator)
    r1 = next(paginator)
    assert r0 == result['results'][0]
    assert r1 == result['results'][1]
    fetcher.assert_called_once_with()
    r2 = next(paginator)
    fetcher.assert_called_with(limit=2, offset=2)
    assert r2 == {'somekey': 'yet another content'}


def test_depaginator_stops_iteration():
    fetcher = Mock()
    fetcher.side_effect = [result, {'next': None, 'count': 3, 'results': [{'somekey': 'yet another content'}]}]
    paginator = iter(AutoDepaginator(fetcher))
    next(paginator)
    next(paginator)
    fetcher.assert_called_once_with()
    next(paginator)
    fetcher.assert_called_with(limit=2, offset=2)
    with pytest.raises(StopIteration):
        next(paginator)


def test_depaginator_works_with_non_paginating_results_and_warns():
    fetcher = Mock()
    fetcher.side_effect = [result['results']]
    fetcher.__name__ = 'test_fetcher'
    with patch('drf_depaginator.logger') as paginator_logger:
        paginator = iter(AutoDepaginator(fetcher))
        response = list(paginator)
        assert len(response) == 2
        assert response == result['results']
        assert any(str(call).startswith('call.warning') for call in paginator_logger.mock_calls), \
            'AutoDepaginator did not log warning about non-compliant API return'


def test_depaginator_len_works_even_without_iterating():
    fetcher = Mock()
    fetcher.side_effect = [result]
    paginator = AutoDepaginator(fetcher)
    assert len(paginator)


def test_depaginator_respects_passed_limit():
    def _get_fetcher():
        fetcher = Mock()
        fetcher.side_effect = [result, {'next': None, 'count': 4, 'results': [{'somekey': 'yet another content'}, {}]}]
        return fetcher

    paginator = AutoDepaginator(_get_fetcher(), limit=1)
    assert len(list(paginator)) == 1

    paginator = AutoDepaginator(_get_fetcher(), limit=3)
    assert len(list(paginator)) == 3


def test_depaginator_respects_passed_offset():

    paginator = AutoDepaginator(real_fetcher, limit=1, offset=2)
    results = list(paginator)
    assert len(results) == 1
    assert results[0] == {2: 2}


def test_depaginator_getitem_works():
    fetcher = Mock()
    fetcher.side_effect = [result]
    paginator = AutoDepaginator(fetcher)
    x = paginator[0]
    assert 'somekey' in x
    assert x['somekey'] == 'somecontent'
    assert paginator[1]['somekey'] == 'another content'


def test_depaginator_getitem_works_across_pages():
    def _get_fetcher():
        fetcher = Mock()
        fetcher.side_effect = [result, {'next': None, 'count': 4, 'results': [{'somekey': 'yet another content'}, {}]}]
        return fetcher

    paginator = AutoDepaginator(_get_fetcher())
    x = paginator[2]
    assert 'somekey' in x
    assert x['somekey'] == 'yet another content'


def test_depaginator_iteration_works_intercalled_with_getitem():
    paginator = AutoDepaginator(real_fetcher)

    for i, result in enumerate(paginator):
        if i == 2:
            assert paginator[0][0] == 0
    assert i == 3
    assert result == {3: 3}
