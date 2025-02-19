from rest_framework import serializers


class OptionSerializer(serializers.Serializer):
    label = serializers.ChoiceField(choices=["A", "B", "C", "D"])
    option = serializers.CharField()


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
    options = OptionSerializer(many=True)
    correct_option = OptionSerializer()


class SmartReviewSerializer(serializers.Serializer):
    class_note = serializers.CharField(required=True)
    number_of_questions = serializers.IntegerField(max_value=10, min_value=1, default=10, required=False)
