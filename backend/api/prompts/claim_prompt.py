from langchain_core.prompts import ChatPromptTemplate

claim_prompt = ChatPromptTemplate.from_messages([
    ("system", "Compose a single claim from the following text. The claim should be concise and capture the main point of the text, and can be multiple parts if needed: {content}"),
    ("human", "{content}")
])

