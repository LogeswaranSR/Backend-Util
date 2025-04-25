from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages.base import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage

from ....db.firebase.firestore import FirestoreUtil

from datetime import datetime


class FirebaseMessageHistory(BaseChatMessageHistory):
    storage_path:  str
    key: str
    uid: str
    db_interface: FirestoreUtil

    def __init__(self, key: str, uid: str):
        print("KEY:", key)
        self.storage_path = "history"
        self.uid = uid
        self.key = key
        self.db_interface = FirestoreUtil()
        self.doc_ref = None
        self.db_data = None

    @property
    def messages(self):
        try:
            if self.doc_ref is None:
                self.doc_ref = self.db_interface.fetch_data(self.uid, self.storage_path, send_ref = True)
            snapshot = self.doc_ref.get()
            if snapshot.exists:
                self.db_data = snapshot.to_dict()
                messages = self.db_data[self.key]
                return self.messages_from_dict(messages)
            else:
                self.db_data = {self.key: []}
                self.doc_ref.set(self.db_data)
                return []
        except Exception as e:
            print(e)
            return []
    
    def add_message(self, message):
        message.timestamp = datetime.now()
        print(message, message.timestamp)
        self.add_messages([message])

    def add_messages(self, messages: list[BaseMessage]) -> None:
        for msg in messages:
            msg.timestamp = datetime.now()
        all_messages = list(self.messages) # Existing messages
        all_messages.extend(messages) # Add new messages

        serialized = self.messages_to_dict(all_messages)
        self.db_data[self.key] = serialized
        try:
           self.doc_ref.update(self.db_data)
        except Exception as e:
           print(e)
       

    def clear(self):
        try:
            prompts = self.db_data[self.key][:2]
            self.db_data[self.key] = prompts
            self.doc_ref.update(self.db_data)
        except Exception as e:
            print(e)

    def messages_from_dict(self, messages: dict[str, object]):
        final = []
        for message in messages:
            if message["role"] == "user":
                final.append(HumanMessage(message["content"], timestamp=message["timestamp"]))
            else:
                final.append(AIMessage(message["content"], timestamp=message["timestamp"]))
        return final

    
    def messages_to_dict(self, messages: list[BaseMessage]):
        dct_list = []
        for i in range(1, len(messages) + 1):
            message = messages[i-1]
            key = "user" if type(message) is HumanMessage else "chatbot"
            dct_list.append({"index":i, "role":key, "content":message.content, "timestamp":message.timestamp })
        return dct_list