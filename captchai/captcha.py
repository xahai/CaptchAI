from typing import TypeVar
from typing import Union

from captchai.core.models.config import AvailableResolvers
from captchai.core.models.config import CaptchaGlobalConfig
from captchai.core.models.config import CaptchaResponse
from captchai.core.provider.aws.providers import AWSProviderCaptcha


T = TypeVar("T", bound=Union[list[bool], str])


class CaptchaSolver:
    def __init__(self, config: CaptchaGlobalConfig):
        self.config = config

    def _create_aws_provider(
        self, config: CaptchaGlobalConfig, resolver: AvailableResolvers
    ):
        return AWSProviderCaptcha(config, resolver)

    def solve_aws_captcha_image(self, data: str, query: str) -> CaptchaResponse[T]:
        """Solve an AWS image captcha.

        Args:
            data: Base64 encoded string of the image data
            query: The type of object to look for in the image

        Returns:
            The captcha solution from the resolver
        """
        resolver: AWSProviderCaptcha = self._create_aws_provider(
            self.config, self.config.aws_provider_config.default_image_resolver
        )
        return resolver.solve(data, query=query)

    def solve_aws_captcha_audio(self, data: str) -> CaptchaResponse[T]:
        """Solve an AWS audio captcha.

        Args:
            data: Base64 encoded string of the audio data

        Returns:
            The captcha solution from the resolver
        """
        resolver: AWSProviderCaptcha = self._create_aws_provider(
            self.config, self.config.aws_provider_config.default_audio_resolver
        )
        return resolver.solve(data)
