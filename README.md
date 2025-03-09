# The Harmony Tutor
## Architecture 
- 1: Building a RAG system : Build a RAG system that can generate responses for a given query and context and host it using a FASTAPI server.
- 2: Extending the RAG system to develop an agent that can answer questions selectively based on the context and query. The agent should be able to decide when to call the RAG system and when to answer the question directly.
- 3: Giving a voice to the agent.

The implementation details are mentioned in the README.md file in the respective folders.
**Note**: 

- This implementation can be done using any LLM model, but for this assignment, we use the Gemini series of models by Google, using their free API.
- Sentence embeddings are generated using the ChromaDB library using the default `all-MiniLM-L6-v2` model, which is very small.
- Hence, this implementation works smoothly on CPUs and does not require a GPU.

## Directory Structure
```
.
├── README.md
├── backend
│   ├── README.md
│   ├── agent_utils.py
│   ├── main.py
│   ├── rag_utils.py.py
│   └── TTS.py
│
└── frontend
    ├── README.md
    └── src
        ├── App.tsx
        └── index.tsx 
```

## Instructions to run the code
- Create a new environment using python. Install the required packages using the requirements.txt file and activate the environment.
    ```bash
    python3 -m venv myenv
    pip install -r requirements.txt
    source myenv/bin/activate
    ```

- Export the neccessary environment variables.
    ```bash
    export GEMINI_KEY=<your_gemini_api_key>
    export SARVAM_KEY=<your_sarvam_api_key>
    ```

- Run the backend and frontend servers using the details mentioned in the respective README.md files of the backend and frontend folders.

---


## Ideation
I created an agent which can run using any LLM instead of being limited to Langchain Tool supported models. The agent can perform various actions depending on the query given by the user.

**Note**: Throughout the implementation, we use the Gemini series of models by Google, as they are free. Running a local LLM was not feasible due to the unavailability of compute.

- Part 1: 
    * Using **PyPDF2** for extracting text from PDFs.
    * Using **ChromaDB** to generate and store sentence embeddings in a persistent vector database.
    * Given a query, the system retrieves the top-k most relevant1 sentences from the database. This list of sentences is then concatenated to form the context.
    * Using **Gemini-1.5-flash-8b**, the query is answered using the context and returned as a response.

- Part 2:
    * The agent utilizes a **Gemini-1.5-flash-002** model for making a decision to choose 1 of the 4 options:
    * Identify the query as a greeting and respond with a greeting.
    * Identify the query as a question related to sound and answer it using the RAG system.
    * Identify the query as a mathematical question relating to finding the value of either wavelength, frequency, or speed of sound given the other two values, and pass it to the sound calculator.
    * Identify the query as a non-sound related question and inform the user that the agent cannot answer the question.

- Part 3:
    * The agent uses the `Sarvam.ai` TTS system to convert the response to speech in the form of a base64 encoded string.
    * This string is then sent to the frontend.

