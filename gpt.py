from langchain_openai import ChatOpenAI


api_key = "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"

prompt_template = '''
How can i make it so that I have latex rendered text with <Latex> using the React-latext-next npmp package but inside of a text box that is editable yet still rendered properly. I want it so that the users don't have to work with the latex code, but can jsut the edit the latex-rendered worksheet. I am trying to create the most simple user experience for the users and I am assuming that they don't know latex. '''

model = ChatOpenAI(openai_api_key = api_key, temperature = 0, model="gpt-4o")
model_response = model.invoke(prompt_template).content
print(model_response)
