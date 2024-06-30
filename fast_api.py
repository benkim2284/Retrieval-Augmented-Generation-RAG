# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from typing import Union
from fastapi import FastAPI
from loader import hello, generate_worksheet, generate_lab
from ai_audio import run_voice_agent

# Flask constructor takes the name of 
# current module (__name__) as argument.
app = FastAPI()

allowed_origin = 'http://localhost:3000'

cors = CORS(app, resources={r"/*": {"origins": allowed_origin}})

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.get('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return hello()

@app.get("/generate/worksheet", methods=['POST'])
def generate_worksheet_endpoint():
    data = request.get_json()
    grade = data.get('grade')
    instructions = data.get('instructions')
    context = data.get('context')
    print(grade)
    print(instructions)
    print(context)

    if not grade or not instructions:
        return jsonify({'error': 'Missing grade or instruction specification'}), 400

    result = generate_worksheet(user_grade=grade, user_instructions=instructions, user_context=context)

    # Return the result as a JSON response
    
    return result

@app.route("/generate/lab", methods=['POST'])
def generate_lab_endpoint():
    data = request.get_json()
    grade = data.get('grade')
    objectives = data.get('objectives')
    skills = data.get('skills')
    context = data.get('context')

    print(grade)
    print(objectives)
    print(skills)
    print(context)

    result = generate_lab(user_grade=grade, user_objectives=objectives, user_skills=skills, user_context=context)

    return result

@app.route("/generate/voice_agent", methods=['POST'])
def generate_voice_agent():
    print("hello")

    run_voice_agent()

    return "voice happened"


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(port=3006, debug=True)