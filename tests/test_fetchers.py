"""Tests for IP fetching strategies."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from ipbot.factory import create_fetcher
from ipbot.fetchers.ipify import IpifyStrategy


class TestIpifyStrategy:
    """Tests for the IpifyStrategy IP fetcher."""

    @pytest.mark.asyncio
    async def test_get_ip_success(self):
        """Test successful IP fetch with JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ip": "203.0.113.42"}
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            strategy = IpifyStrategy()
            ip = await strategy.get_ip()

            assert ip == "203.0.113.42"
            mock_client.get.assert_called_once_with("https://api.ipify.org?format=json")

    @pytest.mark.asyncio
    async def test_get_ip_http_error(self):
        """Test handling of HTTP errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.HTTPError("Connection failed")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            strategy = IpifyStrategy()

            with pytest.raises(Exception, match="Failed to fetch IP"):
                await strategy.get_ip()

    @pytest.mark.asyncio
    async def test_get_ip_timeout(self):
        """Test handling of timeout errors."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
            mock_client_class.return_value.__aenter__.return_value = mock_client

            strategy = IpifyStrategy()

            with pytest.raises(Exception, match="Failed to fetch IP"):
                await strategy.get_ip()

    @pytest.mark.asyncio
    async def test_get_ip_invalid_status_code(self):
        """Test handling of non-200 status codes."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status = Mock(
            side_effect=httpx.HTTPStatusError(
                "Server error", request=Mock(), response=mock_response
            )
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            strategy = IpifyStrategy()

            with pytest.raises(Exception, match="Failed to fetch IP"):
                await strategy.get_ip()

    @pytest.mark.asyncio
    async def test_get_ip_invalid_json_response(self):
        """Test handling of invalid JSON response format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"wrong_key": "value"}
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            strategy = IpifyStrategy()

            with pytest.raises(Exception, match="Invalid response format"):
                await strategy.get_ip()

    @pytest.mark.asyncio
    async def test_client_configured_with_timeout(self):
        """Test that httpx client is configured with proper timeout."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ip": "203.0.113.42"}
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            strategy = IpifyStrategy()
            await strategy.get_ip()

            # Verify AsyncClient was called with timeout parameter
            mock_client_class.assert_called_once()
            call_kwargs = mock_client_class.call_args[1]
            assert "timeout" in call_kwargs
            assert call_kwargs["timeout"] == 3.0


class TestFactory:
    """Tests for the IP fetcher factory."""

    def test_create_fetcher_ipify(self):
        """Test factory creates IpifyStrategy for 'ipify' strategy name."""
        fetcher = create_fetcher("ipify")
        assert isinstance(fetcher, IpifyStrategy)

    def test_create_fetcher_unknown_strategy(self):
        """Test factory raises error for unknown strategy name."""
        with pytest.raises(ValueError, match="Unknown IP fetcher strategy"):
            create_fetcher("unknown_strategy")

    def test_create_fetcher_empty_string(self):
        """Test factory raises error for empty strategy name."""
        with pytest.raises(ValueError, match="Unknown IP fetcher strategy"):
            create_fetcher("")
