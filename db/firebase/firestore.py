from firebase_admin import firestore

from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore import Client

from ...exception import MsgException

class FirestoreInstance:
    __instance: Client = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = firestore.client()
        return cls.__instance

class FirestoreUtil:
    '''
    Util class for Firestore Access
    '''
    def __init__(self):
        self.__db = FirestoreInstance()
        self.__users = self.__db.collection("users")
    
    def validate_user_role(self, email: str, role: str) -> str:
        query = self.__users.where(filter=FieldFilter("email", "==", email))
        docs = query.get()
        if len(docs) == 0:
            raise MsgException(
                "Invalid User!!",
                "User not found!! Please register!!",
                400
            )
        user_role = None
        for doc in docs:
            user_data = doc.to_dict()
            user_role = user_data.get("role", None)
        if(user_role != role):
            raise MsgException(
                "Invalid Login!!",
                "User role doesn't match!! Please login from proper interface.",
                406
            )
        return True
    
    def fetch_user_data(self, uid: str, send_ref: bool = False):
        """Fetch User data from Firestore

        Args:
            uid (str): User ID (for reference)
            send_ref (bool, optional): Boolean value for sending Doc reference or Data only; Set this to True in case of any updates required. Defaults to False.

        Returns:
            DocumentSnapshot | dict: Doc reference | Data retrieved from Firestore
        """
        ref: DocumentSnapshot = self.__users.document(uid).get()
        return ref if send_ref else ref.to_dict()
    
    def fetch_data(self, doc_id: str, collection: str, send_ref: bool = False) -> DocumentReference | dict:
        """Fetch data from Firestore

        Args:
            doc_id (str): Document ID (for reference)
            collection (str): Collection path ( must be in odd values)
            send_ref (bool, optional): Boolean value for sending Doc reference or Data only; Set this to True in case of any updates required. Defaults to False.

        Returns:
            DocumentReference | dict: Doc reference | Data retrieved from Firestore
        """
        ref: DocumentReference = self.__db.collection(collection).document(doc_id)
        return ref if send_ref else ref.get().to_dict()
    
    def fetch_email_by_username(self, username: str) -> str:
        """Fetch Email from Database based on provided username

        Args:
            username (str): Username to be searched for

        Raises:
            MsgException: In case Username is not found

        Returns:
            email: Email found
        """
        query = self.__users.where(filter=FieldFilter("username", "==", username))
        docs = query.get()
        email = None
        
        for doc in docs:
            user_data = doc.to_dict()
            email = user_data["email"]
        
        if(email == None):
            raise MsgException(
                "User not found!!",
                "Given username doesn't match to any user. Please check and try again!!",
                400
            )
        return email
    
    def fetch_user_data_by_user_id(self, user_id: int, org_id: int, send_ref_id: bool = False) -> dict[str, object] | str:
        '''
        Fetch user data by User ID and Organization ID; Use this to fetch UID from user ID as well. 
        '''
        query = self.__users.where(filter=FieldFilter("user_id", "==", user_id)).where(filter=FieldFilter("organization", "==", org_id))
        docs = query.get()
        user_data = None
        doc_id = None
        
        for doc in docs:
            user_data = doc.to_dict()
            doc_id = doc.id
        
        return doc_id if send_ref_id else user_data

    def insert_data(self, collection: str, doc_id: str | None, data: dict[str, object]) -> bool:
        '''
        To insert data to Firebase.

        Parameters
        ----------
        collection : str
            Collection path to which the data will be added. Note: The collection path must be in odd numbers; or else an Exception will be thrown.
        doc_id : str | None
            Document ID; Send one if you want your document to be named specifically. or else send None.
        data : dict[str, Any]
            Data to be inserted into Database.
        '''
        coll = self.__db.collection(collection)
        if doc_id is not None:
            doc_ref = coll.document(doc_id)
        else:
            doc_ref = coll.document()
        
        doc_ref.set(data, merge=True)
        return True
    
    def batch_insert_data(self, collection: str, doc_ids: list[str] | None, data: list[dict[str, object]]) -> bool:
        batch_ref = self.__db.batch()
        coll = self.__db.collection(collection)

        length = len(data)

        for i in range(length):
            doc_id = doc_ids[i] if doc_ids is not None else None
            if doc_id is not None:
                doc_ref = coll.document(doc_id)
            else:
                doc_ref = coll.document()
            
            batch_ref.set(doc_ref, data[i], merge=True)
        batch_ref.commit()

        return True
