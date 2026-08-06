import factory
from faker import Faker

from .models import Attribute, EventAttributeValue

fake = Faker()


class AttributeFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Attribute

    class Params:
        text = factory.Trait(data_type=Attribute.DataType.TEXT)
        integer = factory.Trait(data_type=Attribute.DataType.INTEGER)
        boolean = factory.Trait(data_type=Attribute.DataType.BOOLEAN)

    name = factory.Sequence(lambda n: f"attribute-{n}")
    data_type = Attribute.DataType.TEXT


class EventAttributeValueFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = EventAttributeValue

    event = factory.SubFactory("event.factories.EventFactory")
    attribute = factory.SubFactory(AttributeFactory)
    value_text = factory.LazyAttribute(
        lambda obj: (
            fake.sentence()
            if obj.attribute.data_type == Attribute.DataType.TEXT
            else None
        )
    )
    value_int = factory.LazyAttribute(
        lambda obj: (
            fake.random_int()
            if obj.attribute.data_type == Attribute.DataType.INTEGER
            else None
        )
    )
    value_bool = factory.LazyAttribute(
        lambda obj: (
            fake.boolean()
            if obj.attribute.data_type == Attribute.DataType.BOOLEAN
            else None
        )
    )
