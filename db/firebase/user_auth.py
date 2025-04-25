from firebase_admin import auth

from .firestore import FirestoreUtil
from ...exception import ExceptionUtil, MsgException

class FirebaseAuthentication: ## Inherit from DRF Authentication class if using DRF
    def __init__(self):
        super().__init__()
        self.allowed_paths = ["/validate-user", "/login", "/test", "/register", "/task"]

    def authenticate(self, request):
        """Firebase Authentication for Requests

        Args:
            request (django.http.HttpRequest or Similar Class): Request Object obtained from Django or DRF

        Raises:
            Exception: Authentication Exceptions.

        Returns:
            tuple: two-tuple of (user, token)
        """        
        user = { "uid": None, "is_authenticated":False }

        ## Validate for allowed paths
        path = request.path
        data = request.data
        if path in self.allowed_paths:
            if path == "/test" and not data.get("is_development", False):
                raise ExceptionUtil.unauthorized_exception("This is an Development Endpoint. Do not access it without permission.")
            user["is_authenticated"] = True
            return (user, None)
        
        ## Check for Token in Request Headers
        token = request.headers.get("Authorization")
        if not token and path not in self.allowed_paths:
            raise ExceptionUtil.unauthorized_exception("No Authentication provided")
        token = token[7:]
        
        ## User Validation from Firebase
        try:
            decoded_token = auth.verify_id_token(token) ## Only UID and Auth data is decoded from this.
            uid = decoded_token["uid"]
            user["uid"] = uid
            user["is_authenticated"] = True
            return (user, None)
        except auth.InvalidIdTokenError:
            raise ExceptionUtil.unauthorized_exception("Invalid Token")
        except auth.ExpiredIdTokenError:
            raise ExceptionUtil.unauthorized_exception("Token Expired")
        except Exception as e:
            print(f"Authentication error: {e}")
            return ExceptionUtil.unauthorized_exception("Authentication Failed")

class UserRegistration:
    def __init__(self):
        self.db_interface = FirestoreUtil()
    
    def register_user(self, data: dict):
        try:
            org_id = str(data.get("organization", "freeplan"))
            role: str = data["role"]
            role = role.lower()

            ## Guardian / Doctor Data addition
            if(role != "patient"):
                data["patients"] = []

            ## User ID Creation
            print("Creating User ID...")
            org_data_ref = self.db_interface.fetch_data(org_id, "organizations", send_ref=True)
            org_data = org_data_ref.get().to_dict()
            print("Org Data:", org_data)

            user_id = org_data["user_ids"][role]
            org_data["user_ids"][role] += 1
            data["user_id"] = user_id

            ## User Creation
            email, password = data["email"], data["password"]
            user = auth.create_user(
                email=email,
                password=password
            )
            uid = user.uid
            org_data["active_users"] += 1

            ## DB Updates
            print("Adding Data...")
            del data["password"]
            self.db_interface.insert_data("users", uid, data)
            org_data_ref.update(org_data)
        except Exception as e:
            print("Something went wrong while creating user!!")
            print(e)
            raise MsgException(
                "Error!!",
                "Somethong went wrong while creating user!!",
            )
