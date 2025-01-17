from unittest.mock import Mock
from unittest.mock import patch

import pytest

from captchai.core.provider.aws.providers import RESOLVERS
from captchai.core.provider.aws.providers import AvailableResolvers
from captchai.core.provider.aws.providers import AWSProviderCaptcha
from captchai.core.models.config import AWSProviderConfig
from captchai.core.models.config import CaptchaGlobalConfig


@pytest.fixture
def mock_config():
    return CaptchaGlobalConfig(
        aws_provider_config=AWSProviderConfig(),
        groq_api_key="test-groq-api-key",
        moondream_api_key="test-moondream-api-key",
    )


class TestAWSProviderCaptcha:
    def test_solve_image(self, mock_config):
        # Arrange
        test_data = "test_data"
        test_query = "test_query"
        resolver = AvailableResolvers.GROQ_IMAGE_ONE_SHOOT
        mock_resolver_instance = Mock()
        mock_resolver_instance.solve.return_value = "expected_solution"

        with patch.dict(
            RESOLVERS, {resolver: Mock(return_value=mock_resolver_instance)}
        ):
            # Act
            provider = AWSProviderCaptcha(config=mock_config, resolver=resolver)
            result = provider.solve(test_data, query=test_query)

            # Assert
            assert result == "expected_solution"
            mock_resolver_instance.solve.assert_called_once_with(
                test_data, query=test_query
            )

    def test_solve_audio(self):
        # Arrange
        config = CaptchaGlobalConfig(
            aws_provider_config=AWSProviderConfig(),
            groq_api_key="test-groq-api-key",
            moondream_api_key="test-moondream-api-key",
        )
        resolver = AvailableResolvers.GROQ_AUDIO
        mock_resolver_instance = Mock()
        mock_resolver_instance.solve.return_value = "audio_solution"

        with patch.dict(
            RESOLVERS, {resolver: Mock(return_value=mock_resolver_instance)}
        ):
            # Act
            provider = AWSProviderCaptcha(config=config, resolver=resolver)
            result = provider.solve("audio_data")

            # Assert
            assert result == "audio_solution"
            mock_resolver_instance.solve.assert_called_once_with("audio_data", query="")
