import factory
from datetime import timedelta
from django.utils import timezone

from .models import Event, EventStage

class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    class Params:
        published = factory.Trait(status = Event.Status.PUBLISHED)
        ongoing = factory.Trait(status = Event.Status.ONGOING)
        closed = factory.Trait(status = Event.Status.CLOSED)
        finished = factory.Trait(status = Event.Status.FINISHED)
        cancelled = factory.Trait(status = Event.Status.CANCELLED)

    organizer = factory.SubFactory(
        "user.factories.CustomUserFactory",
        organizer=True
        )
    title = factory.Faker('sentence', nb_words=5)
    description = factory.Faker('paragraph', nb_sentences=3)
    capacity = factory.Faker("random_int", min=10, max=200)
    start_date = factory.LazyFunction( lambda: timezone.now() + timedelta(days=7) )
    status = Event.Status.DRAFT
    end_date = factory.LazyAttribute(lambda obj: obj.start_date + timedelta(hours=4))

class EventStageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventStage

    event = factory.SubFactory('event.factories.EventFactory')
    title = factory.Faker('sentence', nb_words=5)
    description = factory.Faker('paragraph', nb_sentences=3)
    order = factory.Sequence(lambda n: n + 1)
    start_time = factory.LazyAttribute(lambda obj: obj.event.start_date + timedelta(hours=1))
    end_time = factory.LazyAttribute(lambda obj: obj.start_time + timedelta(hours=1))