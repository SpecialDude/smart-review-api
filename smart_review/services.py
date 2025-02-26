import json
import os
import re
from typing import Optional
from groq import Groq

import json_repair

import cohere

from smart_review.serializers import QuestionSerializer


class SmartLLMReviewService:
    _co = cohere.ClientV2(os.environ['COHERE_API_KEY'])
    _groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    @classmethod
    def get_review(cls, class_note: str, no_of_questions: int):
        # return QuestionSerializer(cls._generate_review(class_note, no_of_questions), many=True)
        return QuestionSerializer(cls._generate_review_with_groq(class_note, no_of_questions), many=True)

    @classmethod
    def _generate_review(cls, class_note: str, no_of_questions: int):

        context = class_note
        number_of_question = no_of_questions

        response = cls._co.chat(
            model="command-r-plus",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI that generates **strictly valid JSON** responses with no extra characters or formatting issues."
                },
                {
                    "role": "user",
                    "content": f"""Based on the following class notes, generate {number_of_question} objective questions in JSON format. \
                    Each question should have labelled options (A, B, C, D) and a correct answer. Only generate questions from this context:\n\n{context}\n\n\
                    The JSON structure should be:
                    [
                        {{
                            "question": "string",
                            "options": [
                                {{ "label": "A", "option": "string" }},
                                {{ "label": "B", "option": "string" }},
                                {{ "label": "C", "option": "string" }},
                                {{ "label": "D", "option": "string" }}
                            ],
                            "correct_option": {{ "label": "A", "option": "string" }}
                        }}
                    ]
                    ``` Each question must strictly follow this structure"""
                }
            ]
        )

        content = response.message.content[0].text
        # clean_json = re.sub(r"```json\n|\n```", "", content)

        clean_json = re.sub(r"^.*?```json\n*", "", content, flags=re.DOTALL)
        clean_json = re.sub(r"\n*```$", "", clean_json)

        print(clean_json)

        print("\n\n\nContent\n\n")

        print(clean_json)

        # data = json.loads(clean_json)
        data = json_repair.loads(clean_json)

        print(data)

        return data

    @classmethod
    def _generate_review_with_groq(cls, class_note: str, no_of_questions: int, response_model: Optional[QuestionSerializer] = None) -> dict:

        context = f"""Based on the following class notes, generate {no_of_questions} objective questions in JSON format. \
                Each question should have labelled options (A, B, C, D) and a correct answer. Only generate questions from this context:\n\n{class_note}\n\n\
                The JSON structure should be:
                [
                    {{
                        "question": "string",
                        "options": [
                            {{ "label": "A", "option": "string" }},
                            {{ "label": "B", "option": "string" }},
                            {{ "label": "C", "option": "string" }},
                            {{ "label": "D", "option": "string" }}
                        ],
                        "correct_option": {{ "label": "A", "option": "string" }}
                    }}
                ]
                ``` Each question must strictly follow this structure"""

        completion = cls._groq.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI that generates **strictly valid JSON** responses with no extra characters or formatting issues."},
                {"role": "user", "content": context}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        # Parse response
        response_data = json.loads(completion.choices[0].message.content)

        # # Validate with model if provided
        # if response_model:
        #     validated_data = \
        #         response_model.model_validate(response_data)
        # return validated_data.model_dump()

        return response_data['questions']
