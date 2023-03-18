from typing import List, NamedTuple, Optional, Literal
from datetime import datetime


class AdditionalInfo(NamedTuple):
    """
    Additional info about tinder user profile (non mandatory fields)
    """

    # looking for
    relationsip_goals: Optional[
        Literal[
            "long-term partner",
            "long-term, but open to short-term",
            "short-term, but open to long",
            "short-term fun",
            "new friends",
            "still figuring it out",
        ]
    ]
    # passions
    passions: Optional[List[str]]  # maximum 5
    # languages
    languages: Optional[List[str]]  # maximum 5
    # basics
    zodiac_sign: Optional[str]
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
    ]
    children_attitude: Optional[
        Literal[
            "I want children",
            "I don't want children",
            "I have children and want more",
            "I have children and don't want more",
            "Not sure yet",
        ]
    ]
    vaccination_status: Optional[
        Literal["Vaccinated", "Unvaccinated", "Prefer not to say"]
    ]
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
    ]
    communication_style: Optional[
        Literal[
            "Big time texter",
            "Phone caller",
            "Video chatter",
            "Bad texter",
            "Better in person",
        ]
    ]
    love_receive_language: Optional[
        Literal[
            "Thoughtful gestures", "Presents", "Touch", "Compliments", "Time together"
        ]
    ]
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
    ]
    drinking: Optional[
        Literal[
            "Not for me",
            "Newly teetotal",
            "Sober curious",
            "On special occasions",
            "Socially, at the weekend",
            "Most nights",
        ]
    ]
    smoking: Optional[
        Literal[
            "Social smoker",
            "Smoker when drinking",
            "Non-smoker",
            "Smoker",
            "Trying to quit",
        ]
    ]
    training_frequency: Optional[Literal["Every day", "Often", "Sometimes", "Never"]]
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
    ]
    social_media_presence: Optional[
        Literal[
            "Influencer status", "Socially active", "Off the grid", "Passive scroller"
        ]
    ]
    sleeping_habits: Optional[
        Literal[
            "Early bird",
            "Night owl",
            "It varies",
        ]
    ]
    # work
    job_title: Optional[str]
    company: Optional[str]
    school: Optional[str]
    # living info
    location: Optional[str]  # usally city, state
    # gender
    gender: Optional[str]  # usually 'Man' or 'Woman'
    # orientation
    sexual_orientation: Optional[
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
    ]  # max 3


class Profile(NamedTuple):
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


class Message(NamedTuple):
    """
    Tinder single message info
    """

    _id: str
    sent_date: datetime
    message: str
    to: str
    from_: str
    match_id: str


class Match(NamedTuple):
    """
    Tinder match info (profile + messages + match id)
    """

    _id: str
    profile: Profile
    messages: List[Message]
