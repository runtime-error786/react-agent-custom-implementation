# Implemetaion of reAct agent
## Project Description
This project is a Django REST Framework API designed to process user queries and return answers using a custom agent that leverages the Groq API. The agent operates in a loop of Thought, Action, PAUSE, and Observation to intelligently respond to user inquiries. It can perform calculations and fetch information from Wikipedia to provide accurate answers.

## Key Features
 Query Processing: Accepts user queries and returns informative responses.
 Dynamic Actions: Utilizes defined actions such as calculations and Wikipedia lookups to derive answers.
 Structured Responses: Returns structured JSON responses with either the answer or error messages for invalid queries.
This API serves as a robust tool for answering diverse questions, making it useful for applications that require dynamic information retrieval and processing.
