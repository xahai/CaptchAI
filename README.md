# 🤖 CaptchAI

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)]()

**Solve AWS WAF CAPTCHAs using Modern AI! 🚀**

*Using powerful AI models like Groq and Moondream to solve AWS WAF CAPTCHAs quickly and accurately*

*A joint development effort by [LaProp](https://laprop.co) and [XAhai](https://xahai.co)*

> ⚠️ **Alpha Status Notice**: This library is currently in alpha stage. Many features are still under development, 
> requiring thorough testing and integration. Expect frequent updates and potential breaking changes.
> We welcome feedback and contributions to help improve stability and functionality!

[Features](#-features) •
[Installation](#-installation) •
[Configuration](#%EF%B8%8F-configuration) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Contributing](#-contributing)

</div>

## 🌟 Features

- 🧠 **Modern AI Models**
  - Groq LLM for smart solving
  - Moondream for image analysis
  - High accuracy rates
  
- 🛡️ **AWS WAF CAPTCHA Support**
  - Built for AWS WAF challenges
  - Solves image puzzles
  - Handles audio challenges
  
- ⚡ **High Performance**
  - Quick processing
  - Smart backup options
  - Reliable results
  
- 🛠️ **Easy to Use**
  - Simple API
  - Easy setup
  - Built to extend
  - Full Python typing

> **Note**: Currently, CaptchAI only works with AWS WAF CAPTCHAs. We plan to add support for other CAPTCHAs in the future.

## 📦 Installation

```bash
pip install captchai
```

## ⚙️ Configuration

```python
from captchai.core.models.config import CaptchaGlobalConfig, AWSProviderConfig, AvailableResolvers

config = CaptchaGlobalConfig(
    groq_api_key="your-groq-api-key",
    moondream_api_key="your-moondream-api-key",
    aws_provider_config=AWSProviderConfig(
        image_size=(640, 640),  # Customize image size
        grid_size=3,  # Grid dimensions
        resolver=AvailableResolvers.GROQ_IMAGE_ONE_SHOOT,
        # Fallback resolvers for resilience
        list_resolver_image_fallback=[
            AvailableResolvers.MOONDREAM_IMAGE_ONE_SHOOT,
            AvailableResolvers.GROQ_IMAGE_ONE_SHOOT,
            AvailableResolvers.GROQ_IMAGE_MULTI_SHOOT,
            AvailableResolvers.MOONDREAM_IMAGE_MULTI_SHOOT
        ]
    )
)
```

## 🎯 Available Resolvers

### 🖼️ Image Resolvers
- `GROQ_IMAGE_ONE_SHOOT`: Single-shot solving with Groq
- `GROQ_IMAGE_MULTI_SHOOT`: Multi-shot approach with Groq
- `MOONDREAM_IMAGE_ONE_SHOOT`: Quick Moondream vision model
- `MOONDREAM_IMAGE_MULTI_SHOOT`: Advanced Moondream processing

### 🎵 Audio Resolvers
- `GROQ_AUDIO`: Advanced audio CAPTCHA processing

## 🚀 Quick Start

Here's a complete example of how to use Captchai to solve different types of CAPTCHAs:

```python
from captchai import CaptchaSolver
from captchai.core.models.config import (
    CaptchaGlobalConfig,
    AWSProviderConfig,
    AvailableResolvers
)
import base64

def solve_captcha_example():
    # 1. Configure the solver
    config = CaptchaGlobalConfig(
        groq_api_key="your-groq-api-key",
        moondream_api_key="your-moondream-api-key",
        aws_provider_config=AWSProviderConfig(
            resolver=AvailableResolvers.GROQ_IMAGE_ONE_SHOOT,
            grid_size=3,
            image_size=(640, 640)
        )
    )

    # 2. Initialize the solver
    solver = CaptchaSolver(config)

    # 3. Solve different types of CAPTCHAs
    
    # Image CAPTCHA (using base64 string)
    with open("path/to/captcha.png", "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # For image CAPTCHAs, query is required - it specifies what type of object to identify
    image_result = solver.solve_aws_captcha_image(
        data=image_base64,
        query="bucket"  # Required: Specify the type of object to identify
    )
    print(f"Image CAPTCHA Solution: {image_result}")

    # Audio CAPTCHA (using base64 string)
    with open("path/to/audio.mp3", "rb") as audio_file:
        audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
    
    # For audio CAPTCHAs, query is optional
    audio_result = solver.solve_aws_captcha(
        data=audio_base64
    )
    print(f"Audio CAPTCHA Solution: {audio_result}")

if __name__ == "__main__":
    solve_captcha_example()
```

> **Note**: For image CAPTCHAs, the `query` parameter is required - it specifies what type of object to identify (e.g., "Select all images with traffic lights", "Select all squares with buses"). For audio CAPTCHAs, the `query` parameter is optional.

## 📋 Requirements

- Python 3.12+
- Dependencies:
  - groq >= 0.15.0
  - moondream >= 0.0.6
  - pydantic >= 2.10.5
  - pydub >= 0.25.1
  - pytest >= 8.3.4

## 📝 TODO List

- [x] **Core Features**
  - [x] Groq LLM integration
  - [x] Moondream vision model integration
  - [x] AWS WAF CAPTCHA image solving
  - [x] AWS WAF CAPTCHA audio solving
  - [x] Fallback resolver system

- [ ] **Direct AWS Integration**
  - [ ] Handle AWS CAPTCHA request/response flow directly
  - [ ] Implement automatic token extraction and submission

- [ ] **Browser Automation**
  - [ ] Selenium integration for automated CAPTCHA solving
  - [ ] Playwright integration
  - [ ] Browser extension support

- [ ] **Future Enhancements**
  - [ ] Support for additional CAPTCHA providers
  - [ ] More AI model options
  - [ ] Performance optimizations
  - [ ] Improved error handling and retries
  - [ ] Comprehensive logging system

## 🤝 Contributing

We welcome your contributions! We want to make it easy for you to help improve Captchai. Check out our [Contributing Guidelines](CONTRIBUTING.md) to get started.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**IMPORTANT: FOR RESEARCH AND EDUCATIONAL PURPOSES ONLY**

This library is for **research and educational purposes only**. It helps study and understand how AI can solve CAPTCHA challenges.

By using this library, you agree that:

1. This tool is only for research, testing, and learning
2. Using this library to bypass CAPTCHAs on real websites may break their terms of service
3. The developers and contributors are NOT responsible for:
   - Any misuse of the library
   - Breaking any website's terms of service
   - Any legal issues from using this library
   - Any problems or losses from using this library
4. You are responsible for using this library in a way that follows all laws, rules, and terms of service

**DO NOT** use this library to:
- Bypass security on real websites
- Break any website's terms of service
- Do any kind of automated abuse or spam

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

---

<div align="center">
Made with ❤️ by the xAhai and LaProp Team
</div>