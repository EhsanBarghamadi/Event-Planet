from rest_framework import serializers
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
        request = self.context.get('request')
        if self.instance:
            event = attrs.get('event', self.instance.event)
            attribute = attrs.get('attribute', self.instance.attribute)
        else:
            event = attrs.get('event')
            attribute = attrs.get('attribute')
        
        if event.organizer != request.user:
            raise serializers.ValidationError('شما مالک این رویداد نیستید!')
        
        if attribute:
            value_text = attrs.get('value_text')
            value_int = attrs.get('value_int')
            value_bool = attrs.get('value_bool')
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