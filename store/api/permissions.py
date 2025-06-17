from rest_framework import permissions


class IsStaffOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_staff = user.has_perm("store.change_order")

        if view.action == "retrieve":
            return is_staff or obj.user == user

        if view.action == "list":
            return True

        if view.action == "create":
            return True

        if view.action in ["update", "partial_update"]:
            if not is_staff:
                return False
            return set(request.data.keys()) <= {"status"}

        if view.action == "destroy":
            return False

        return False
