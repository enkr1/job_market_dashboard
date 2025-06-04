
from enum import Enum

class Country(Enum):
    SINGAPORE = "Singapore"
    REMOTE = "Remote"

class JobType(Enum):
    FULL_TIME = "Full-time"
    FREELANCE = "Freelance"

class Currency(Enum):
    SGD = "SGD"

class URL(Enum):
    TARGET = "https://www.techinasia.com/jobs/search"
    TECH_IN_ASIA = (
        f"{TARGET}"
        "?country_name[]=Singapore"
        "&country_name[]=Remote"
        "&job_type[]=Full-time"
        "&job_type[]=Freelance"
        "&currency=SGD"
    )

class CSSSelector(Enum):
    JOB_CARD = "article[data-cy='job-result']"
    TITLE_LINK = "a[data-cy='job-title']"
    COMPANY_LINK = ".details a[href^='/companies']"
    LOCATION_DIV = ".details > div:nth-child(3)"
    AVATAR_IMG = ".avatar img"
    COMPENSATION = ".compensation"
    PUBLISHED_DATE = ".published-at"
    METADATA = ".additional-meta"
