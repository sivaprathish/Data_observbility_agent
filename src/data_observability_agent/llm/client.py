from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class LLMClient:

    def __init__(self):

        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is missing."
            )

        self.model = os.getenv(
            "GROQ_MODEL"
        )

        self.client = Groq(
            api_key=api_key
        )

    def generate(
        self,
        prompt: str,
    ) -> str:

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior data "
                            "reliability and data "
                            "observability engineer."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.1,
                max_tokens=1200,
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )
