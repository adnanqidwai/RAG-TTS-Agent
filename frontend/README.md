# Frontend for the Harmony Tutor

## Running the frontend
Run the following commands to install the dependencies:
```bash
npm install
```

Run the following command to start the frontend:
```bash
npm start
```

This will start the frontend on `http://localhost:3000`.

## Implementation
This is a basic frontend application to access the agent which is provided by the backend. The frontend is built using TypeScript, React, and Material-UI. The frontend provides a simple interface to interact with the agent. The user can input a query and get a response from the agent. The response initially comes in the form of text, but can be converted to speech using the *TTS endpoint* provided by the backend. These audio outputs are cached for future or repeated use. 