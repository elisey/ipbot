"""Tests for the ResultFormatter."""

from ipbot.formatter import ResultFormatter
from ipbot.result import FetcherResult, FetchResult


def test_all_success_same_ip():
    """Test formatting when all fetchers succeed with the same IP."""
    result = FetchResult(
        results=[
            FetcherResult(fetcher_name="identme", success=True, ip="10.10.10.1"),
            FetcherResult(fetcher_name="ifconfig", success=True, ip="10.10.10.1"),
            FetcherResult(fetcher_name="ipify", success=True, ip="10.10.10.1"),
            FetcherResult(fetcher_name="ipinfo", success=True, ip="10.10.10.1"),
        ],
        consensus_ip="10.10.10.1",
        has_conflicts=False,
    )

    formatter = ResultFormatter()
    output = formatter.format(result)

    expected = """🌐 IP address: 10.10.10.1

🟢 identme
🟢 ifconfig
🟢 ipify
🟢 ipinfo"""

    assert output == expected


def test_partial_failure():
    """Test formatting when some fetchers fail but others agree."""
    result = FetchResult(
        results=[
            FetcherResult(fetcher_name="identme", success=True, ip="10.10.10.1"),
            FetcherResult(fetcher_name="ifconfig", success=False, error_type="Timeout"),
            FetcherResult(fetcher_name="ipify", success=True, ip="10.10.10.1"),
            FetcherResult(fetcher_name="ipinfo", success=True, ip="10.10.10.1"),
        ],
        consensus_ip="10.10.10.1",
        has_conflicts=False,
    )

    formatter = ResultFormatter()
    output = formatter.format(result)

    expected = """🌐 IP address: 10.10.10.1

🟢 identme
❌ ifconfig: Timeout
🟢 ipify
🟢 ipinfo"""

    assert output == expected


def test_ip_conflicts():
    """Test formatting when successful fetchers return different IPs."""
    result = FetchResult(
        results=[
            FetcherResult(fetcher_name="identme", success=True, ip="10.10.10.1"),
            FetcherResult(fetcher_name="ifconfig", success=False, error_type="Parsing error"),
            FetcherResult(fetcher_name="ipify", success=False, error_type="Network error"),
            FetcherResult(fetcher_name="ipinfo", success=True, ip="180.3.3.5"),
        ],
        consensus_ip=None,
        has_conflicts=True,
    )

    formatter = ResultFormatter()
    output = formatter.format(result)

    expected = """🌐 IP address: unknown

🟡 identme: 10.10.10.1
❌ ifconfig: Parsing error
❌ ipify: Network error
🟡 ipinfo: 180.3.3.5"""

    assert output == expected


def test_all_fetchers_fail():
    """Test formatting when all fetchers fail."""
    result = FetchResult(
        results=[
            FetcherResult(fetcher_name="identme", success=False, error_type="Timeout"),
            FetcherResult(fetcher_name="ifconfig", success=False, error_type="Network error"),
            FetcherResult(fetcher_name="ipify", success=False, error_type="Parsing error"),
            FetcherResult(fetcher_name="ipinfo", success=False, error_type="Error"),
        ],
        consensus_ip=None,
        has_conflicts=False,
    )

    formatter = ResultFormatter()
    output = formatter.format(result)

    expected = """🌐 IP address: unknown

❌ identme: Timeout
❌ ifconfig: Network error
❌ ipify: Parsing error
❌ ipinfo: Error"""

    assert output == expected


def test_single_fetcher_success():
    """Test formatting with a single successful fetcher."""
    result = FetchResult(
        results=[
            FetcherResult(fetcher_name="ipify", success=True, ip="192.168.1.1"),
        ],
        consensus_ip="192.168.1.1",
        has_conflicts=False,
    )

    formatter = ResultFormatter()
    output = formatter.format(result)

    expected = """🌐 IP address: 192.168.1.1

🟢 ipify"""

    assert output == expected


def test_mixed_errors():
    """Test formatting with different error types."""
    result = FetchResult(
        results=[
            FetcherResult(fetcher_name="identme", success=True, ip="1.1.1.1"),
            FetcherResult(fetcher_name="ifconfig", success=False, error_type="Timeout"),
            FetcherResult(fetcher_name="ipify", success=False, error_type="Network error"),
            FetcherResult(fetcher_name="ipinfo", success=True, ip="1.1.1.1"),
        ],
        consensus_ip="1.1.1.1",
        has_conflicts=False,
    )

    formatter = ResultFormatter()
    output = formatter.format(result)

    expected = """🌐 IP address: 1.1.1.1

🟢 identme
❌ ifconfig: Timeout
❌ ipify: Network error
🟢 ipinfo"""

    assert output == expected
