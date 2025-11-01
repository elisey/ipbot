from ipbot.fetchers.base import FetchStrategy
from ipbot.fetchers.exceptions import FetcherParsingError
from ipbot.fetchers.http_fetcher import HttpFetcher


class CustomStrategy(FetchStrategy):
    IFCONFIG_URL = "https://" + "myip" + ".elisei" + ".nl"
    TIMEOUT = 3.0

    async def get_ip(self) -> str:
        http_fetcher = HttpFetcher(timeout=self.TIMEOUT)
        response = await http_fetcher.fetch(self.IFCONFIG_URL, self.get_name())

        ip_address = response.text.strip()

        if not ip_address:
            raise FetcherParsingError("Invalid response format from ifconfig.me: empty response")

        return ip_address

    def get_name(self) -> str:
        return "myip" + ".elisei" + ".nl"
