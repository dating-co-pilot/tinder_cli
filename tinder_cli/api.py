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
        phone_number: int,
        app_version: Optional[str] = Defaults.APP_VERSION,
        platform: Optional[str] = Defaults.PLATFORM,
        user_agent: Optional[str] = Defaults.USER_AGENT,
    ):
        data = {"phone_number": phone_number}
        r = requests.post(
            TinderSMSApiEndpoints.CODE_REQUEST_URL,
            headers=TinderSMSApi._get_headers(app_version, platform, user_agent),
            data=json.dumps(data),
            verify=False,
        )
        response = r.json()
        if response.get("data")["sms_sent"] is False:
            return False
        else:
            return True

    @staticmethod
    def get_refresh_token(
        otp_code: str,
        phone_number: int,
        app_version: Optional[str] = Defaults.APP_VERSION,
        platform: Optional[str] = Defaults.PLATFORM,
        user_agent: Optional[str] = Defaults.USER_AGENT,
    ) -> Optional[str]:
        data = {"otp_code": otp_code, "phone_number": phone_number}
        r = requests.post(
            TinderSMSApiEndpoints.CODE_VALIDATE_URL,
            headers=TinderSMSApi._get_headers(app_version, platform, user_agent),
            data=json.dumps(data),
            verify=False,
        )
        response = r.json()
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
        data = {"refresh_token": refresh_token}
        r = requests.post(
            TinderSMSApiEndpoints.TOKEN_URL,
            headers=TinderSMSApi._get_headers(app_version, platform, user_agent),
            data=json.dumps(data),
            verify=False,
        )
        print(r.url)
        response = r.json()
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

        try:
            r = requests.get("https://api.gotinder.com/user/recs", headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong with getting recomendations:", err)

    def get_updates(self, last_activity_date=""):
        """
        Returns all updates since the given activity date.
        The last activity date is defaulted at the beginning of time.
        Format for last_activity_date: "2017-07-09T10:28:13.392Z"
        """
        try:
            url = TinderSMSApiEndpoints.HOST + "/updates"
            r = requests.post(
                url,
                headers=self.headers,
                data=json.dumps({"last_activity_date": last_activity_date}),
            )
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong with getting updates:", err)

    def get_self(self):
        """
        Returns your own profile data
        """
        try:
            url = TinderSMSApiEndpoints.HOST + "/profile"
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not get your data:", err)

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
        try:
            url = TinderSMSApiEndpoints.HOST + "/profile"
            r = requests.post(url, headers=self.headers, data=json.dumps(kwargs))
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not change your preferences:", err)

    def get_meta(self):
        """
        Returns meta data on yourself. Including the following keys:
        ['globals', 'client_resources', 'versions', 'purchases',
        'status', 'groups', 'products', 'rating', 'tutorials',
        'travel', 'notifications', 'user']
        """
        try:
            url = TinderSMSApiEndpoints.HOST + "/meta"
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not get your metadata:", err)

    def update_location(self, lat, lon):
        """
        Updates your location to the given float inputs
        Note: Requires a passport / Tinder Plus
        """
        try:
            url = TinderSMSApiEndpoints.HOST + "/passport/user/travel"
            r = requests.post(
                url,
                headers=self.headers,
                data=json.dumps({"lat": lat, "lon": lon}),
            )
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not update your location:", err)

    def reset_real_location(self):
        try:
            url = TinderSMSApiEndpoints.HOST + "/passport/user/reset"
            r = requests.post(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not update your location:", err)

    def get_recommendations_v2(self):
        """
        This works more consistently then the normal get_recommendations becuase it seeems to check new location
        """
        try:
            url = TinderSMSApiEndpoints.HOST + "/v2/recs/core?locale=en-US"
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not get recommendations:", err)

    def set_webprofileusername(self, username: str):
        """
        Sets the username for the webprofile: https://www.gotinder.com/@YOURUSERNAME
        """
        try:
            url = TinderSMSApiEndpoints.HOST + "/profile/username"
            r = requests.put(
                url,
                headers=self.headers,
                data=json.dumps({"username": username}),
            )
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not set webprofile username:", err)

    def reset_webprofileusername(self, username: str):
        """
        Resets the username for the webprofile
        """
        try:
            url = TinderSMSApiEndpoints.HOST + "/profile/username"
            r = requests.delete(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not delete webprofile username:", err)

    def get_person(self, person_id: str):
        """
        Gets a user's profile via their id
        """
        try:
            url = TinderSMSApiEndpoints.HOST + f"/user/{person_id}"
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not get that person:", err)

    def send_msg(self, match_id: str, msg: str):
        try:
            url = TinderSMSApiEndpoints.HOST + f"/user/matches/{match_id}"
            r = requests.post(
                url, headers=self.headers, data=json.dumps({"message": msg})
            )
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not send your message:", err)

    def superlike(self, person_id: str):
        try:
            url = TinderSMSApiEndpoints.HOST + f"/like/{person_id}/super"
            r = requests.post(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not superlike:", err)

    def like(self, person_id: str):
        try:
            url = TinderSMSApiEndpoints.HOST + f"/like/{person_id}"
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not like:", err)

    def dislike(self, person_id: str):
        try:
            url = TinderSMSApiEndpoints.HOST + f"/pass/{person_id}"
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not dislike:", err)

    def report(self, person_id: str, cause: Literal[0, 1, 4], explanation: str):
        """
        There are three options for cause:
            0 : Other and requires an explanation
            1 : Feels like spam and no explanation
            4 : Inappropriate Photos and no explanation
        """
        try:
            url = TinderSMSApiEndpoints.HOST + f"/report/{person_id}"
            r = requests.post(
                url,
                headers=self.headers,
                data={"cause": cause, "text": explanation},
            )
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not report:", err)

    def match_info(self, match_id: str):
        try:
            url = TinderSMSApiEndpoints.HOST + f"/matches/{match_id}"
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not get your match info:", err)

    def all_matches(self):
        try:
            url = TinderSMSApiEndpoints.HOST + "/v2/matches"
            r = requests.get(url, headers=self.headers)
            return r.json()
        except requests.exceptions.RequestException as err:
            print("Something went wrong. Could not get your match info:", err)
