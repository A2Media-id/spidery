from enum import Enum


class DeviceType(Enum):
    TABLET = 'tablet'
    SMARTPHONE = 'smartphone'
    UNKNOWN = 'unknown'
    DESKTOP = 'desktop'
    EMAIL_CLIENT = 'email-client'
    CRAWLER = 'crawler'
    BROWSER = 'browser'
    MOBILE_BROWSER = 'mobile-browser'
