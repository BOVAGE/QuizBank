from rest_framework import serializers
from .models import InCorrectAnswer, Question, Category


class IncorrectAnswerSerializer(serializers.Serializer):
    incorrect_answer_1 = serializers.CharField(write_only=True)
    incorrect_answer_2 = serializers.CharField(write_only=True, required=False)
    incorrect_answer_3 = serializers.CharField(write_only=True, required=False)


class QuestionPublicSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        source="category.slug", queryset=Category.objects.all()
    )
    incorrect_answer_fields = IncorrectAnswerSerializer(write_only=True)
    incorrect_answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "question",
            "difficulty",
            "type",
            "category",
            "correct_answer",
            "incorrect_answers",
            "incorrect_answer_fields",
            "explanation",
            "image",
        ]

    def get_incorrect_answers(self, obj):
        return obj.incorrect_answers.values_list("option", flat=True)

    def validate(self, data):
        if (
            data.get("type") == "True / False"
            and len(data.get("incorrect_answer_fields")) > 1
        ):
            raise serializers.ValidationError(
                {
                    "incorrect_answer_fields": "True/False questions can have only one incorrect answer"
                }
            )
        return data

    def create(self, validated_data):
        category = validated_data.pop("category")["slug"]
        incorrect_answers = validated_data.pop("incorrect_answer_fields")
        question = Question.objects.create(**validated_data, category=category)
        incorrect_answers_list = []
        for incorrect_answer in incorrect_answers.values():
            incorrect_answers_list.append(
                InCorrectAnswer(question=question, option=incorrect_answer)
            )
        InCorrectAnswer.objects.bulk_create(incorrect_answers_list)
        question.refresh_from_db()
        return question

    def update(self, instance, validated_data):
        # check if category and incorrect_answer_fields is in validated_data

        category = (
            validated_data.get("category").get("slug")
            if validated_data.get("category")
            else None
        )
        incorrect_answers = validated_data.get("incorrect_answer_fields")
        if category:
            category = validated_data.pop("category")["slug"]
            instance.category = category
        if incorrect_answers:
            incorrect_answers = validated_data.pop("incorrect_answer_fields")
        # bulk update the only fields that are supplied using the key
        for key in validated_data.keys():
            setattr(instance, key, validated_data[key])
        instance.save()
        if incorrect_answers:
            incorrect_answers_list = [
                incorrect_answer for incorrect_answer in incorrect_answers.values()
            ]
            instance_incorrect_answers = instance.incorrect_answers.all()
            for idx, instance_incorrect_answer in enumerate(instance_incorrect_answers):
                instance_incorrect_answer.option = incorrect_answers_list[idx]
                instance_incorrect_answer.save()
            instance.refresh_from_db()
        return instance


class QuestionDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.username")
    verified_by = serializers.ReadOnlyField(source="verified_by.username")
    category = serializers.ReadOnlyField(source="category.slug")
    incorrect_answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "question",
            "difficulty",
            "type",
            "category",
            "correct_answer",
            "incorrect_answers",
            "explanation",
            "image",
            "created_by",
            "date_created",
            "is_verified",
            "verified_by",
            "date_verified",
        ]

    def get_incorrect_answers(self, obj):
        return obj.incorrect_answers.values_list("option", flat=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "name", "slug"]
        model = Category
