"""Tests for the main application entry point."""

from unittest.mock import Mock, patch

from ipbot.main import build_application, main


class TestBuildApplication:
    """Tests for the build_application function."""

    @patch("ipbot.main.BotConfig")
    @patch("ipbot.main.create_fetchers")
    @patch("ipbot.main.ParallelFetchOrchestrator")
    @patch("ipbot.main.setup_handlers")
    @patch("ipbot.main.ApplicationBuilder")
    def test_build_application_creates_application(
        self,
        mock_app_builder,
        mock_setup_handlers,
        mock_orchestrator_class,
        mock_create_fetchers,
        mock_config,
    ):
        """Test that build_application creates and configures an Application."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.telegram_token = "test_token"
        mock_config.return_value = mock_config_instance

        mock_fetcher1 = Mock()
        mock_fetcher1.get_name.return_value = "ipify.org"
        mock_fetcher2 = Mock()
        mock_fetcher2.get_name.return_value = "identme"
        mock_create_fetchers.return_value = [mock_fetcher1, mock_fetcher2]

        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

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

        # Verify fetchers were created with config
        mock_create_fetchers.assert_called_once_with(mock_config_instance)

        # Verify orchestrator was created with all fetchers
        mock_orchestrator_class.assert_called_once_with([mock_fetcher1, mock_fetcher2])

        # Verify ApplicationBuilder was configured
        mock_app_builder.assert_called_once()
        mock_builder.token.assert_called_once_with("test_token")
        mock_builder.build.assert_called_once()

        # Verify bot_data was set with orchestrator
        assert mock_application.bot_data == {
            "config": mock_config_instance,
            "orchestrator": mock_orchestrator,
        }

        # Verify handlers were setup
        mock_setup_handlers.assert_called_once_with(mock_application)

        # Verify result is the application
        assert result == mock_application

    @patch("ipbot.main.BotConfig")
    @patch("ipbot.main.create_fetchers")
    @patch("ipbot.main.ParallelFetchOrchestrator")
    def test_build_application_uses_create_fetchers(
        self, mock_orchestrator_class, mock_create_fetchers, mock_config
    ):
        """Test that build_application uses create_fetchers function."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.telegram_token = "test_token"
        mock_config.return_value = mock_config_instance

        mock_fetcher1 = Mock()
        mock_fetcher1.get_name.return_value = "fetcher1"
        mock_fetcher2 = Mock()
        mock_fetcher2.get_name.return_value = "fetcher2"
        mock_fetcher3 = Mock()
        mock_fetcher3.get_name.return_value = "fetcher3"
        mock_create_fetchers.return_value = [mock_fetcher1, mock_fetcher2, mock_fetcher3]

        with patch("ipbot.main.ApplicationBuilder"), patch("ipbot.main.setup_handlers"):
            build_application()

            # Verify create_fetchers was called with config
            mock_create_fetchers.assert_called_once_with(mock_config_instance)

            # Verify orchestrator was created with all fetchers
            mock_orchestrator_class.assert_called_once_with(
                [mock_fetcher1, mock_fetcher2, mock_fetcher3]
            )


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
