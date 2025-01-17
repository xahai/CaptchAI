from captchai.core.models.config import AvailableResolvers
from captchai.core.models.config import CaptchaGlobalConfig
from captchai.core.provider.aws.resolvers import AWSAudioResolverGroqBackend
from captchai.core.provider.aws.resolvers import AWSImageResolverMultiShootGroqBackend
from captchai.core.provider.aws.resolvers import (
    AWSImageResolverMultiShootMoonDreamBackend,
)
from captchai.core.provider.aws.resolvers import AWSImageResolverOneShootGroqBackend
from captchai.core.provider.aws.resolvers import (
    AWSImageResolverOneShootMoonDreamBackend,
)


RESOLVERS = {
    AvailableResolvers.GROQ_AUDIO: AWSAudioResolverGroqBackend,
    AvailableResolvers.MOONDREAM_IMAGE_ONE_SHOOT: (
        AWSImageResolverOneShootMoonDreamBackend
    ),
    AvailableResolvers.GROQ_IMAGE_ONE_SHOOT: (AWSImageResolverOneShootGroqBackend),
    AvailableResolvers.GROQ_IMAGE_MULTI_SHOOT: (AWSImageResolverMultiShootGroqBackend),
    AvailableResolvers.MOONDREAM_IMAGE_MULTI_SHOOT: (
        AWSImageResolverMultiShootMoonDreamBackend
    ),
}


class AWSProviderCaptcha:
    def _initialize_type(
        self, config: CaptchaGlobalConfig, resolver: AvailableResolvers
    ):
        return RESOLVERS[resolver](config=config)

    def __init__(self, config: CaptchaGlobalConfig, resolver: AvailableResolvers):
        self._config = config
        self._resolver = resolver

    def solve(self, data: str, query: str = ""):
        resolver = self._initialize_type(self._config, self._resolver)
        return resolver.solve(data, query=query)
