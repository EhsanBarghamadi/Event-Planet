from rest_framework import permissions

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
