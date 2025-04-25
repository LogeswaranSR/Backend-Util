from langchain_core.output_parsers import BaseOutputParser

## Huggingface Libraries
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

## Third-Party Integrations
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

from .parsers import ChatOutputParser, DeepseekOutputParser

class LLMManager:
    def load_default(self, key: str):
        if key not in self.Constants.default_settings:
            raise Exception("No such key available!! Please check once again!!")
        model_id = self.Constants.default_settings[key]["llm"]
        llm = self.load_llm(model_id, self.Constants.default_settings[key]["interface"])
        parser = self.load_parser_from_settings(key)
        return llm, parser
    
    def load_llm(self, model_id: str, interface: str):
        if interface == "huggingface":
            llm = HuggingFaceEndpoint(
                repo_id=model_id,
                task="text-generation",
            )
            chat = ChatHuggingFace(llm=llm, verbose=False)
            return chat
        elif interface == "ollama":
            return ChatOllama(
                model=model_id,
            )
        elif interface == "groq":
            return ChatGroq(
                model_name=model_id
            )
        else:
            raise Exception("No such interface available!! Please check once again!!")
    
    def load_parser_from_settings(self, key: str) -> BaseOutputParser:
        default_parser: BaseOutputParser = self.Constants.default_settings[key]["parser"]
        return default_parser()
    
    class Constants:
        llm_models = {
            "deepseek-r1:1.5b": {
                "huggingface": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
                "ollama": "deepseek-r1:1.5b"
            },
            "deepseek-r1:32b": {
                "groq": "deepseek-r1-distill-qwen-32b"
            },
            "mistral-7b": {
                "huggingface": "mistralai/Mistral-7B-Instruct-v0.2"
            },
            "llama:70b": {
                "groq": "llama3-70b-8192"
            },
            "phi": {
                "huggingface": "microsoft/phi-2",
                "ollama": "phi"
            },
            "falcon3:3b": {
                "huggingface": "tiiuae/Falcon3-3B-Base",
                "ollama": "falcon3:3b"
            },
            "smollm": {
                "huggingface": "HuggingFaceTB/SmolLM-1.7B",
                "ollama": "smollm"
            },
            "gemma:2b": {
                "ollama": "gemma:2b"
            },
            "stablelm-zephyr": {
                "ollama": "stablelm-zephyr"
            }
        }

        default_settings = {
            "virtual_assistant":{
                "interface": "groq",
                "llm": llm_models["llama:70b"]["groq"],
                "parser": ChatOutputParser
            },
            "enquiry_chatbot":{
                "interface":"ollama",
                "llm": llm_models["deepseek-r1:1.5b"]["ollama"],
                "parser": DeepseekOutputParser
            }
        }