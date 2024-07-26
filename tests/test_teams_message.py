import pytest
import pymsteams
from dsptools.utils.notifications import send_teams_message
from dsptools.errors.execution import TeamsMessageError


class TestSendTeamsMessage:

    # Successfully sends a message to a Microsoft Teams channel using a valid webhook URL
    def test_successful_message_send(self, mocker):
        webhook_url = "https://valid.webhook.url"
        message = "Hello, Teams!"

        mock_connectorcard = mocker.patch("pymsteams.connectorcard")
        mock_teams_message = mocker.Mock()
        mock_connectorcard.return_value = mock_teams_message

        send_teams_message(webhook_url, message)

        mock_connectorcard.assert_called_once_with(webhook_url)
        mock_teams_message.text.assert_called_once_with(message)
        mock_teams_message.send.assert_called_once()

    # Handles invalid webhook URL by raising TeamsMessageError
    def test_invalid_webhook_url(self, mocker):
        webhook_url = "https://invalid.webhook.url"
        message = "Hello, Teams!"

        mock_connectorcard = mocker.patch("pymsteams.connectorcard")
        mock_connectorcard.side_effect = pymsteams.WebhookUrlError("Invalid URL")

        with pytest.raises(TeamsMessageError) as exc_info:
            send_teams_message(webhook_url, message)

        assert "Error sending Teams message" in str(exc_info.value)

    def test_successful_message_send_empty_message(self, mocker):
        webhook_url = "https://valid.webhook.url"
        message = ""

        mock_connectorcard = mocker.patch("pymsteams.connectorcard")
        mock_teams_message = mocker.Mock()
        mock_connectorcard.return_value = mock_teams_message

        send_teams_message(webhook_url, message)

        mock_connectorcard.assert_called_once_with(webhook_url)
        mock_teams_message.text.assert_called_once_with(message)
        mock_teams_message.send.assert_called_once()

    def test_message_send_failure(self, mocker):
        webhook_url = "https://valid.webhook.url"
        message = "Hello, Teams!"

        mock_connectorcard = mocker.patch("pymsteams.connectorcard")
        mock_teams_message = mocker.Mock()
        mock_connectorcard.return_value = mock_teams_message
        mock_teams_message.send.side_effect = pymsteams.TeamsWebhookException(
            "Failed to send message"
        )

        with pytest.raises(TeamsMessageError) as exc_info:
            send_teams_message(webhook_url, message)

        assert "Error sending Teams message" in str(exc_info.value)
