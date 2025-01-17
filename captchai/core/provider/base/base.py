from abc import abstractmethod

from captchai.core.models.config import CaptchaGlobalConfig


class AbstractResolver:
    def __init__(self, config: CaptchaGlobalConfig):
        self.config = config

    @abstractmethod
    def solve(self, data: str, **kwargs): ...
