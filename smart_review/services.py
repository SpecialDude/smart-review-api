import json
import os
import re

import cohere

from smart_review.serializers import QuestionSerializer


class SmartLLMReviewService:
    _co = cohere.ClientV2(os.environ['COHERE_API_KEY'])

    @classmethod
    def get_review(cls, class_note: str, no_of_questions: int):
        return QuestionSerializer(cls._generate_review(class_note, no_of_questions), many=True)

    @classmethod
    def _generate_review(cls, class_note: str, no_of_questions: int):

        context = class_note
        number_of_question = no_of_questions

        response = cls._co.chat(
            model="command-r-plus",
            messages=[
                {
                    "role": "user",
                    "content": f"Based on the following class notes, generate {number_of_question} objective questions in JSON format. \
                    Each question should have labelled options (A, B, C, D) and a correct answer. Only generate questions from this context:\n\n{context}\n\n\
                    The JSON structure should be:\n\
                    ```json\n\
                    [\n\
                        {{\n\
                            \"question\": \"string\",\n\
                            \"options\": [\n\
                                {{ \"label\": \"A\", \"option\": \"string\" }},\n\
                                {{ \"label\": \"B\", \"option\": \"string\" }},\n\
                                {{ \"label\": \"C\", \"option\": \"string\" }},\n\
                                {{ \"label\": \"D\", \"option\": \"string\" }}\n\
                            ],\n\
                            \"correct_option\": {{ \"label\": \"A\", \"option\": \"string\" }}\n\
                        }}\n\
                    ]\n\
                    ```"
                }
            ]
        )

        content = response.message.content[0].text
        clean_json = re.sub(r"```json\n|\n```", "", content)

        print(content)

        print("\n\n\nContent\n\n")

        print(clean_json)

        data = json.loads(clean_json)

        print(data)

        return data
