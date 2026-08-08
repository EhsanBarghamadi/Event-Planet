from django.core.management.base import BaseCommand

from user.models import CustomUser
from event.models import Event, EventStage
from attribute.models import Attribute, EventAttributeValue
from relation.models import Registration, Feedback, Result
from user.factories import CustomUserFactory
from event.factories import EventFactory, EventStageFactory
from attribute.factories import AttributeFactory, EventAttributeValueFactory
from relation.factories import RegistrationFactory, FeedbackFactory, ResultFactory


class Command(BaseCommand):
    help = "Seed database with realisitic data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing seed data before creating new data",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self._flush_data()
        self.stdout.write("Seed command started")
        organizers, participants = self._create_users()
        events = self._create_event_scenarios(organizers)
        self._create_cancelled_scenario(events["cancelled"])
        self._create_attribute_event(events)
        self._create_event_stages(events)
        self._create_published_scenario(events["published"])
        self._create_ongoing_scenario(events["ongoing"], participants, 10)
        self._create_finished_scenario(events["finished"], participants)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created\n"
                f"Users: {CustomUser.objects.count()}\n"
                f"Events: {Event.objects.count()}\n"
                f"Attributes: {Attribute.objects.count()}\n"
                f"Registrations: {Registration.objects.count()}\n"
                f"Feedbacks: {Feedback.objects.count()}\n"
                f"Results: {Result.objects.count()}"
            )
        )

    def _create_users(self):
        organizers = [CustomUserFactory(organizer=True) for _ in range(1, 6)]
        participants = [CustomUserFactory(participant=True) for _ in range(1, 16)]
        return organizers, participants

    def _create_event_scenarios(self, organizers):
        events = {
            "cancelled": EventFactory(organizer=organizers[0]),
            "draft": EventFactory(organizer=organizers[1]),
            "published": EventFactory(organizer=organizers[2]),
            "ongoing": EventFactory(organizer=organizers[3]),
            "finished": EventFactory(organizer=organizers[4]),
        }
        return events

    def _create_cancelled_scenario(self, event):
        event.status = Event.Status.CANCELLED
        event.save()

    def _create_attributes(self):
        attribute = []
        text_attribute = AttributeFactory(text=True)
        integer_attribute = AttributeFactory(integer=True)
        boolean_attribute = AttributeFactory(boolean=True)
        attribute.extend([text_attribute, integer_attribute, boolean_attribute])
        return attribute

    def _create_attribute_event(self, events):
        attributes = self._create_attributes()

        draft = events["draft"]
        published = events["published"]
        ongoing = events["ongoing"]
        finished = events["finished"]

        for attribute in attributes:
            EventAttributeValueFactory(event=draft, attribute=attribute)
            EventAttributeValueFactory(event=published, attribute=attribute)
            EventAttributeValueFactory(event=ongoing, attribute=attribute)
            EventAttributeValueFactory(event=finished, attribute=attribute)

    def _create_event_stages(self, events):
        EventStageFactory(event=events["draft"])
        EventStageFactory(event=events["published"])
        EventStageFactory(event=events["ongoing"])
        EventStageFactory(event=events["finished"])

    def _create_registrations(self, event, participants, registration_count):
        registrations = []
        for participant in participants[:registration_count]:
            registration = RegistrationFactory(event=event, participant=participant)
            registrations.append(registration)
        return registrations

    def _create_published_scenario(self, event):
        event.status = Event.Status.PUBLISHED
        event.save()

    def _create_ongoing_scenario(self, event, participants, registration_count):
        self._create_published_scenario(event)
        registrations = self._create_registrations(
            event, participants, registration_count
        )

        event.status = Event.Status.ONGOING
        event.save()

        return registrations

    def _create_finished_scenario(self, event, participants):
        registrations = self._create_ongoing_scenario(event, participants, 10)

        event.status = Event.Status.FINISHED
        event.save()

        for registration in registrations:
            FeedbackFactory(participant=registration.participant, event=event)
            ResultFactory(participant=registration.participant, event=event)

    def _flush_data(self):
        self.stdout.write("Flushing existing seed data...")
        Feedback.objects.all().delete()
        Result.objects.all().delete()
        Registration.objects.all().delete()
        EventAttributeValue.objects.all().delete()
        Attribute.objects.all().delete()
        EventStage.objects.all().delete()
        Event.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()
