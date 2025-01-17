import base64
import json
import os

from pathlib import Path
from time import sleep

import pytest

from dotenv import load_dotenv

from captchai.core.models.config import AWSProviderConfig
from captchai.core.models.config import CaptchaGlobalConfig
from captchai.core.provider.aws.resolvers import AudioTranscriptionError
from captchai.core.provider.aws.resolvers import AWSAudioResolverGroqBackend
from captchai.core.provider.aws.resolvers import AWSImageResolverMultiShootGroqBackend
from captchai.core.provider.aws.resolvers import (
    AWSImageResolverMultiShootMoonDreamBackend,
)
from captchai.core.provider.aws.resolvers import AWSImageResolverOneShootGroqBackend
from captchai.core.provider.aws.resolvers import (
    AWSImageResolverOneShootMoonDreamBackend,
)


load_dotenv()


def load_audio_test_cases():
    test_cases = []
    resources_dir = Path(__file__).parent.parent.parent / "audio_captchas_resources"

    for captcha_dir in sorted(resources_dir.glob("captcha-*")):
        if not captcha_dir.is_dir():
            continue

        audio_path = captcha_dir / "audio.flac"
        solution_path = captcha_dir / "solution.json"

        if not audio_path.exists() or not solution_path.exists():
            continue

        with open(audio_path, "rb") as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode("utf-8")

        with open(solution_path) as solution_file:
            expected_solution = json.load(solution_file)

        test_cases.append(
            pytest.param(audio_data, expected_solution["words"], id=captcha_dir.name)
        )

    return test_cases


def load_image_test_cases(type_of_match: str):
    test_cases = []
    resources_dir = Path(__file__).parent.parent.parent / "visual_captchas_resources"

    for captcha_dir in sorted(resources_dir.glob("captcha-*")):
        if not captcha_dir.is_dir():
            continue

        image_path = captcha_dir / "image.png"
        solution_path = captcha_dir / "solution.json"

        if not image_path.exists() or not solution_path.exists():
            continue

        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        with open(solution_path) as solution_file:
            expected_solution = json.load(solution_file)

        test_cases.append(
            pytest.param(
                image_data,
                expected_solution["matrix"],
                expected_solution["query"],
                expected_solution[type_of_match],
                id=captcha_dir.name,
            )
        )

    return test_cases


# Add a fixture for the config that uses environment variables
@pytest.fixture
def test_config():
    return CaptchaGlobalConfig(
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        moondream_api_key=os.getenv("MOONDREAM_API_KEY", ""),
        aws_provider_config=AWSProviderConfig(),
    )


@pytest.mark.parametrize("audio_data,expected_solution", load_audio_test_cases())
def test_aws_groq_audio_resolver(
    test_config, audio_data: str, expected_solution: list[str]
):
    sleep(15)
    resolver = AWSAudioResolverGroqBackend(test_config)
    result = resolver.solve(audio_data)

    assert result.response == expected_solution, (
        f"Expected {expected_solution}, but got {result.response}"
    )


def test_aws_audio_groq_resolver_with_convertion(test_config):
    resources_dir = Path(__file__).parent.parent.parent / "audio_captchas_resources"
    audio_path = resources_dir / "to-convert-captcha" / "audio.mpeg"
    solution_path = resources_dir / "to-convert-captcha" / "solution.json"

    with open(solution_path) as solution_file:
        expected_solution = json.load(solution_file)

    with open(audio_path, "rb") as audio_file:
        audio_data = base64.b64encode(audio_file.read()).decode("utf-8")

    resolver = AWSAudioResolverGroqBackend(test_config)
    result = resolver.solve(audio_data)

    assert result.response == expected_solution["words"], (
        f"Expected {expected_solution}, but got {result.response}"
    )


def test_aws_audio_groq_resolver_with_convertion_error(test_config):
    resources_dir = Path(__file__).parent.parent.parent / "audio_captchas_resources"
    audio_path = resources_dir / "error-captcha" / "audio.flac"

    with open(audio_path, "rb") as audio_file:
        audio_data = base64.b64encode(audio_file.read()).decode("utf-8")

    resolver = AWSAudioResolverGroqBackend(test_config)

    with pytest.raises(
        AudioTranscriptionError, match="Failed to parse audio transcription"
    ):
        resolver.solve(audio_data)


@pytest.mark.parametrize(
    "image_data,expected_solution,expected_query,groq_match",
    load_image_test_cases("groq_match"),
)
def test_aws_image_groq_resolver(
    test_config,
    image_data: str,
    expected_solution: list[bool],
    expected_query: str,
    groq_match: bool,
):
    sleep(15)
    resolver = AWSImageResolverOneShootGroqBackend(test_config)
    result = resolver.solve(image_data, query=expected_query)

    evaluation_groq = result.response == expected_solution

    assert result.response == expected_solution or evaluation_groq == groq_match, (
        f"Expected {expected_solution}, but got {result.response}"
    )


@pytest.mark.parametrize(
    "image_data,expected_solution,expected_query,moondream_match",
    load_image_test_cases("moondream_match"),
)
def test_aws_moondream_image_resolver(
    test_config,
    image_data: str,
    expected_solution: list[bool],
    expected_query: str,
    moondream_match: bool,
):
    sleep(15)
    resolver = AWSImageResolverOneShootMoonDreamBackend(test_config)
    result = resolver.solve(image_data, query=expected_query)

    evaluation_moondream: bool = result.response == expected_solution
    assert (
        result.response == expected_solution or evaluation_moondream == moondream_match
    ), f"Expected {expected_solution}, but got {result.response}"


@pytest.mark.parametrize(
    "image_data,expected_solution,expected_query,moondream_multi_shoot_match",
    load_image_test_cases("moondream_multi_shoot_match"),
)
def test_aws_moondream_multi_shoot_image_resolver(
    test_config,
    image_data: str,
    expected_solution: list[bool],
    expected_query: str,
    moondream_multi_shoot_match: bool,
):
    sleep(15)
    resolver = AWSImageResolverMultiShootMoonDreamBackend(test_config)
    result = resolver.solve(image_data, query=expected_query)

    assert (
        result.response == expected_solution
        or result.response == moondream_multi_shoot_match
    ), f"Expected {expected_solution}, but got {result.response}"


@pytest.mark.parametrize(
    "image_data,expected_solution,expected_query,groq_multi_shoot_match",
    load_image_test_cases("groq_multi_shoot_match"),
)
def test_aws_groq_multi_shoot_image_resolver(
    test_config,
    image_data: str,
    expected_solution: list[bool],
    expected_query: str,
    groq_multi_shoot_match: bool,
):
    sleep(15)
    resolver = AWSImageResolverMultiShootGroqBackend(test_config)
    result = resolver.solve(image_data, query=expected_query)

    evaluation_groq: bool = result.response == expected_solution

    assert (
        result.response == expected_solution
        or evaluation_groq == groq_multi_shoot_match
    ), f"Expected {expected_solution}, but got {result.response}"
