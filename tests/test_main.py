"""Tests for the main application entry point."""

from unittest.mock import Mock, patch

from ipbot.main import build_application, main


class TestBuildApplication:
    """Tests for the build_application function."""

    @patch("ipbot.main.BotConfig")
    @patch("ipbot.main.create_fetcher")
    @patch("ipbot.main.setup_handlers")
    @patch("ipbot.main.ApplicationBuilder")
    def test_build_application_creates_application(
        self, mock_app_builder, mock_setup_handlers, mock_create_fetcher, mock_config
    ):
        """Test that build_application creates and configures an Application."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.telegram_token = "test_token"
        mock_config_instance.get_strategy_list.return_value = ["ipify"]
        mock_config.return_value = mock_config_instance

        mock_fetcher = Mock()
        mock_create_fetcher.return_value = mock_fetcher

        mock_builder = Mock()
        mock_application = Mock()
        mock_application.bot_data = {}  # Make bot_data a real dict
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_application
        mock_app_builder.return_value = mock_builder

        # Call build_application
        result = build_application()

        # Verify config was loaded
        mock_config.assert_called_once()

        # Verify fetcher was created with first strategy
        mock_create_fetcher.assert_called_once_with("ipify")

        # Verify ApplicationBuilder was configured
        mock_app_builder.assert_called_once()
        mock_builder.token.assert_called_once_with("test_token")
        mock_builder.build.assert_called_once()

        # Verify bot_data was set
        assert mock_application.bot_data == {
            "config": mock_config_instance,
            "fetcher": mock_fetcher,
        }

        # Verify handlers were setup
        mock_setup_handlers.assert_called_once_with(mock_application)

        # Verify result is the application
        assert result == mock_application

    @patch("ipbot.main.BotConfig")
    @patch("ipbot.main.create_fetcher")
    def test_build_application_uses_first_strategy_from_list(
        self, mock_create_fetcher, mock_config
    ):
        """Test that build_application uses the first strategy from config list."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.telegram_token = "test_token"
        mock_config_instance.get_strategy_list.return_value = ["ipify", "ifconfigme", "curl"]
        mock_config.return_value = mock_config_instance

        with patch("ipbot.main.ApplicationBuilder"), patch("ipbot.main.setup_handlers"):
            build_application()

            # Verify only the first strategy was used
            mock_create_fetcher.assert_called_once_with("ipify")


class TestMain:
    """Tests for the main function."""

    @patch("ipbot.main.build_application")
    @patch("ipbot.main.logger")
    def test_main_runs_application(self, mock_logger, mock_build_app):
        """Test that main builds and runs the application."""
        # Setup mocks
        mock_application = Mock()
        mock_application.run_polling = Mock()
        mock_build_app.return_value = mock_application

        # Call main
        main()

        # Verify application was built
        mock_build_app.assert_called_once()

        # Verify polling was started
        mock_application.run_polling.assert_called_once()

        # Verify logging occurred
        assert mock_logger.info.call_count >= 1

    @patch("ipbot.main.build_application")
    @patch("ipbot.main.logger")
    def test_main_logs_startup(self, mock_logger, mock_build_app):
        """Test that main logs startup message."""
        # Setup mocks
        mock_application = Mock()
        mock_application.run_polling = Mock()
        mock_build_app.return_value = mock_application

        # Call main
        main()

        # Verify startup logging
        startup_calls = [
            call for call in mock_logger.info.call_args_list if "Starting" in str(call)
        ]
        assert len(startup_calls) > 0

    @patch("ipbot.main.build_application")
    @patch("ipbot.main.logger")
    def test_main_logs_shutdown(self, mock_logger, mock_build_app):
        """Test that main logs shutdown message."""
        # Setup mocks
        mock_application = Mock()
        mock_application.run_polling = Mock()
        mock_build_app.return_value = mock_application

        # Call main
        main()

        # Verify shutdown logging
        shutdown_calls = [
            call for call in mock_logger.info.call_args_list if "shutdown" in str(call).lower()
        ]
        assert len(shutdown_calls) > 0
