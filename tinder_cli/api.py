from typing import Literal, Dict, Optional, List, Tuple
from .parse_utils import parse_profile_response, parse_matches, parse_messages
from .models import Profile, Match, Message
import requests
import json
import logging


logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s : %(levelname)s : %(message)s"
)
logger = logging.getLogger(__name__)


class Defaults:
    APP_VERSION = "6.9.4"
    PLATFORM = "ios"
    USER_AGENT = "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)"


class TinderSMSApiEndpoints:
    HOST = "https://api.gotinder.com"
    CODE_REQUEST_URL = f"{HOST}/v2/auth/sms/send?auth_type=sms"
    CODE_VALIDATE_URL = f"{HOST}/v2/auth/sms/validate?auth_type=sms"
    TOKEN_URL = f"{HOST}/v2/auth/login/sms"


class BaseTinderClient:
    app_version: str
    platform: str
    user_agent: str

    def __init__(
        self,
        app_version: str = Defaults.APP_VERSION,
        platform: str = Defaults.PLATFORM,
        user_agent: str = Defaults.USER_AGENT,
    ) -> None:
        self.app_version = app_version
        self.platform = platform
        self.user_agent = user_agent

    def get_headers(self) -> Dict[str, str]:
        """
        Returns the headers for the Tinder API
        """
        return {
            "app_version": self.app_version,
            "platform": self.platform,
            "content-type": "application/json",
            "User-agent": self.user_agent,
        }

    def general_request(
        self,
        url: str,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        err_msg: str,
        data: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, str]:
        """
        Handles general request to the Tinder API
        """
        try:
            data = json.dumps(data) if data else None
            req_collable = getattr(requests, method.lower())
            rsp = req_collable(url, headers=self.get_headers(), data=data, **kwargs)
            return rsp.json()
        except requests.exceptions.RequestException as err:
            logger.error("%s:\n %s", err_msg, err)


class TinderSMSAuth(BaseTinderClient):
    """
    Handles the SMS authentication flow
    """

    phone_number: str
    app_version: str
    platform: str
    user_agent: str
    refresh_token: Optional[str]

    def __init__(
        self,
        phone_number: int,
        app_version: Optional[str] = Defaults.APP_VERSION,
        platform: Optional[str] = Defaults.PLATFORM,
        user_agent: Optional[str] = Defaults.USER_AGENT,
    ):
        super().__init__(app_version, platform, user_agent)
        self.phone_number = phone_number

    def request_otp_sms(self) -> Dict[str, str]:
        """
        Requests an OTP (One Time Password) SMS to be sent to the given phone number.
        """
        return self.general_request(
            url=TinderSMSApiEndpoints.CODE_REQUEST_URL,
            method="POST",
            data={"phone_number": self.phone_number},
            err_msg="Failed to request OTP SMS",
            verify=False,
        )

    def get_refresh_token(self, otp_code: str):
        """
        Retrieves the refresh token from the server.
        """

        rsp = self.general_request(
            url=TinderSMSApiEndpoints.CODE_VALIDATE_URL,
            method="POST",
            data={"otp_code": otp_code, "phone_number": self.phone_number},
            err_msg="Failed to get refresh token",
            verify=False,
        )

        if rsp.get("data")["validated"] is False:
            raise ValueError("OTP code is not valid")
        self.refresh_token = rsp.get("data")["refresh_token"]

    def get_auth_token(self) -> str:
        """
        Retrieves the auth token from the server.
        """
        if self.refresh_token is None:
            raise ValueError("Refresh token is not obtained yet")
        rsp = self.general_request(
            TinderSMSApiEndpoints.TOKEN_URL,
            data={"refresh_token": self.refresh_token},
            err_msg="Failed to get API auth token",
            method="POST",
            verify=False,
        )
        return rsp["data"]["api_token"]


class TinderFBAuth(BaseTinderClient):
    


class TinderClient(BaseTinderClient):
    auth_token: str
    app_version: str
    platform: str
    user_agent: str

    def __init__(
        self,
        auth_token: str,
        app_version: Optional[str] = Defaults.APP_VERSION,
        platform: Optional[str] = Defaults.PLATFORM,
        user_agent: Optional[str] = Defaults.USER_AGENT,
    ):
        super().__init__(app_version, platform, user_agent)
        self.auth_token = auth_token

    def get_headers(self) -> Dict[str, str]:
        return {
            "app_version": self.app_version,
            "platform": self.platform,
            "content-type": "application/json",
            "User-agent": self.user_agent,
            "X-Auth-Token": self.auth_token,
        }

    def get_recommendations(self):
        """
        Returns a list of users that you can swipe on
        """
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/users/recs",
            method="GET",
            err_msg="Something went wrong with getting recomendations",
        )

    def get_updates(self, last_activity_date=""):
        """
        Returns all updates since the given activity date.
        The last activity date is defaulted at the beginning of time.
        Format for last_activity_date: "2017-07-09T10:28:13.392Z"
        """
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/updates",
            method="POST",
            err_msg="Something went wrong with getting updates",
            data={"last_activity_date": last_activity_date},
        )

    def get_self(self):
        """
        Returns your own profile data
        """
        res = self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/profile",
            method="GET",
            err_msg="Something went wrong with getting your data",
        )
        return res

    def change_preferences(self, **kwargs):
        """
        ex: change_preferences(age_filter_min=30, gender=0)
        kwargs: a dictionary - whose keys become separate keyword arguments and the values become values of these arguments
        age_filter_min: 18..46
        age_filter_max: 22..55
        age_filter_min <= age_filter_max - 4
        gender: 0 == seeking males, 1 == seeking females
        distance_filter: 1..100
        discoverable: true | false
        {"photo_optimizer_enabled":false}
        """
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/profile",
            method="POST",
            err_msg="Something went wrong with changing your preferences",
            data=kwargs,
        )

    def get_meta(self):
        """
        Returns meta data on yourself. Including the following keys:
        ['globals', 'client_resources', 'versions', 'purchases',
        'status', 'groups', 'products', 'rating', 'tutorials',
        'travel', 'notifications', 'user']
        """
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/meta",
            method="GET",
            err_msg="Something went wrong with getting your metadata",
        )

    def update_location(self, lat, lon):
        """
        Updates your location to the given float inputs
        Note: Requires a passport / Tinder Plus
        """
        self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/passport/user/travel",
            method="POST",
            err_msg="Something went wrong with updating your location",
            data={"lat": lat, "lon": lon},
        )

    def reset_real_location(self):
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/passport/user/reset",
            method="POST",
            err_msg="Something went wrong with resetting your location",
        )

    def get_recommendations_v2(self):
        """
        This works more consistently then the normal get_recommendations becuase it seeems to check new location
        """
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/v2/recs/core?locale=en-US",
            method="GET",
            err_msg="Something went wrong with getting recomendations",
        )

    def set_webprofileusername(self, username: str):
        """
        Sets the username for the webprofile: https://www.gotinder.com/@YOURUSERNAME
        """
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/profile/{username}",
            method="PUT",
            err_msg="Something went wrong with setting your webprofile username",
            data={"username": username},
        )

    def reset_webprofileusername(self, username: str):
        """
        Resets the username for the webprofile
        """
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/profile/{username}",
            method="DELETE",
            err_msg="Something went wrong with resetting your webprofile username",
        )

    def get_profile(self, person_id: str) -> Profile:
        """
        Gets a user's profile via their id
        """
        res = self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/user/{person_id}",
            method="GET",
            err_msg="Something went wrong with getting that person",
        )
        return parse_profile_response(res)

    def send_msg(self, match_id: str, msg: str):
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/user/matches/{match_id}",
            method="POST",
            err_msg="Something went wrong. Could not send your message",
            data={"message": msg},
        )

    def superlike(self, person_id: str):
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/like/{person_id}/super",
            method="POST",
            err_msg="Something went wrong. Could not superlike",
        )

    def like(self, person_id: str):
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/like/{person_id}",
            method="GET",
            err_msg="Something went wrong. Could not like",
        )

    def dislike(self, person_id: str):
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/pass/{person_id}",
            method="GET",
            err_msg="Something went wrong. Could not dislike",
        )

    def report(self, person_id: str, cause: Literal[0, 1, 4], explanation: str):
        """
        There are three options for cause:
            0 : Other and requires an explanation
            1 : Feels like spam and no explanation
            4 : Inappropriate Photos and no explanation
        """
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/report/{person_id}",
            method="POST",
            err_msg="Something went wrong. Could not report",
            data={"cause": cause, "text": explanation},
        )

    def match_info(self, match_id: str):
        return self.general_request(
            f"{TinderSMSApiEndpoints.HOST}/v2/matches/{match_id}?locale=en&is_tinder_u=false",
            method="GET",
            err_msg="Something went wrong. Could not get your match info",
        )

    def get_matches(
        self, limit: int = 60, next_page_token: Optional[str] = None
    ) -> Tuple[List[Match], Optional[str]]:
        """
        Returns a list of matches and the next page token if there is one
        """
        url = f"{TinderSMSApiEndpoints.HOST}/v2/matches?locale=en&count={limit}&is_tinder_u=false"
        if next_page_token is not None:
            url += f"&page_token={next_page_token}"

        res = self.general_request(
            url,
            method="GET",
            err_msg="Something went wrong. Could not get your match info",
        )
        return parse_matches(res)

    def get_messages(
        self, match_id: str, limit: int = 60, next_page_token: Optional[str] = None
    ) -> Tuple[List[Message], Optional[str]]:
        """
        Returns a list of messages and the next page token if there is one
        """
        url = f"{TinderSMSApiEndpoints.HOST}/v2/matches/{match_id}/messages?locale=en&count={limit}"
        if next_page_token is not None:
            url += f"&page_token={next_page_token}"

        res = self.general_request(
            url,
            method="GET",
            err_msg="Something went wrong. Could not get your match info",
        )
        return parse_messages(res)
