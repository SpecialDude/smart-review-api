from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from smart_review.serializers import SmartReviewSerializer, QuestionSerializer
from smart_review.services import SmartLLMReviewService


# Create your views here.


class SmartReviewAPIView(APIView):
    """
    API endpoint that takes a class note and generates a set of questions using LLM.
    """

    @extend_schema(
        summary="Generate Questions from Class Notes",
        description=(
                "This API takes a class note and generates multiple-choice questions "
                "using an LLM. You can specify the number of questions (maximum: 20)."
        ),
        tags=['LLM Smart Review'],
        request=SmartReviewSerializer,
        responses={200: QuestionSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Example Request",
                description="Request to generate 3 questions from a physics note.",
                value={
                    "class_note": "Newton's Laws of Motion describe the relationship between motion and force.",
                    "number_of_questions": 3
                },
                request_only=True
            ),
            OpenApiExample(
                name="Example Response",
                description="Response with generated multiple-choice questions.",
                value=[
                    {
                        "question": "Which of Newton's Laws states that an object in motion stays in motion unless acted upon?",
                        "options": [
                            {"label": "A", "option": "First Law"},
                            {"label": "B", "option": "Second Law"},
                            {"label": "C", "option": "Third Law"},
                            {"label": "D", "option": "Law of Universal Gravitation"}
                        ],
                        "correct_option": {"label": "A", "option": "First Law"}
                    }
                ],
                response_only=True
            )
        ]
    )
    def post(self, request):
        serializer = SmartReviewSerializer(data=request.data)
        if serializer.is_valid():
            class_note = serializer.validated_data["class_note"]
            number_of_questions = serializer.validated_data["number_of_questions"]

            # Call the service layer to generate questions
            questions = SmartLLMReviewService.get_review(class_note, number_of_questions)

            return Response(questions.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
