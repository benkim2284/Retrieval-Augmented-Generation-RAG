# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, request, jsonify
from flask_cors import CORS
from loader import hello, generate_worksheet

# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)

allowed_origin = 'http://localhost:3000'

cors = CORS(app, resources={r"/*": {"origins": allowed_origin}})

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return hello()

@app.route("/generate/worksheet", methods=['POST'])
def addNum():
    data = request.get_json()
    grade = data.get('grade')
    instructions = data.get('instructions')
    context = data.get('context')
    print(grade)
    print(instructions)
    print(context)

    if not grade or not instructions:
        return jsonify({'error': 'Missing grade or instruction specification'}), 400

    result = generate_worksheet(grade, instructions, context)

    # Return the result as a JSON response
    
    return result


# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(port=3006, debug=True)