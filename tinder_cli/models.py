from typing import List, Optional, Literal
from datetime import datetime
from dataclasses import dataclass


@dataclass
class AdditionalInfo:
    """
    Additional info about tinder user profile (non mandatory fields)
    """

    # looking for
    relationship_goals: Optional[
        Literal[
            "long-term partner",
            "long-term, but open to short-term",
            "short-term, but open to long",
            "short-term fun",
            "new friends",
            "still figuring it out",
        ]
    ] = None
    # passions
    passions: Optional[List[str]] = None  # maximum 5
    # languages
    languages: Optional[List[str]] = None  # maximum 5
    # basics
    zodiac_sign: Optional[str] = None
    education_level: Optional[
        Literal[
            "Bachelor degree",
            "At uni",
            "High school",
            "PhD",
            "On a graduate programme",
            "Master degree",
            "Trade school",
        ]
    ] = None
    children_attitude: Optional[
        Literal[
            "I want children",
            "I don't want children",
            "I have children and want more",
            "I have children and don't want more",
            "Not sure yet",
        ]
    ] = None
    vaccination_status: Optional[
        Literal["Vaccinated", "Unvaccinated", "Prefer not to say"]
    ] = None
    personality_type: Optional[
        Literal[
            "INTJ",
            "INTP",
            "ENTJ",
            "ENTP",
            "INFJ",
            "INFP",
            "ENFJ",
            "ENFP",
            "ISTJ",
            "ISFJ",
            "ESTJ",
            "ESFJ",
            "ISTP",
            "ISFP",
            "ESTP",
            "ESFP",
        ]
    ] = None
    communication_style: Optional[
        Literal[
            "Big time texter",
            "Phone caller",
            "Video chatter",
            "Bad texter",
            "Better in person",
        ]
    ] = None
    love_receive_language: Optional[
        Literal[
            "Thoughtful gestures", "Presents", "Touch", "Compliments", "Time together"
        ]
    ] = None
    # lifestyle
    pets: Optional[
        Literal[
            "Dog",
            "Cat",
            "Reptile",
            "Ampibian",
            "Bird",
            "Fish",
            "Dont't have, but love",
            "Other",
            "Turtle",
            "Hamster",
            "Rabbit",
            "Pet-free",
            "All the pets",
            "Want a pet",
            "Allergic to pets",
        ]
    ] = None
    drinking: Optional[
        Literal[
            "Not for me",
            "Newly teetotal",
            "Sober curious",
            "On special occasions",
            "Socially, at the weekend",
            "Most nights",
        ]
    ] = None
    smoking: Optional[
        Literal[
            "Social smoker",
            "Smoker when drinking",
            "Non-smoker",
            "Smoker",
            "Trying to quit",
        ]
    ] = None
    training_frequency: Optional[
        Literal["Every day", "Often", "Sometimes", "Never"]
    ] = None
    diet_preferences: Optional[
        Literal[
            "Vegan",
            "Vegetarian",
            "Pescatarian",
            "Kosher",
            "Halal",
            "Carnivore",
            "Omnivore",
            "Other",
        ]
    ] = None
    social_media_presence: Optional[
        Literal[
            "Influencer status", "Socially active", "Off the grid", "Passive scroller"
        ]
    ] = None
    sleeping_habits: Optional[
        Literal[
            "Early bird",
            "Night owl",
            "It varies",
        ]
    ] = None
    # work
    job_title: Optional[str] = None
    company: Optional[str] = None
    schools: Optional[List[str]] = None
    # location info
    location: Optional[str] = None  # usally city
    # gender
    gender: Optional[str] = None  # usually 'Man' or 'Woman'
    # orientation
    sexual_orientations: Optional[
        List[
            Literal[
                "Straight",
                "Gay",
                "Lesbian",
                "Bisexual",
                "Asexual",
                "Demisexual",
                "Pansexual",
                "Queer",
                "Questioning",
            ]
        ]
    ] = None  # max 3


@dataclass
class Profile:
    """
    Tinder user profile info
    """

    _id: str
    bio: str
    birth_date: datetime
    name: str
    photos: List[str]  # url to photo
    distance_mi: int
    additional: AdditionalInfo


@dataclass
class Message:
    """
    Tinder single message info
    """

    _id: str
    sent_date: datetime
    message: str
    to_id: str
    from_id: str
    match_id: str


@dataclass
class Match:
    """
    Tinder match info (profile_id + match_id)
    """

    match_id: str
    profile_id: str
