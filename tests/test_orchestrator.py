"""Tests for the ParallelFetchOrchestrator."""

import pytest

from ipbot.fetchers.base import FetchStrategy
from ipbot.fetchers.exceptions import FetcherHTTPError, FetcherParsingError
from ipbot.orchestrator import ParallelFetchOrchestrator


class MockFetcher(FetchStrategy):
    """Mock fetcher for testing."""

    def __init__(self, name: str, ip: str | None = None, exception: Exception | None = None):
        """Initialize mock fetcher.

        Args:
            name: Name of the fetcher.
            ip: IP address to return (if successful).
            exception: Exception to raise (if failing).
        """
        self._name = name
        self._ip = ip
        self._exception = exception

    def get_name(self) -> str:
        """Return the fetcher name."""
        return self._name

    async def get_ip(self) -> str:
        """Return IP or raise exception."""
        if self._exception:
            raise self._exception
        if self._ip:
            return self._ip
        raise ValueError("Either ip or exception must be provided")


@pytest.mark.asyncio
async def test_all_fetchers_succeed_same_ip():
    """Test when all fetchers succeed and return the same IP."""
    fetchers = [
        MockFetcher("fetcher1", ip="10.10.10.1"),
        MockFetcher("fetcher2", ip="10.10.10.1"),
        MockFetcher("fetcher3", ip="10.10.10.1"),
    ]

    orchestrator = ParallelFetchOrchestrator(fetchers)
    result = await orchestrator.fetch_all()

    assert result.consensus_ip == "10.10.10.1"
    assert result.has_conflicts is False
    assert len(result.results) == 3

    for fetcher_result in result.results:
        assert fetcher_result.success is True
        assert fetcher_result.ip == "10.10.10.1"
        assert fetcher_result.error_type is None


@pytest.mark.asyncio
async def test_some_fetchers_fail_others_agree():
    """Test when some fetchers fail but successful ones agree."""
    fetchers = [
        MockFetcher("fetcher1", ip="10.10.10.1"),
        MockFetcher("fetcher2", exception=FetcherHTTPError("Network error")),
        MockFetcher("fetcher3", ip="10.10.10.1"),
        MockFetcher("fetcher4", exception=TimeoutError()),
    ]

    orchestrator = ParallelFetchOrchestrator(fetchers)
    result = await orchestrator.fetch_all()

    assert result.consensus_ip == "10.10.10.1"
    assert result.has_conflicts is False
    assert len(result.results) == 4

    # Check successful fetchers
    assert result.results[0].success is True
    assert result.results[0].ip == "10.10.10.1"
    assert result.results[0].fetcher_name == "fetcher1"

    assert result.results[2].success is True
    assert result.results[2].ip == "10.10.10.1"
    assert result.results[2].fetcher_name == "fetcher3"

    # Check failed fetchers
    assert result.results[1].success is False
    assert result.results[1].error_type == "Network error"
    assert result.results[1].fetcher_name == "fetcher2"

    assert result.results[3].success is False
    assert result.results[3].error_type == "Timeout"
    assert result.results[3].fetcher_name == "fetcher4"


@pytest.mark.asyncio
async def test_ip_conflicts():
    """Test when successful fetchers return different IPs."""
    fetchers = [
        MockFetcher("fetcher1", ip="10.10.10.1"),
        MockFetcher("fetcher2", exception=FetcherParsingError("Invalid format")),
        MockFetcher("fetcher3", ip="180.3.3.5"),
        MockFetcher("fetcher4", ip="10.10.10.1"),
    ]

    orchestrator = ParallelFetchOrchestrator(fetchers)
    result = await orchestrator.fetch_all()

    assert result.consensus_ip is None
    assert result.has_conflicts is True
    assert len(result.results) == 4

    # Check that IPs are captured
    assert result.results[0].ip == "10.10.10.1"
    assert result.results[2].ip == "180.3.3.5"
    assert result.results[3].ip == "10.10.10.1"

    # Check parsing error
    assert result.results[1].success is False
    assert result.results[1].error_type == "Parsing error"


@pytest.mark.asyncio
async def test_all_fetchers_fail():
    """Test when all fetchers fail."""
    fetchers = [
        MockFetcher("fetcher1", exception=FetcherHTTPError("Network error")),
        MockFetcher("fetcher2", exception=TimeoutError()),
        MockFetcher("fetcher3", exception=FetcherParsingError("Invalid format")),
    ]

    orchestrator = ParallelFetchOrchestrator(fetchers)
    result = await orchestrator.fetch_all()

    assert result.consensus_ip is None
    assert result.has_conflicts is False
    assert len(result.results) == 3

    for fetcher_result in result.results:
        assert fetcher_result.success is False
        assert fetcher_result.error_type is not None


@pytest.mark.asyncio
async def test_error_categorization():
    """Test that errors are correctly categorized."""
    fetchers = [
        MockFetcher("fetcher1", exception=TimeoutError()),
        MockFetcher("fetcher2", exception=FetcherHTTPError("Network error")),
        MockFetcher("fetcher3", exception=FetcherParsingError("Parse error")),
        MockFetcher("fetcher4", exception=ValueError("Some other error")),
    ]

    orchestrator = ParallelFetchOrchestrator(fetchers)
    result = await orchestrator.fetch_all()

    assert result.results[0].error_type == "Timeout"
    assert result.results[1].error_type == "Network error"
    assert result.results[2].error_type == "Parsing error"
    assert result.results[3].error_type == "Error"


@pytest.mark.asyncio
async def test_single_fetcher_success():
    """Test with a single fetcher that succeeds."""
    fetchers = [MockFetcher("single", ip="192.168.1.1")]

    orchestrator = ParallelFetchOrchestrator(fetchers)
    result = await orchestrator.fetch_all()

    assert result.consensus_ip == "192.168.1.1"
    assert result.has_conflicts is False
    assert len(result.results) == 1
    assert result.results[0].success is True


@pytest.mark.asyncio
async def test_fetcher_names_preserved():
    """Test that fetcher names are correctly preserved in results."""
    fetchers = [
        MockFetcher("ipify", ip="1.1.1.1"),
        MockFetcher("identme", ip="1.1.1.1"),
        MockFetcher("ifconfig", exception=FetcherHTTPError("Error")),
        MockFetcher("ipinfo", ip="1.1.1.1"),
    ]

    orchestrator = ParallelFetchOrchestrator(fetchers)
    result = await orchestrator.fetch_all()

    assert result.results[0].fetcher_name == "ipify"
    assert result.results[1].fetcher_name == "identme"
    assert result.results[2].fetcher_name == "ifconfig"
    assert result.results[3].fetcher_name == "ipinfo"
