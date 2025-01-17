from enum import Enum
from typing import Generic
from typing import TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class AvailableResolvers(Enum):
    GROQ_IMAGE_ONE_SHOOT = "groq_image_one_shoot"
    GROQ_IMAGE_MULTI_SHOOT = "groq_image_multi_shoot"
    GROQ_AUDIO = "groq_audio"
    MOONDREAM_IMAGE_ONE_SHOOT = "moondream_image_one_shoot"
    MOONDREAM_IMAGE_MULTI_SHOOT = "moondream_image_multi_shoot"


class CaptchaResponse(BaseModel, Generic[T]):
    """Generic response wrapper for different captcha implementations."""

    response: T


class AWSProviderConfig(BaseModel):
    image_size: tuple[float, float] = (640, 640)
    grid_size: int = 3
    default_audio_resolver: AvailableResolvers = AvailableResolvers.GROQ_AUDIO
    default_image_resolver: AvailableResolvers = AvailableResolvers.GROQ_IMAGE_ONE_SHOOT
    list_resolver_image_fallback: list[AvailableResolvers] = [
        AvailableResolvers.MOONDREAM_IMAGE_ONE_SHOOT,
        AvailableResolvers.MOONDREAM_IMAGE_ONE_SHOOT,
        AvailableResolvers.GROQ_IMAGE_ONE_SHOOT,
        AvailableResolvers.GROQ_IMAGE_MULTI_SHOOT,
        AvailableResolvers.MOONDREAM_IMAGE_MULTI_SHOOT,
    ]
    list_resolver_audio_fallback: list[AvailableResolvers] = [
        AvailableResolvers.GROQ_AUDIO,
    ]


class CaptchaGlobalConfig(BaseModel):
    """Configuration for AWS Captcha Provider with API keys for different backends."""

    groq_api_key: str
    moondream_api_key: str
    aws_provider_config: AWSProviderConfig
