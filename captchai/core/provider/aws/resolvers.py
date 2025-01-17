import base64
import io
import json

from functools import cached_property
from time import sleep

import moondream as md

from groq import Groq
from moondream.types import Region
from PIL import Image
from pydub import AudioSegment

from captchai.core.models.config import CaptchaGlobalConfig
from captchai.core.models.config import CaptchaResponse
from captchai.core.models.grid import GridLLamaVisionResponse
from captchai.core.models.grid import GridQuadrant
from captchai.core.provider.base.base import AbstractResolver


class AudioTranscriptionError(Exception):
    """Base exception for audio transcription related errors."""


class AudioProcessingError(AudioTranscriptionError):
    """Raised when there are issues processing the audio file."""


class AWSImageResolverOneShootGroqBackend(AbstractResolver):
    """Resolver for image captchas using the Llama 3.2 90B Vision model."""

    __PROMPT = """
    This image has 3 rows and 3 columns. It is a 3x3 grid. List all images inside
    in order using just one word (e.g., bed, clock, bucket, hat, bag, curtain, etc.).
    If you find a Window, change it for a curtain. Put the data in a JSON format
    and respond with it only, without adding any explanation.
    """

    def __init__(self, config: CaptchaGlobalConfig):
        super().__init__(config)
        self.groq = Groq(api_key=config.groq_api_key)

    def _extract_response(
        self, response: str, query: str
    ) -> CaptchaResponse[list[bool]]:
        data = json.loads(response)
        validated_response = GridLLamaVisionResponse(**data)
        return CaptchaResponse[list[bool]](
            response=validated_response.get_flattened_matches(query)
        )

    def solve(self, data: str, **kwargs):
        if "query" not in kwargs:
            raise ValueError("'query' parameter is required in kwargs")

        completion = self.groq.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.__PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{data}"},
                        },
                    ],
                }
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        return self._extract_response(
            completion.choices[0].message.content, kwargs.get("query", "")
        )


class AWSAudioResolverGroqBackend(AbstractResolver):
    def __init__(self, config: CaptchaGlobalConfig):
        super().__init__(config)
        self._groq = Groq(api_key=config.groq_api_key)

    def _parse_transcription(self, transcription: str) -> list[str]:
        """Parse the transcription to extract the two words after 'spoken by me'.

        Args:
            transcription: The transcribed text from the audio file

        Returns:
            List containing the two parsed words

        Raises:
            ValueError: If the parsing fails or words cannot be extracted
        """
        try:
            filter_word_from_sentence = transcription.split("spoken by me. ")
            after_spoken_by_me = filter_word_from_sentence[1].split(" ")

            first_word = after_spoken_by_me[0].replace(".", "").strip().lower()
            second_word = after_spoken_by_me[1].replace(".", "").strip().lower()

            return [first_word, second_word]
        except Exception as e:
            raise AudioTranscriptionError("Failed to parse audio transcription") from e

    def _prepare_flac_audio(self, audio_data: bytes) -> tuple[str, bytes]:
        """Prepare audio data for transcription by ensuring it's in FLAC format.

        Args:
            audio_data: Raw audio data in bytes

        Returns:
            A tuple of (filename, audio_data) ready for the Groq API

        Note:
            The method handles both conversion to FLAC if needed and proper file
            format detection
        """
        audio_buffer = io.BytesIO(audio_data)

        try:
            # Check if the file is already FLAC by examining the header
            audio_buffer.seek(0)
            header = audio_buffer.read(4)
            is_flac = header.startswith(b"fLaC")
            audio_buffer.seek(0)

            audio = AudioSegment.from_file(audio_buffer)

            # Only convert if not already in FLAC format
            if not is_flac:
                flac_buffer = io.BytesIO()
                audio.export(flac_buffer, format="flac")
                flac_buffer.seek(0)
                processed_audio = flac_buffer.read()
            else:
                audio_buffer.seek(0)
                processed_audio = audio_buffer.read()

            return ("audio.flac", processed_audio)

        except Exception as e:
            raise AudioProcessingError("Failed to process audio file") from e
        finally:
            audio_buffer.close()

    def solve(self, data: str, **kwargs) -> CaptchaResponse[list[str]]:
        audio_data = base64.b64decode(data)

        file_data = self._prepare_flac_audio(audio_data)

        response = self._groq.audio.transcriptions.create(
            file=file_data,
            model="whisper-large-v3-turbo",
            language="en",
            temperature=0,
        )

        words = self._parse_transcription(response.text)
        captcha_response = CaptchaResponse(response=words)
        return captcha_response


class AWSImageResolverOneShootMoonDreamBackend(AbstractResolver):
    """Resolver for image captchas using the MoonDream backend."""

    def __init__(self, config: CaptchaGlobalConfig):
        super().__init__(config)
        self.image_size = config.aws_provider_config.image_size
        self.grid_size = config.aws_provider_config.grid_size
        self.model = md.vl(api_key=config.moondream_api_key)

    @cached_property
    def _get_grid_quadrants(self) -> list[GridQuadrant]:
        """Returns a list of GridQuadrants for the given image."""
        grid_size = self.grid_size
        image_size = self.image_size

        grid_width = image_size[0] // grid_size
        grid_height = image_size[1] // grid_size

        quadrants = []
        for y in range(grid_size):
            for x in range(grid_size):
                quadrants.append(
                    GridQuadrant(
                        x_start=x * grid_width,
                        x_end=(x + 1) * grid_width,
                        y_start=y * grid_height,
                        y_end=(y + 1) * grid_height,
                    )
                )
        return quadrants

    def _get_quadrants_of_objects(self, objects: list[Region]) -> list[GridQuadrant]:
        quadrants_of_objects = []
        for object_quadrant in objects:
            quadrants_of_objects.append(
                GridQuadrant(
                    x_start=object_quadrant["x_min"] * self.image_size[0],
                    x_end=object_quadrant["x_max"] * self.image_size[0],
                    y_start=object_quadrant["y_min"] * self.image_size[1],
                    y_end=object_quadrant["y_max"] * self.image_size[1],
                )
            )
        return quadrants_of_objects

    def _compute_solution_flatten_list(
        self, quadrants_of_objects: list[GridQuadrant]
    ) -> list[bool]:
        solutions = [False] * self.config.aws_provider_config.grid_size**2
        image_quadrants: list[GridQuadrant] = self._get_grid_quadrants
        for object_quadrant_index, object_quadrant in enumerate(quadrants_of_objects):
            for quadrant_index, quadrant in enumerate(image_quadrants):
                inside = quadrant.is_point_inside(
                    object_quadrant.middle_point_coordinates[0],
                    object_quadrant.middle_point_coordinates[1],
                )
                if inside:
                    solutions[quadrant_index] = True
                    break
        return solutions

    def _extract_solution(self, query, loaded_image):
        detected_output = self.model.detect(loaded_image, query)
        quadrants_of_objects = self._get_quadrants_of_objects(
            detected_output["objects"]
        )

        solution = self._compute_solution_flatten_list(quadrants_of_objects)
        return solution

    def solve(self, data: str, **kwargs):
        if "query" not in kwargs:
            raise ValueError("'query' parameter is required in kwargs")

        query = kwargs["query"]
        loaded_image = Image.open(io.BytesIO(base64.b64decode(data)))
        solution = self._extract_solution(query, loaded_image)
        return CaptchaResponse[list[bool]](response=solution)


class AWSImageResolverMultiShootMoonDreamBackend(AbstractResolver):
    def __init__(self, config: CaptchaGlobalConfig):
        super().__init__(config)
        self.grid_size = config.aws_provider_config.grid_size
        self.image_size = config.aws_provider_config.image_size
        self.model = md.vl(api_key=config.moondream_api_key)

    def solve(self, data: str, **kwargs):
        if "query" not in kwargs:
            raise ValueError("'query' parameter is required in kwargs")

        query = kwargs["query"]
        loaded_image = Image.open(io.BytesIO(base64.b64decode(data)))
        solution = self._extract_solution(query, loaded_image)
        return CaptchaResponse[list[bool]](response=solution)

    def _extract_solution(self, query, loaded_image):
        solution = []
        splitted_image = self._split_image(loaded_image)
        for image in splitted_image:
            sleep(2)
            result = self.model.query(
                image, f"is this a {query}? answer only in yes or no"
            )
            if result["answer"].strip().lower() == "yes":
                solution.append(True)
            else:
                solution.append(False)
        return solution

    def _split_image(self, loaded_image: Image.Image) -> list[Image.Image]:
        grid_width = self.image_size[0] // self.grid_size
        grid_height = self.image_size[1] // self.grid_size

        split_images = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                x_start = x * grid_width
                x_end = (x + 1) * grid_width
                y_start = y * grid_height
                y_end = (y + 1) * grid_height

                cropped_image = loaded_image.crop((x_start, y_start, x_end, y_end))
                split_images.append(cropped_image)

        return split_images


class AWSImageResolverMultiShootGroqBackend(AbstractResolver):
    __PROMPT = """
    Choose the type of object you see. The preferred options are: chair, hat,
    bag, bed, bucket or curtain. If you strongly believe it is something else,
    respond with that one word only. Provide only the object name as your answer,
    nothing more.
    """

    def __init__(self, config: CaptchaGlobalConfig):
        super().__init__(config)
        self.grid_size = config.aws_provider_config.grid_size
        self.image_size = config.aws_provider_config.image_size
        self.groq = Groq(api_key=config.groq_api_key)

    def _split_image(self, loaded_image: Image.Image) -> list[Image.Image]:
        grid_width = self.image_size[0] // self.grid_size
        grid_height = self.image_size[1] // self.grid_size

        split_images = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                x_start = x * grid_width
                x_end = (x + 1) * grid_width
                y_start = y * grid_height
                y_end = (y + 1) * grid_height

                cropped_image = loaded_image.crop((x_start, y_start, x_end, y_end))
                split_images.append(cropped_image)

        return split_images

    def _extract_solution(self, query, loaded_image) -> list[bool]:
        solution = []
        split_image = self._split_image(loaded_image)
        for idx, image in enumerate(split_image):
            # Save each split image for debugging
            # image.save(os.path.join(debug_dir, f"split_image_{idx}.png"))

            buffer = io.BytesIO()
            image.convert("RGB").save(buffer, format="JPEG")
            data = base64.b64encode(buffer.getvalue()).decode("utf-8")
            sleep(2)
            result = self.groq.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.__PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{data}"},
                            },
                        ],
                    }
                ],
                temperature=0,
            )
            if (
                result.choices[0].message.content.strip().lower().replace(".", "")
                == query
            ):
                solution.append(True)
            else:
                solution.append(False)
        return solution

    def solve(self, data: str, **kwargs):
        if "query" not in kwargs:
            raise ValueError("'query' parameter is required in kwargs")

        query = kwargs["query"]
        loaded_image = Image.open(io.BytesIO(base64.b64decode(data)))
        solution = self._extract_solution(query, loaded_image)
        return CaptchaResponse[list[bool]](response=solution)
