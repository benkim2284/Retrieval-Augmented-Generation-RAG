from langchain_openai import ChatOpenAI


api_key = "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"

prompt_template = '''
You are a lab guide generator. Your response should be only the latex lab guide and nothing else. 
In the latex lab guide itself, make sure the only packages you use are "amsmath" and "amsfont” and do NOT use any other latex packages,
but make sure that the lab guide is visually appealing and is suited for data collection/analysis if necessary. 
Your response should not start with "```latex" but should directly start with the content of the latex lab guide.
Generate me a lab guide that has the following: an introduction, list of materials and equipments, detailed procedures, safety precautions, data collection and analysis, and conclusion/questions. 
The lab guide should achieve the learning objectives of "students should understand surface tension." 
THere should be an emphasis on the skills of "data collection, measurement, data analysis"
'''

model = ChatOpenAI(openai_api_key = api_key, temperature = 0, model="gpt-4o")
model_response = model.invoke(prompt_template).content
print(model_response)
