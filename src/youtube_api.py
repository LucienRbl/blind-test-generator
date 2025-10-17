import http.client
import httplib2
import random
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine,
)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


class YouTubeAPI:
    """Class to interact with YouTube Data API for video uploads and management"""

    def __init__(
        self,
        client_secrets_file: str,
        api_service_name: str = "youtube",
        api_version: str = "v3",
        scopes: list = None,
    ):
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.client_secrets_file = client_secrets_file
        self.api_service_name = api_service_name
        self.api_version = api_version
        self.scopes = scopes
        self.youtube = self.get_authenticated_service()

    def get_authenticated_service(self):
        flow = flow_from_clientsecrets(self.client_secrets_file, scope=self.scopes)
        storage = Storage("youtube-oauth2.json")
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage)

        return build(self.api_service_name, self.api_version, credentials=credentials)

    def initialize_upload(self, options):
        body = {
            "snippet": {
                "title": options["title"],
                "description": options["description"],
                "tags": options["tags"],
                "categoryId": options["category"],
            },
            "status": {"privacyStatus": options["privacyStatus"]},
        }

        insert_request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(options["file"], chunksize=-1, resumable=True),
        )

        self.resumable_upload(insert_request)

    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0

        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if "id" in response:
                        print(f"The video was successfully uploaded at https://youtu.be/{response['id']}")
                    else:
                        print(
                            f"The upload failed with an unexpected response: {response}"
                        )
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = (
                        f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                    )
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    print("No longer attempting to retry.")
                    break

                max_sleep = 2**retry
                sleep_seconds = random.random() * max_sleep
                print(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)
                error = None

    def upload_video(
        self,
        file: str,
        title: str,
        description: str,
        category: str = "22",
        privacyStatus: str = "public",
        tags: list[str] = None,
    ):
        """
        Upload a video to YouTube

        Args:
            file: Path to the video file
            title: Title of the video
            description: Description of the video
            category: Category ID for the video
            tags: Comma-separated tags for the video
            privacyStatus: Privacy status of the video (public, unlisted, private)
        """
        options = {
            "file": file,
            "title": title,
            "description": description,
            "category": category,
            "tags": tags,
            "privacyStatus": privacyStatus,
        }
        self.initialize_upload(options)


if __name__ == "__main__":
    argparser.add_argument("--file", required=True, help="Video file to upload")
    argparser.add_argument("--title", help="Video title", default="Test Title")
    argparser.add_argument(
        "--description", help="Video description", default="Test Description"
    )
    argparser.add_argument(
        "--category",
        default="22",
        help="Numeric video category. See https://developers.google.com/youtube/v3/docs/videoCategories/list",
    )
    argparser.add_argument(
        "--keywords", help="Video keywords, comma separated", default=""
    )
    argparser.add_argument(
        "--privacyStatus",
        choices=["public", "private", "unlisted"],
        default="public",
        help="Video privacy status.",
    )

    args = argparser.parse_args()

    youtube_api = YouTubeAPI(client_secrets_file="client_secret.json")
    youtube_api.upload_video(
        file=args.file,
        title=args.title,
        description=args.description,
        category=args.category,
        keywords=args.keywords,
        privacyStatus=args.privacyStatus,
    )
