import json
import httpx
from urllib.parse import quote
import google.generativeai.protos as protos

DECISION_PROMPT = """Determine the appropriate action for the following user query. The possible actions are:

- 'smalltalk' if the question is a greeting or compliment only. The question is not related to sound or any calculations.
- 'vectordb' if the query is not a greeting and is remotely related to the topic of sound, including questions about the speed of sound in different media or at different temperatures and pressures. If the query involves calculations but is missing necessary information, also use 'vectordb'. Do not perform any calculations.
- 'sound_calculator' if the query is related to calculating the speed of sound, wavelength, or frequency, given the other two parameters. The calculator expects frequency in Hz, speed in m/s, and wavelength in m. Provide the known values and indicate which parameter is unknown.
- 'unknown' if the query is not related to any of the above, return 'unknown'.

You need to think step by step to determine which action to take. 
At the end of the response, append the action name and the parameters required for the action in the following format: <your reasoning>. Final action: <action_name>, <parameters>.
If there are no parameters, use NONE.
Make sure to follow the correct format.

For example:
Query: Hi!
Response: The query is a greeting. Final action: smalltalk, NONE.

Query: What is the capital of France?
Response: The query is not a greeting and is not related to sound and is a general knowledge question. Final action: unknown, NONE.

Query: What is the speed of sound in air?
Response: The query does not contain any specific values for speed of sound, wavelength, or frequency, but is related to the topic of sound. Final action: vectordb, NONE.

Query: What is the speed of sound in air at 20 degrees Celsius?
Response: The query contains a specific value for temperature and is related to the topic of sound. Final action: vectordb, NONE.

Query: What is the wavelength of a sound wave with a frequency of 440 Hz and a speed of sound of 343 m/s?
Response: The query contains specific values for frequency and speed of sound and is related to the topic of sound. Here, the unknown parameter is wavelength. The known parameters are frequency with a value of 440 Hz and speed of sound with a value of 343 m/s. Final action: sound_calculator, {"frequency": "440", "speed": "343", "unknown": "wavelength"}.

Query: What is the frequency of a sound wave with a wavelength of 0.75 m and a speed of sound of 343 m/s?
Response: The query contains specific values for wavelength and speed of sound and is related to the topic of sound. Here, the unknown parameter is frequency. The known parameters are wavelength with a value of 0.75 m and speed of sound with a value of 343 m/s. Final action: sound_calculator, {"wavelength": "0.75", "speed": "343", "unknown": "frequency"}.

Query: What is the wavelength if the speed is 300?
Response: The query mentions speed but is missing the frequency.  It's related to sound calculations, but insufficient information is provided. Final action: vectordb, NONE.

Query: What's the speed of sound in water?
Response: The query asks about the speed of sound in a specific medium (water). Final Action: vectordb, NONE.

Query: What is the frequency of a sound wave with a wavelength of 2e-2 m and a speed of sound of 343 m/s?
Response: The query contains specific values for wavelength and speed of sound and is related to the topic of sound. Here, the unknown parameter is frequency. The known parameters are wavelength with a value of 0.02 m (2e-2 m) and speed of sound with a value of 343 m/s.  Final action: sound_calculator, {"wavelength": "0.02", "speed": "343", "unknown": "frequency"}.

Query: INSERT_QUERY_HERE
Response:"""

proxy = "http://localhost:8000"

decision_generation_config = {
  "temperature": 1,
  "max_output_tokens": 2048,
}


def sound_calculator(query: str) -> str:
    # to handle if the query contains backslashes
    if '\\' in query:
        query = query.replace('\\', '')
    
    structured_query = json.loads(query)
    unknown = structured_query['unknown']
    try:
        if unknown == "wavelength":
            speed = float(structured_query['speed'])
            frequency = float(structured_query['frequency'])
            wavelength = speed / frequency
            return f"The wavelength is {wavelength} meters."
        
        elif unknown == "frequency":
            speed = float(structured_query['speed'])
            wavelength = float(structured_query['wavelength'])
            frequency = speed / wavelength
            return f"The frequency is {frequency} Hz."
        
        elif unknown == "time_period":
            frequency = float(structured_query['frequency'])
            time_period = 1 / frequency
            return f"The time period is {time_period} seconds."
        
        elif unknown == "speed":
            wavelength = float(structured_query['wavelength'])
            frequency = float(structured_query['frequency'])
            speed = wavelength * frequency
            return f"The speed is {speed} m/s."

        else:
            return "Invalid output type. Please choose from 'wavelength', 'frequency', or 'time_period'."
        
    except KeyError:
        return "Invalid input. Incorrectly mapped parameters."
    
    except ZeroDivisionError:
        return "Invalid input. Please provide valid values for the parameters."
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

# def generate_model_response(model, query: str) -> str:
    
#     try:
#         response = model.generate_content(DECISION_PROMPT.replace("INSERT_QUERY_HERE", query)).text
#         return response
#     except Exception as e:
#         return f"An error occurred: {str(e)}. The request ({query}) could not be processed."

def generate_model_response(chat_session, query: str) -> str:
    
    try:
        response = chat_session.send_message(DECISION_PROMPT.replace("INSERT_QUERY_HERE", query)).text
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}. The request ({query}) could not be processed."

def action_parser(response):
    action = response.strip().lower()
    action = action.split("final action:")[-1]
    action, params = action.split(",", 1)
    action = action.strip() 
    print("Taking action:", action)
    params = params.strip()

    return action, params
    
def initiate_smalltalk(chat_session, question):
    try:
        response = chat_session.send_message(question).text
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}."
    
def add_history(chat_session, response):
    chat_session.history.append(protos.Content({'parts': [{'text': response}], 'role': 'model'}))

async def determine_action_from_query(chat_session, query):
    action, params = action_parser(generate_model_response(chat_session, query))
    if action == 'smalltalk':
        response = initiate_smalltalk(chat_session, query)
        return response
    
    elif action == 'sound_calculator':
        response = sound_calculator(params)
        add_history(chat_session, response)
        return "Using my calculator, I calculate that: " + response
    
    elif action == 'unknown':
        response = "I am sorry, I am only allowed to possess limited knowledge :("
        add_history(chat_session, response)
        return response

    else: 
        async with httpx.AsyncClient() as client:
            rag_response = await client.get(f"{proxy}/rag", params={"query": query})
        response = rag_response.json()["response"] 
        add_history(chat_session, response)
        response =  "Using the context provided to me, I found the following information: " + response
        return response
    