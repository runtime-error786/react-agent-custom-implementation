from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import re
import httpx
from groq import Groq

os.environ['GROQ_API_KEY'] = "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"  
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class Agent:
    def __init__(self, client: Groq, system: str = "") -> None:
        self.client = client
        self.system = system
        self.messages: list = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = self.client.chat.completions.create(
            model="llama3-70b-8192", messages=self.messages
        )
        return completion.choices[0].message.content

system_prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

wikipedia:
e.g. wikipedia: Django
Returns a summary from searching Wikipedia

Always look things up on Wikipedia if you have the opportunity to do so.

Example session:

Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: wikipedia: France
PAUSE 

You will be called again with this:

Observation: France is a country. The capital is Paris.
Thought: I think I have found the answer
Action: Paris.
You should then call the appropriate action and determine the answer from the result

You then output:

Answer: The capital of France is Paris

Example session

Question: What is the mass of Earth times 2?
Thought: I need to find the mass of Earth on Wikipedia
Action: wikipedia : mass of earth
PAUSE

You will be called again with this: 

Observation: mass of earth is 1,1944×10e25

Thought: I need to multiply this by 2
Action: calculate: 5.972e24 * 2
PAUSE

You will be called again with this: 

Observation: 1,1944×10e25

If you have the answer, output it as the Answer.

Answer: The mass of Earth times 2 is 1,1944×10e25.

Now it's your turn:
""".strip()

def wikipedia(q):
    return httpx.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query",
        "list": "search",
        "srsearch": q,
        "format": "json"
    }).json()["query"]["search"][0]["snippet"]

def calculate(operation: str) -> float:
    return eval(operation)

class QueryAgentView(APIView):
    def post(self, request):
        query = request.data.get("query", "")
        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)

        agent = Agent(client=client, system=system_prompt)
        max_iterations = 10
        next_prompt = query

        for _ in range(max_iterations):
            result = agent(next_prompt)

            if "PAUSE" in result and "Action" in result:
                action = re.findall(r"Action: ([a-z_]+): (.+)", result, re.IGNORECASE)
                if action:
                    chosen_tool = action[0][0]
                    arg = action[0][1]

                    if chosen_tool == "wikipedia":
                        result_tool = wikipedia(arg)
                    elif chosen_tool == "calculate":
                        result_tool = calculate(arg)
                    else:
                        return Response({"error": "Tool not found"}, status=status.HTTP_400_BAD_REQUEST)

                    next_prompt = f"Observation: {result_tool}"
                else:
                    next_prompt = "Observation: Tool not found"
                continue

            if "Answer" in result:
                return Response({"answer": result}, status=status.HTTP_200_OK)

        return Response({"error": "No valid answer found"}, status=status.HTTP_400_BAD_REQUEST)
