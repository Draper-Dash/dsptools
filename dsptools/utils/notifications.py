# pylint: skip-file
from __future__ import annotations
from typing import List, Optional
import requests
import msal
import base64
import os
import pymsteams  # type: ignore[import-not-found]
from dsptools.errors.data import EmailAttachmentError
from dsptools.errors.execution import TeamsMessageError


def send_email(
    email_clientid: str,
    email_secret: str,
    email_tenantid: str,
    emails: List[str],
    subject: str,
    message: str,
    attachments: Optional[List[str]] = None,
    sender: str = "dsp-notifications@realworld.health",
) -> None:
    # TODO implement keyvalut and get rid of inbox and pwd params
    """
    Send an email with an optional attachment to a list of recipients using Microsoft Graph API.

    Args:
        email_clientid: The Client ID of the Service Principal being used to send the email.
        email_secret: The Client Secret of the Service Principal being used to send the email.
        email_tenantid The Tenant ID of the Service Principal being used to send the email.
        emails (List[str]): List of email addresses to send the email to.
        subject (str): The email subject.
        message (str): The email message content (HTML).
        attachment (str, optional): Path to the attachment file (PDF, DOC, CSV, TXT, or LOG). Default is None.
        sender (str, optional): The sender's email address.

    Raises:
        EmailAttachmentError: If the attachment file type is not supported.
        Exception: If there is an issue with sending the email.

    Example:
        send_email(
            email_clientid="your_client_id",
            email_secret="your_client_secret",
            email_tenantid="your_tenant_id",
            emails=["recipient@example.com"],
            subject="Important Report",
            message="<html><body>...</body></html>",
            attachment="report.pdf"
        )
    """
    supported_attachment_types = (
        ".pdf",
        ".doc",
        ".csv",
        ".txt",
        ".log",
        ".jpg",
        ".jpeg",
        ".png",
    )

    if attachments:
        for attachment in attachments:
            if not attachment.endswith(supported_attachment_types):
                raise EmailAttachmentError(
                    "Unsupported attachment file type. Supported types: PDF, DOC, CSV, TXT, LOG, JPG, JPEG, PNG"
                )

    # MSAL configuration
    authority = f"https://login.microsoftonline.com/{email_tenantid}"
    scopes = ["https://graph.microsoft.com/.default"]

    # Create MSAL app
    app = msal.ConfidentialClientApplication(
        email_clientid, authority=authority, client_credential=email_secret
    )

    # Acquire token
    result = app.acquire_token_silent(scopes, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        access_token = result["access_token"]

        recipients = [{"emailAddress": {"address": email}} for email in emails]

        # Construct the email message
        email_msg = {
            "message": {
                "subject": subject,
                "body": {"contentType": "html", "content": message},
                "toRecipients": recipients,
                "attachments": [],
            },
            "saveToSentItems": "true",
        }

        # Add attachment if provided
        if attachments:
            for attachment in attachments:
                if not os.path.isfile(attachment):
                    raise EmailAttachmentError(
                        f"Attachment file {attachment} not found"
                    )
                try:
                    with open(attachment, "rb") as file:
                        attachment_content = file.read()
                        encoded_attachment = base64.b64encode(
                            attachment_content
                        ).decode("utf-8")
                        attachment_name = os.path.basename(attachment)
                        attachment_type = (
                            "application/octet-stream"  # Default MIME type
                        )

                        # Determine the MIME type based on the file extension
                        if attachment.endswith(".pdf"):
                            attachment_type = "application/pdf"
                        elif attachment.endswith(".doc"):
                            attachment_type = "application/msword"
                        elif attachment.endswith(".csv"):
                            attachment_type = "text/csv"
                        elif attachment.endswith(".txt"):
                            attachment_type = "text/plain"
                        elif attachment.endswith(".log"):
                            attachment_type = "text/plain"
                        elif attachment_type.endswith(
                            ".jpg"
                        ) or attachment_type.endswith(".jpeg"):
                            attachment_type = "image/jpeg"
                        elif attachment_type.endswith(".png"):
                            attachment_type = "image/png"

                        email_msg["message"]["attachments"].append(
                            {
                                "@odata.type": "#microsoft.graph.fileAttachment",
                                "name": attachment_name,
                                "contentType": attachment_type,
                                "contentBytes": encoded_attachment,
                            }
                        )
                except FileNotFoundError:
                    raise FileNotFoundError("Attachment file not found")

        # Send the email using Graph API
        graph_endpoint = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.post(graph_endpoint, headers=headers, json=email_msg)
        if response.status_code != 202:
            raise Exception(
                f"Failed to send email. Status code: {response.status_code}. Detail: {response.json()}"
            )
    else:
        raise Exception(
            f"Failed to acquire token for email \n{result.get('error')} \n{result.get('error_description')}"
        )


def send_teams_message(webhook_url: str, message: str) -> None:
    """
    Send a message to a Microsoft Teams channel using a webhook.

    Args:
        channel (str): The name of the channel as configured in teams_config.yml.
        message (str): The message text to send.

    Raises:
        TeamsMessageError: An error occurred while sending the Teams message. This is a custom exception
        that encapsulates various possible errors, including those related to webhook configuration and
        network issues.

    Usage:
        try:
            send_teams_message("general", "Hello, Teams!")
        except TeamsMessageError as e:
            print(f"Failed to send Teams message: {e}")
    """
    try:
        teams_message = pymsteams.connectorcard(webhook_url)
        teams_message.text(message)
        teams_message.send()

    except pymsteams.WebhookUrlError as e:
        raise TeamsMessageError(f"Error sending Teams message: {e}") from e

    except pymsteams.TeamsWebhookRequestError as e:
        raise TeamsMessageError(f"Error sending Teams message: {e}") from e

    except pymsteams.TeamsWebhookHTTPError as e:
        raise TeamsMessageError(f"Error sending Teams message: {e}") from e

    except pymsteams.TeamsWebhookValidationError as e:
        raise TeamsMessageError(f"Error sending Teams message: {e}") from e

    except pymsteams.TeamsWebhookProxyError as e:
        raise TeamsMessageError(f"Error sending Teams message: {e}") from e

    except Exception as e:
        raise TeamsMessageError(
            f"An unexpected error occurred while sending the Teams message: {e}"
        )
