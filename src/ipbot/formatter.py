"""Formatter for displaying IP fetching results."""

from ipbot.result import FetchResult


class ResultFormatter:
    """Formats FetchResult into a user-friendly message.

    Displays IP address at the top and shows status for each fetcher
    with appropriate emoji indicators.
    """

    def format(self, result: FetchResult) -> str:
        """Format a FetchResult into a display message.

        Args:
            result: The FetchResult to format.

        Returns:
            A formatted string with IP address and fetcher statuses.
        """
        lines = []

        # Header with IP address
        ip_display = result.consensus_ip if result.consensus_ip else "unknown"
        lines.append(f"🌐 IP address: {ip_display}")
        lines.append("")  # Blank line

        # Fetcher results
        for fetcher_result in result.results:
            if fetcher_result.success:
                if result.has_conflicts:
                    # Show IP for each fetcher when there are conflicts
                    lines.append(f"🟡 {fetcher_result.fetcher_name}: {fetcher_result.ip}")
                else:
                    # Just show success when all agree
                    lines.append(f"🟢 {fetcher_result.fetcher_name}")
            else:
                # Show error
                lines.append(f"❌ {fetcher_result.fetcher_name}: {fetcher_result.error_type}")

        return "\n".join(lines)
