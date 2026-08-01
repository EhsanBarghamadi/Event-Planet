import factory

from .models import CustomUser


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    phone = factory.Sequence(lambda n: f'0{9000000000 + n}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = CustomUser.Roles.PARTICIPANT

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return 
        self.set_password(extracted if extracted else '1234')
        self.save()

class OrganizerFactory(CustomUserFactory):
    role = CustomUser.Roles.ORGANIZER

class ParticipantFactory(CustomUserFactory):
    role = CustomUser.Roles.PARTICIPANT