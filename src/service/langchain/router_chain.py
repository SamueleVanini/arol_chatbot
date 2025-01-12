from langchain_core.language_models import BaseChatModel

from service.langchain.prompt.prebuilt_prompt import get_system_prompt, SystemPromptType
from service.langchain.prompt.prompt_template import get_template
from service.langchain.chain_configs import ChainType
from typing import List, Optional
from pydantic import BaseModel, Field
from service.langchain.routable_chain import RoutableChainFactory
from typing import Literal
from langchain_core.runnables import RunnableLambda, RunnableConfig, RunnablePassthrough


class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource based on content and context analysis."""

    datasource: Literal["machines_catalog", "arol_company_information", "chat_history"] = Field(
        ...,
        description="""Choose the most appropriate datasource for the question:
        - 'machines_catalog': ONLY for completely self-contained questions about specific machines, with explicit machine names and no pronouns or references to previous conversation
        - 'arol_company_information': ONLY for completely self-contained questions about Arol as a company, with no pronouns or references to previous conversation
        - 'chat_history': For ANY questions that:
            * Use pronouns (it, that, this, etc.)
            * Reference previous conversation
            * Ask about the conversation itself
            * Are incomplete without context
            * Create any doubt about whether previous context is needed
        When in doubt, choose chat_history""",
    )


class RoutingLLMChain:

    def __init__(self, llm: BaseChatModel):
        # LLM with function call
        self.llm = llm
        self.router = self._get_router()
        self.llm_routes: List[RoutableChainFactory] = []

    def _get_router(self):
        structured_llm = self.llm.with_structured_output(RouteQuery)
        # Prompt
        system_routing_template = get_template(
            system_prompt=get_system_prompt(SystemPromptType.QUERY_ROUTING),
            chain_type=ChainType.QA
        )
        # Define router
        self.router = system_routing_template | structured_llm
        return self.router

    def add_routes(self, llm_routes: List[RoutableChainFactory]):
        self.llm_routes.extend(llm_routes)

    def _navigate_to_route(self, info: dict[str, RouteQuery]):
        if not self.llm_routes:
            raise ValueError("No routes available")
        for route in self.llm_routes:
            if route.name in info['datasource'].datasource.lower() or info['datasource']:
                print("this is the chain : ",route.name)
                return route.main_chain
        raise ValueError("Route not found")

    def answer_question(self, question: str,config: Optional[RunnableConfig] = None) -> str:
        if not self.llm_routes:
            raise ValueError("No routes available")

        unified_chain = (
                {"datasource": self.router,"input": lambda x: x["input"]}
                | RunnableLambda(self._navigate_to_route)
        )
        result = unified_chain.invoke({"input": question},config)
        return result['answer']
