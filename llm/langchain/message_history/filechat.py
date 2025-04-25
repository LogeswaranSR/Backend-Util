from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages.base import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage

import json
import os


class FileChatMessageHistory(BaseChatMessageHistory):
    storage_path:  str
    session_id: str

    def __init__(self, storage_path, session_id):
        self.storage_path = storage_path
        self.session_id = session_id

    @property
    def messages(self):
        try: 
            with open(os.path.join(self.storage_path, self.session_id+".json"), 'r') as f:
                messages = json.loads(f.read())
            return self.messages_from_dict(messages)
        except FileNotFoundError:
            return []
    
    def add_message(self, message):
        self.add_messages([message])

    def add_messages(self, messages: list[BaseMessage]) -> None:
       all_messages = list(self.messages) # Existing messages
       all_messages.extend(messages) # Add new messages

       serialized = self.messages_to_dict(all_messages)
       # Can be further optimized by only writing new messages
       # using append mode.
       with open(os.path.join(self.storage_path, self.session_id+".json"), 'w') as f:
           json.dump(serialized, f)

    def clear(self):
       with open(os.path.join(self.storage_path, self.session_id+".json"), 'w') as f:
           f.write("[]")

    def messages_from_dict(self, messages):
        final = []
        for message in messages:
            if message["role"] == "user":
                final.append(HumanMessage(message["content"]))
            else:
                final.append(AIMessage(message["content"]))
        return final

    
    def messages_to_dict(self, messages):
        dct_list = []
        for i in range(1, len(messages) + 1):
            message = messages[i-1]
            key = "user" if type(message) is HumanMessage else "chatbot"
            dct_list.append({ "key":i, "index":i, "role":key, "content":message.content })
        return dct_list