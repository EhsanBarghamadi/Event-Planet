from rest_framework import serializers

from event.models import Event
from .models import Attribute, EventAttributeValue

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'slug', 'name', 'data_type']
        read_only_fields = ['slug']

class EventAttributeValueSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    
    class Meta:
        model = EventAttributeValue
        fields = ['id', 'event', 'attribute', 'value_text', 'value_int', 'value_bool', 'created_at', 'updated_at']

    def validate(self, attrs):
        if self.instance:
            event = attrs.get('event', self.instance.event)
            attribute = attrs.get('attribute', self.instance.attribute)
            value_text = attrs.get('value_text', self.instance.value_text)
            value_int = attrs.get('value_int', self.instance.value_int)
            value_bool = attrs.get('value_bool', self.instance.value_bool)

            if 'event' in attrs and attrs['event'] != self.instance.event:
                raise serializers.ValidationError({'event': 'تغییر رویداد مجاز نیست!'})
            if 'attribute' in attrs and attrs['attribute'] != self.instance.attribute:
                raise serializers.ValidationError({'attribute': 'تغییر ویژگی مجاز نیست!'})
            
        else:
            event = attrs.get('event')
            attribute = attrs.get('attribute')
            value_text = attrs.get('value_text')
            value_int = attrs.get('value_int')
            value_bool = attrs.get('value_bool')

        if not event:
            raise serializers.ValidationError({'event': 'انتخاب رویداد الزامی است!'})
        
        if event.status != Event.Status.DRAFT:
            raise serializers.ValidationError({
                'event': 'امکان ثبت ویژگی فقط روی رویداد های پیش نویس وجود دارد.'
            })
        
        if attribute:
            if attribute.data_type == "TEXT":
                if value_int is not None or value_bool is not None or value_text is None:
                    raise serializers.ValidationError('فقط باید فیلد متن پر شود.')
                else:
                    return attrs
            elif attribute.data_type == 'INTEGER':
                if value_text is not None or value_bool is not None or value_int is None:
                    raise serializers.ValidationError('فقط باید فیلد عدد پر شود.')
                else:
                    return attrs
            elif attribute.data_type == 'BOOLEAN':
                if value_text is not None or value_int is not None or value_bool is None:
                    raise serializers.ValidationError('فقط باید فیلد بله و خیر پر شود.')
                return attrs
        return attrs