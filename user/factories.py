import factory

from .models import CustomUser


class CustomUserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CustomUser

    class Params:
        organizer = factory.Trait(role=CustomUser.Roles.ORGANIZER)
        participant = factory.Trait(role=CustomUser.Roles.PARTICIPANT)

    phone = factory.Sequence(lambda n: f"0{9000000000 + n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = CustomUser.Roles.PARTICIPANT

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        self.set_password(extracted if extracted else "1234")
        self.save()
