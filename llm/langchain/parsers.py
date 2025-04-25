from langchain_core.exceptions import OutputParserException
from langchain_core.output_parsers import BaseLLMOutputParser, BaseOutputParser
from langchain_core.outputs import ChatGeneration, Generation

class ChatOutputParser(BaseLLMOutputParser):
    def parse_result(self, result: list[Generation], *, partial: bool = False):
        """Parse a list of model Generations into a specific format.

        Args:
            result: A list of Generations to be parsed. The Generations are assumed
                to be different candidate outputs for a single model input.
                Many parsers assume that only a single generation is passed it in.
                We will assert for that
            partial: Whether to allow partial results. This is used for parsers
                     that support streaming
        """
        if len(result) != 1:
            raise NotImplementedError(
                "This output parser can only be used with a single generation."
            )
        generation = result[0]
        if not isinstance(generation, ChatGeneration):
            # Say that this one only works with chat generations
            raise OutputParserException(
                "This output parser can only be used with a chat generation."
            )
        content = generation.message.content
        content = content.strip()
        if "AI:" not in content and "Human:" not in content:
            ## Cut the content if it is generated too long.
            if "\n" in content:
                content = content.split("\n")[0]
            return content.strip()
        ## Remove generated conversation from the response
        human_index = content.index("Human:")
        ai_index = content.index("AI:")
        index = min(human_index, ai_index)
        return content[:index].strip()

class DeepseekOutputParser(BaseOutputParser):
    def parse(self, result: list[Generation], *, partial: bool = False):
        """Parse a list of model Generations into a specific format.

        Args:
            result: A list of Generations to be parsed. The Generations are assumed
                to be different candidate outputs for a single model input.
                Many parsers assume that only a single generation is passed it in.
                We will assert for that
            partial: Whether to allow partial results. This is used for parsers
                     that support streaming
        """
        if type(result) is not str:
            if len(result) != 1:
                raise NotImplementedError(
                    "This output parser can only be used with a single generation."
                )
            generation = result[0]
            if not isinstance(generation, ChatGeneration):
                # Say that this one only works with chat generations
                raise OutputParserException(
                    "This output parser can only be used with a chat generation."
                )
            content = generation.message.content
        else:
            content = result
        start_idx = content.index("<think>")
        end_idx = content.index("</think>")

        think_cloud = content[start_idx + 7: end_idx]
        print("Think Cloud:", think_cloud)
        response = content[end_idx + 8: ]

        return response.strip()