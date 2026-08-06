import factory

from .models import Registration, Feedback, Result


class RegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Registration

    participant = factory.SubFactory(
        "user.factories.CustomUserFactory", participant=True
    )
    event = factory.SubFactory("event.factories.EventFactory", published=True)


class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feedback

    participant = factory.SubFactory(
        "user.factories.CustomUserFactory", participant=True
    )
    event = factory.SubFactory("event.factories.EventFactory", finished=True)
    rating = factory.Faker("random_int", min=1, max=5)
    comment = factory.Faker("paragraph", nb_sentences=2)


class ResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Result

    participant = factory.SubFactory(
        "user.factories.CustomUserFactory", participant=True
    )
    event = factory.SubFactory("event.factories.EventFactory", finished=True)
    achievement = factory.Faker(
        "random_element",
        elements=[
            "کسب رتبه اول",
            "کسب رتبه دوم",
            "کسب رتبه سوم",
            "شایسته تقدیر",
            "قبول",
        ],
    )
