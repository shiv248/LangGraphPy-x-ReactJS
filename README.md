![par-atom](https://raw.githubusercontent.com/shiv248/fluffy-dollop/refs/heads/master/Screenshot_2024-09-23_at_4.23.45_PM-removebg-preview.png)

# LangGraph Python Backend w/ React TypeScript Frontend

## TLDR
_LangGraph_ backend using FastAPI and websockets to communicate with _React_ showing model generating
responses and streaming, made easy as a template. Run via `pip install -r requirements.txt` then
`./start-local.sh --backend --build`. Check out more info below!

## Background
As _LangGraph_ develops there would be a need to establish what is an
optimal way approaching a seamless interaction between _LangGraph_ and any frontend
framework. A key aspect to UI in a chat setting with LLMs is seeing that the bot is
_Actively_ working on the response you sent it. Acknowledgement, be it a visual aid 
such as a spinner, a toast, a status bar, or streaming the tokens as they are being
generated. This is a playground template to merge core concepts between frontend
and backend to give a great user experience for someone who doesn't have technical
knowledge of LLMs and their limitations.

I found great success with going the streaming approach to represent the LLM
acknowledged my message and is generating a response. I used WebSockets to handle
the connection/communication between frontend and backend which allowed easy
integration of _LangChain_'s [asynchronous streaming events](https://python.langchain.com/docs/how_to/streaming/#using-stream-events) 
and _React_'s useEffect hook to facilitate waiting for response from bot and actively
streaming the tokens as they are being generated. I tried to make it as simple and
documented as I thought was necessary for anyone to just clone, start, and get going on
this project with a drop in replacement for your LangGraph runnable in `graph.py` and 
really only needing `useWebSocket.ts` implementation for any frontend.

## Project Overview
```
Project Tree
.
├── Dockerfile             # Shipable blueprint Dockerfile
├── Procfile               # web command to run on servers (PaaS eg. Heroku)
├── README.md
├── cust_logger.py         # Custom logger utility for logging for backend serving
├── frontend
│   ├── package.json       # Contains metadata and dependencies for React project
│   ├── public             # Default Create-React-App Public assets
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   ├── logo192.png
│   │   ├── logo512.png
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── src                # Source code for the React frontend
│   │   ├── App.css
│   │   ├── App.tsx        # Main App component in TypeScript
│   │   ├── components     # Demo components used in App.tsx
│   │   │   └── easter_egg # ssshhhh... try "LangChain"
│   │   │       ├── ee.css
│   │   │       └── ee.tsx
│   │   ├── index.tsx      # Entry point for the React app
│   │   ├── react-app-env.d.ts # Default from Create-React-App
│   │   └── services
│   │       └── useWebSocket.ts # WebSocket hook for real-time communication via WebSocket
│   └── tsconfig.json      # TypeScript configuration for the frontend
├── graph.py               # Simple LangGraph implementation
├── requirements.txt       # Python dependencies required for the backend project
├── server.py              # FastAPI implementation
└── start-local.sh         # Shell script to start the application locally (backend or frontend)
```

#### Communication
The WebSocket connection allows real-time, bidirectional communication between the React frontend
and a backend server, continuously receiving messages without having to reload or make repeated requests.
There are many ways to handle the data being sent across, could be the msg itself, a chunk of messages (msg_history),
or a structured format. I chose to go with the structured format since it allows the client and server to 
expect certain keys in a certain order and allows flexibility for future additions to the payload. I chose to use JSON
since it's the easiest to read and pickup, but you're free to use any other such as XML, YAML, CSV, Protobuff, BSON.
In short, there are predefined json structure that both sides are looking for, if there are certain criterias met throughout the exchange
from either side, it will trigger actions within that specific side. eg. if the event kind is `on_chat_model_stream` it should stream out
the response to the client, if the client receives any changes in socket connection, it will adjust and render/console.log accordingly.

Our communication exchanges:
![coms xc](https://raw.githubusercontent.com/shiv248/fluffy-dollop/refs/heads/master/par-atom.png)
Find out more about what each function does from the comments in the codebase.

#### Frontend
The Frontend has a few features to get the ball rolling:
- from the frontend you can tell that you're connected to the server via indicator
- there is multi-line typing (`Shift + Enter`) and normal `Enter` to send
- Automatic scrolling as the responses are generated
- The Websocket has an auto retry of reconnection and messages if the server is down
- stateless frontend, meaning messages are not stored frontend side and sent as `msg_history`, only single message is sent
- Explanation of how to use custom LangGraph events to trigger a component in Frontend side
  - try asking the model about LangChain or LangGraph! :D

#### Backend
I tried to keep the backend very slim while still being functional, it uses FastAPI 
and Uvicorn to handle asynchronous requests. Some Features:
- Simple FastAPI Implementation
  - serves static web files that are from `npm build`
  - allows flexability for `React Router`
  - simple websocket connection
- expressive logging
  - matching Uvicorn's logging format
  - `file_name:line_num` format for easy log tracing  
  - custom logging colors, so in any file you can set to a respective color
  - Example Log:
      ```
      INFO:     server.py:34    - {"timestamp": "YYYY-MM-DDTHH:MM:SS.MS", "uuid": "nearer-zebra-one-worker", "received": {"uuid": "oldest-honor-create-card", "message": "what is e?", "init": false}}
      INFO:     graph.py:86     - {"timestamp": "YYYY-MM-DDTHH:MM:SS.MS", "uuid": "nearer-zebra-one-worker", "llm_method": "on_chat_model_end", "sent": "2.718281828459045"}
      ```
  - in consistent logging format and output in JSON allowing easy import into a any observability system
  - designated by timestamp in timeseries, conversational UUID or llm function call.
- Simple Graph
  - this graph example is a generic call model without tool calling, but easily can be replaced with your graph
  - currently for simplicity used conversational UUID to designate threads for [memory persistence](https://langchain-ai.github.io/langgraph/how-tos/persistence/) using MemorySaver
  - This allows conversational history to be maintained within a Websocket channel on the Backend and client isn't bespoke to rendering and storing in case of data loss or refresh
- events handler to send websocket responses back to designated clients
  - This currently handles Chat Streaming and Custom events within your graph. eg to trigger a Frontend components or flag
    - using `adispatch_custom_event` and `astream_events`

### Lets Get Started

#### Automated Starting
I tried to make setup and running as simple as possible locally
This script is used to start the frontend and backend of the application. It accepts various command-line options to control which components to run and their respective configurations.

before you being please make sure you `pip install -r requirements.txt`, I recommend using your personal flavor of virtual env, I didn't automate pip setup due to user assumption.
```
# required libraries
fastapi              # Fast web framework to handle our APIs
uvicorn              # ASGI server for serving FastAPI applications
websockets           # core WebSocket server and client library
python-dotenv        # reads key-value pairs from a `.env` file and sets them as environment variables
langchain-fireworks  # LangChain x Fireworks implementation to use Firework.AI's ChatModel with Langchain
langgraph            # An awesome talking parrot that shoots webs :D
colorama             # used for coloring logs
```

#### `./start-local.sh` Options
Please read the `start-local.sh` to understand what alias commands it is doing under the hood
- **`--frontend`**:
    - Starts the frontend application.
    - Example:
      ```bash
      ./start-local.sh --frontend
      ```

- **`--backend`**:
    - Starts the backend application.
    - Example:
      ```bash
      ./start-local.sh --backend
      ```

- **`--build`** optional flag:
    - Builds the frontend application before starting the backend. This option is only relevant to the backend.
    - Example:
      ```bash
      ./start-local.sh --backend --build
      ```

- **`--frontend-port <port>`** optional flag:
    - Specifies the port on which the frontend application should run. The default port is `3000`.
    - Example:
      ```bash
      ./start-local.sh --frontend --frontend-port 4000
      ```

- **`--backend-port <port>`** optional flag:
    - Specifies the port on which the backend application should run. The default port is `8000`.
    - Example:
      ```bash
      ./start-local.sh --backend --backend-port 9000
      ```

#### Starting the Application Manually
If you prefer not to use the `start-local.sh` script, you can manually start the frontend and backend components using the following steps.
I would recommend using 2 different terminal tabs.
- For the **frontend**, navigate to the `frontend` directory and install the required packages and run with your flavor of node package manager:
     ```bash
     cd frontend
     npm install
     npm run
     ```
- For the **backend**, in root of project folder.
   ```bash
  pip install -r requirements.txt
  cd frontend
  npm install
  npm build
  cd ..
  uvicorn server:app --host 0.0.0.0 --port 8000 --reload
   ```

### Demo
As we can see, even if two people are typing to the server, it is able to handle it in a non-blocking fashion
and be able to serve both clients with no loss in response throughput

### Deployment
There is a Dockerfile and Procfile, both can be used to run the server used as a standalone docker container or 
your own solution, would recommend docker-compose for easy deployment on kubernetes via helm charts and easy replicas with VTCL/HZTL scaling.
Remember to handle ports and SSL if your solution requires it.

**NOTE - This server backend is not secure**, it currently isn't using WebSocket Secure due to localhost being http and lack of  core securities
due to easy of local running. I would recommend adding something like this to the frontend:
```typescript jsx
const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const wsUrl = `${wsProtocol}://${window.location.hostname}/ws`;
```
also would advise adding origin checking for incoming server requests and securing your API using JWT token, OAuth's Bearer Token, API Keys ect.
possibly rate-limiting WebSocket connections or handling reconnections securely, preventive actions for DDOS.

### Thoughts and Future Improvements
This was a fun implementation mixing two technologies you want together but not clearly defined, especially in 
a scenario that both are used without limitations to each other.

There are many improvements that thought could be done, but they are not implemented due to potential lockout and flexibility
of future users for simplicity’s sake.
I would be willing to make new template for different use-cases or add to this repo, possibly:
- tool calling is viable through any graph in LangGraph but its not handled as a frontend visual update
- conversations stored in-memory => dedicated network database solution
- sharing conversation or looking up by conversation ID
- handle grouping conversation by user would need some sort of distinction between users.
- K8s docker-compose setup