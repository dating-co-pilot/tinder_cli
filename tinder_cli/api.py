from typing import Literal, Dict, Optional
import requests
import json


class Defaults:
    APP_VERSION = "6.9.4"
    PLATFORM = "ios"
    USER_AGENT = "Tinder/7.5.3 (iPhone; iOS 10.3.2; Scale/2.00)"


class TinderSMSApiEndpoints:
    HOST = "https://api.gotinder.com"
    CODE_REQUEST_URL = f"{HOST}/v2/auth/sms/send?auth_type=sms"
    CODE_VALIDATE_URL = f"{HOST}/v2/auth/sms/validate?auth_type=sms"
    TOKEN_URL = f"{HOST}/v2/auth/login/sms"


class TinderSMSApi:
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
        self.auth_token = auth_token
        self.app_version = app_version
        self.platform = platform
        self.user_agent = user_agent

    @staticmethod
    def request_otp_sms(
        phone_number: int,  # with country code
        app_version: Optional[str] = Defaults.APP_VERSION,
        platform: Optional[str] = Defaults.PLATFORM,
        user_agent: Optional[str] = Defaults.USER_AGENT,
    ):
        """
        Requests an OTP (One Time Password) SMS to be sent to the given phone number.
        """
        return TinderSMSApi.general_request(
            url=TinderSMSApiEndpoints.CODE_REQUEST_URL,
            method="POST",
            headers=TinderSMSApi._get_headers(app_version, platform, user_agent),
            data={"phone_number": phone_number},
            err_msg="Failed to request OTP SMS",
            verify=False,
        )

    @staticmethod
    def get_refresh_token(
        otp_code: str,
        phone_number: int,
        app_version: Optional[str] = Defaults.APP_VERSION,
        platform: Optional[str] = Defaults.PLATFORM,
        user_agent: Optional[str] = Defaults.USER_AGENT,
    ) -> Optional[str]:
        """
        Returns the refresh token for the given the OTP which was requested by 'phone_number' using request_otp_sms.
        """
        response = TinderSMSApi.general_request(
            url=TinderSMSApiEndpoints.CODE_VALIDATE_URL,
            method="POST",
            headers=TinderSMSApi._get_headers(app_version, platform, user_agent),
            data={"otp_code": otp_code, "phone_number": phone_number},
            err_msg="Failed to validate OTP code",
            verify=False,
        )

        if response.get("data")["validated"] is False:
            return None
        else:
            return response.get("data")["refresh_token"]

    @staticmethod
    def get_api_token(
        refresh_token: str,
        app_version: Optional[str] = Defaults.APP_VERSION,
        platform: Optional[str] = Defaults.PLATFORM,
        user_agent: Optional[str] = Defaults.USER_AGENT,
    ):
        """
        Returns the API token for the user given the refresh token.
        """
        response = TinderSMSApi.general_request(
            TinderSMSApiEndpoints.TOKEN_URL,
            headers=TinderSMSApi._get_headers(app_version, platform, user_agent),
            data={"refresh_token": refresh_token},
            err_msg="Failed to get API token",
            method="POST",
            verify=False,
        )

        return response.get("data")["api_token"]

    @staticmethod
    def _get_headers(
        app_version: str, platform: str, user_agent: str
    ) -> Dict[str, str]:
        return {
            "app_version": app_version,
            "platform": platform,
            "content-type": "application/json",
            "User-agent": user_agent,
        }

    @staticmethod
    def general_request(
        url: str,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        err_msg: str,
        data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> Dict[str, str]:
        try:
            r = None
            data = json.dumps(data) if data else None
            if method == "POST":
                r = (requests.post(url, headers=headers, data=data, **kwargs),)
            elif method == "GET":
                r = requests.get(url, headers=headers, data=data, **kwargs)
            elif method == "PUT":
                r = requests.put(url, headers=headers, data=data, **kwargs)
            elif method == "DELETE":
                r = requests.delete(url, headers=headers, data=data, **kwargs)
            else:
                raise ValueError(f"Invalid method: {method}")
            return r.json()
        except requests.exceptions.RequestException as err:
            print(f"{err_msg}:", err)

    def basic_request(
        self,
        url: str,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        err_msg: str,
        data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        return self.general_request(url, method, err_msg, data, self.headers)

    @property
    def headers(self) -> Dict[str, str]:
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
        return self.basic_request(
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
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/updates",
            method="POST",
            err_msg="Something went wrong with getting updates",
            data={"last_activity_date": last_activity_date},
        )

    def get_self(self):
        """
        Returns your own profile data
        """
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/profile",
            method="GET",
            err_msg="Something went wrong with getting your data",
        )

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
        return self.basic_request(
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
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/meta",
            method="GET",
            err_msg="Something went wrong with getting your metadata",
        )

    def update_location(self, lat, lon):
        """
        Updates your location to the given float inputs
        Note: Requires a passport / Tinder Plus
        """
        self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/passport/user/travel",
            method="POST",
            err_msg="Something went wrong with updating your location",
            data={"lat": lat, "lon": lon},
        )

    def reset_real_location(self):
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/passport/user/reset",
            method="POST",
            err_msg="Something went wrong with resetting your location",
        )

    def get_recommendations_v2(self):
        """
        This works more consistently then the normal get_recommendations becuase it seeems to check new location
        """
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/v2/recs/core?locale=en-US",
            method="GET",
            err_msg="Something went wrong with getting recomendations",
        )

    def set_webprofileusername(self, username: str):
        """
        Sets the username for the webprofile: https://www.gotinder.com/@YOURUSERNAME
        """
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/profile/{username}",
            method="PUT",
            err_msg="Something went wrong with setting your webprofile username",
            data={"username": username},
        )

    def reset_webprofileusername(self, username: str):
        """
        Resets the username for the webprofile
        """
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/profile/{username}",
            method="DELETE",
            err_msg="Something went wrong with resetting your webprofile username",
        )

    def get_person(self, person_id: str):
        """
        Gets a user's profile via their id
        """
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/user/{person_id}",
            method="GET",
            err_msg="Something went wrong with getting that person",
        )

    def send_msg(self, match_id: str, msg: str):
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/user/matches/{match_id}",
            method="POST",
            err_msg="Something went wrong. Could not send your message",
            data={"message": msg},
        )

    def superlike(self, person_id: str):
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/like/{person_id}/super",
            method="POST",
            err_msg="Something went wrong. Could not superlike",
        )

    def like(self, person_id: str):
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/like/{person_id}",
            method="GET",
            err_msg="Something went wrong. Could not like",
        )

    def dislike(self, person_id: str):
        return self.basic_request(
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
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/report/{person_id}",
            method="POST",
            err_msg="Something went wrong. Could not report",
            data={"cause": cause, "text": explanation},
        )

    def match_info(self, match_id: str):
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/v2/matches/{match_id}?locale=en&is_tinder_u=false",
            method="GET",
            err_msg="Something went wrong. Could not get your match info",
        )

    def all_matches(self, limit: int = 60):
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/v2/matches?locale=en&count={limit}&is_tinder_u=false",
            method="GET",
            err_msg="Something went wrong. Could not get your match info",
        )

    def get_messages(self, match_id: str, limit: int = 60):
        return self.basic_request(
            f"{TinderSMSApiEndpoints.HOST}/v2/matches/{match_id}/messages?locale=en&count={limit}",
            method="GET",
            err_msg="Something went wrong. Could not get your match info",
        )
