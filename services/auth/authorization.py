class AuthorizationError(Exception):
    pass

class AuthorizationService:
    @staticmethod
    def get_permissions_for_identity(db, identity):
        from models.user_role import UserRole
        from models.service_account_role import ServiceAccountRole
        from models.role_permission import RolePermission
        from models.permission import Permission
        perms = set()
        if identity.subject_type == "user":
            roles = db.query(UserRole).filter_by(user_id=identity.subject_id).all()
        else:
            roles = db.query(ServiceAccountRole).filter_by(service_id=identity.subject_id).all()
        for r in roles:
            role_perms = (
                db.query(Permission.key)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .filter(RolePermission.role_id == r.role_id)
                .all()
            )
            for p in role_perms:
                perms.add(p[0])
        return perms

    @staticmethod
    def check(db, identity, permission_key: str):
        if identity is None:
            raise AuthorizationError("Not authenticated")
        # 1. If identity has token scopes, enforce them first
        if hasattr(identity, "token_scopes") and identity.token_scopes is not None:
            scopes = identity.token_scopes
            if permission_key in scopes:
                return True
            # wildcard support
            prefix = permission_key.split(".")[0] + ".*"
            if prefix in scopes:
                return True
            raise AuthorizationError(f"Token scope denied: '{permission_key}'")
        # 2. RBAC fallback
        perms = AuthorizationService.get_permissions_for_identity(db, identity)
        if permission_key in perms:
            return True
        # Wildcard support (e.g., entity.write.*)
        parts = permission_key.split(".")
        for i in range(1, len(parts)):
            prefix = ".".join(parts[:i]) + ".*"
            if prefix in perms:
                return True
        raise AuthorizationError(
            f"Permission denied: {getattr(identity, 'display_name', identity)} "
            f"lacks permission '{permission_key}'"
        )
