from tinder_cli.models import Profile, AdditionalInfo, Match, Message
from typing import Dict, Tuple, List, Optional, Any
import logging
from datetime import datetime


logger = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


def match_additional_info_attr_name(
    descriptor_section: str, descriptor_name: str
) -> Tuple[str, bool]:
    """
    str: Return attribute name for AdditionalInfo class based on descriptor section and name
    bools: returns if attribute is multicategorcial or not (True if multicategorcial)
    """

    def raise_err():
        raise ValueError(
            f"Unknown descriptor section and name: {descriptor_section} {descriptor_name}"
        )

    match (descriptor_section, descriptor_name):
        case ("Basics", _):
            match (descriptor_name):
                case ("Zodiac"):
                    return "zodiac_sign", False
                case ("Education"):
                    return "education_level", False
                case ("Family Plans"):
                    return "children_attitude", False
                case ("COVID Vaccine"):
                    return "covid_vaccine", False
                case ("Personality Type"):
                    return "personality_type", False
                case ("Communication Style"):
                    return "communication_style", False
                case ("Love Style"):
                    return "love_receive_language", False
                case _:
                    raise_err()
        case ("Lifestyle", _):
            match (descriptor_name):
                case ("Pets"):
                    return "pets", False
                case ("Drinking"):
                    return "drinking", False
                case ("Smoking"):
                    return "smoking", False
                case ("Workout"):
                    return "training_frequency", False
                case ("Dietary Preference"):
                    return "diet_preferences", False
                case ("Social Media"):
                    return "social_media_presence", False
                case ("Sleeping Habits"):
                    return "sleeping_habits", False
                case _:
                    raise_err()
        case ("Relationship Goals", "Looking for"):
            return "relationship_goals", False
        case ("Lifestyle", "Pets"):
            return "pets", False
        case ("Languages I Know", None):
            return "languages", True
        case _:
            raise_err()


def parse_gender(result: Dict[str, Any]) -> Optional[str]:
    """
    Returns name of gender from numerical value, returns none if not shown on profile
    """

    # if gender not shown on profile, we dont know in what gender is user interested nor their gender identity
    if result["show_gender_on_profile"] is False:
        return None

    if "custom_gender" in result:
        return result["custom_gender"]

    match result["gender"]:
        case 0:
            return "Man"
        case 1:
            return "Woman"
        case _:
            # this branch should never be reached
            return None


def parse_profile_response(rsp: Dict[str, Any]) -> Profile:
    """
    Parse profile response from Tinder API
    """

    result = rsp["results"]

    additional_info = AdditionalInfo()
    # parse schools
    if len(result["schools"]) > 0:
        additional_info.schools = [school["name"] for school in result["schools"]]
    # parse passions / interests
    if len(result["user_interests"]["selected_interests"]) > 0:
        additional_info.passions = [
            passion["name"]
            for passion in result["user_interests"]["selected_interests"]
        ]
    # add job title if exists (not sure if there can be more than one job possible)
    if len(result["jobs"]) > 0:
        job = result["jobs"][0]
        if "title" in job:
            additional_info.job_title = job["title"]["name"]
        if "company" in job:
            additional_info.company = job["company"]["name"]

    # parse location (usually city)
    if "city" in result:
        additional_info.location = result["city"]["name"]

    # parse gender
    additional_info.gender = parse_gender(result)
    # parse sexual orientations
    if "sexual_orientations" in result:
        additional_info.sexual_orientations = [
            orientation["name"] for orientation in result["sexual_orientations"]
        ]

    # parse additional features from "selected_descriptors" category
    for descriptor in result["selected_descriptors"]:
        attr_name, is_multisel = match_additional_info_attr_name(
            descriptor["section_name"], descriptor.get("name")
        )
        value = [desc["name"] for desc in descriptor["choice_selections"]]
        if is_multisel is False:
            value = value[0]
        setattr(additional_info, attr_name, value)

    # parse photos ignoring videos
    photos = []
    for photo in result["photos"]:
        if photo["url"].endswith(".webp"):
            continue
        photos.append(photo["url"])

    # load mandatory fields
    return Profile(
        _id=result["_id"],
        bio=result["bio"],
        birth_date=datetime.strptime(result["birth_date"], DATETIME_FORMAT),
        name=result["name"],
        photos=photos,
        distance_mi=result["distance_mi"],
        additional=additional_info,
    )


def parse_matches(rsp: Dict[str, Any]) -> Tuple[List[Match], Optional[str]]:
    """
    Extract match ids from match response
    Additionally returns next page token for paginiation if there are more matches
    """

    next_page_token: Optional[str] = rsp["data"].get("next_page_token")
    matches: List[Match] = []

    for match in rsp["data"]["matches"]:
        m = Match(
            match_id=match["_id"],
            profile_id=match["person"]["_id"],
        )
        matches.append(m)

    return matches, next_page_token


def parse_messages(rsp: Dict[str, Any]) -> Tuple[List[Message], Optional[str]]:
    """
    Extract messages from message response
    Additionally returns next page token for paginiation if there are more messages
    """

    next_page_token: Optional[str] = rsp["data"].get("next_page_token")
    messages: List[Message] = []

    for message in rsp["data"]["messages"]:
        m = Message(
            _id=message["_id"],
            match_id=message["match_id"],
            message=message["message"],
            sent_date=datetime.strptime(message["sent_date"], DATETIME_FORMAT),
            from_id=message["from"],
            to_id=message["to"],
        )
        messages.append(m)

    return messages, next_page_token
