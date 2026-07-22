from rest_framework import permissions

from event.models import Event

class IsOrganizer(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.role == 'ORGANIZER':
            return True
        return False
    
class IsParticipant(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.role == 'PARTICIPANT':
            return True
        return False
        
class IsEventOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == 'create':
            event_id = request.data.get('event_id')
            event = request.data.get('event')
 
            if not event_id and not event:
                return True
 
            if event_id and event and str(event_id) != str(event):
                return False
 
            event_id_to_check = event_id or event
            return Event.objects.filter(
                id=event_id_to_check, organizer=request.user
            ).exists()
        return True

    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        event = obj if hasattr(obj , 'organizer') else getattr(obj, 'event', None)
        return bool(event and event.organizer_id == request.user.id)

class IsFeedbackOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.participant == request.user
