This project is a mockup frontend where I will be implementing AI to further extent this POC. 

Check the current frontend, check the readme and use playwright to explore the frontend. For now nothing works and the folders and PDFs do not work, everything is visual. The intention is to extend this frontend into a working POC with AI services, real documents and some other AI working in the background. 

AI services: 
The AI services are: 

1.- Google ADK backend single agent to read the document where the user is and update the form on the right side of the web page. The chat interface is for reading and exploring the document, translate and answer questions that the user may have. The context for the agent is the current document. Gemini accepts PDFs by default, so that shouldn't be an issue. The other context is a cascading inherited context that should come from the project and then from the current folder. The project/case has already a context and the folder also has a context. For now don't worry about it, just note it. So there should be a class that inherits context depending on the user position. When exploring go to a document to understand how this could be implemented. 

2.- Google ADK should have another agent (I need to separate them by design, but assess this decision, they are isolated and have nothing to do with each other). It can also be a langgraph flow, but assess if its better to simply use Google ADK since I will be using that already for the AI service 1. 

The functionality for this second service is adding new fields (with semantic metadata so that the other agent can parse data into the fields, starting form the document). Adding new fields should be possible from the admin view (see the toggle button for changing between user and admin view). In the admin view there should be a space for introducing natural language text requesting new fields for a specific form. For example suer could request a new text field or option field, the agent should then go through a process to change and version the current form. Respect the current page style, and propose the best UX for adding this functionality that I'm describing. No database is needed for now, store everything locally. The forms shouldn't save information anywhere, but the parsing data from document and adding fields should be possible. Important to use Kolibri components (https://github.com/public-ui). I have a proposal with langgraph for this. Check the word document named langgraph-flow.docx in this project. That is just a proposal, understand and assess the requirement to implement it. Use Playwright if necessary to better understand how to do this. 

For building requirements I need you to be extra analytical and use playwright to navigate to the UI (first use npm run dev to be able to navigate to the localhost and see the app running) also use the code graph over "docs/code-graph/code-graph.json" or/and use the mcp for code-graph to query and see relationships that may affect how this requirements are implemented. 

The document describes a complex process, as an MVP is enough to simplify it as much as possible to add some basic fields to any form. As you can see there is only one form per case and the form isn't changing as the user navigates to other folders. The form is at the CASE level, not the folder level. Each case has ONE form template (e.g., "German Integration Course Application" with 7 fields).

Key points about forms:
- Forms are per CASE, not per folder
- The same form persists when navigating between folders within a case
- Different cases can have different form data but use the same form template
- The AI can fill the form from documents in any folder 

Add this as a new tab in the admin view besides "Forms" tab. There is already an easy add fields in admin view, but an AI one is also needed. 


Extra info: 
This is a POC that will be developed in the same contained docker, so don't worry about security, however the project has to be well organized and should be modular. 


Additional information: 
For this additional info, please considere to ask questions about other functionalities after your exploration. You will see other buttons like translate and anonymize, don't worry about that for now, I will implement those requirements after. For this first sprint is very important to add those 2 AI services that I mentioned. 

Replace the current files with text files, but leave the same name, I will eventually replace with actual PDF documents. So the AI should get the text as context when selecting the file, here I expect to ask questions about it only at this point, so the agent should only have instructions to answer questions regardless of the language from document and/or user. The agent for this should have a tool to check the parallel form attached to the current folder and parse information into it (fill up the form). 

For the context. Please considere that this is a case to manage an application for an integration course. The government entity manages this case which has already some process context. For now I need you te set variables to define this context, I need a top level context for this kind of case and also context at the folder level, each folder should have context focused in process that may make a difference in how the suer chats and asks questions about a document, for example, if there is mistakes or missleading information in a document how would the person without experience know that?, that would be because the right context is in there and the agent can let the user know. So I need you to be very proactive and meet my requirement while helping out with the context information, then help by providing an example that makes a statement of why an agent is needed in there, besides only answering and summarizing... so come up with context and add context to the folder as well. think about it as a process and how a predefined project and predefined folders could have additional information as context. 

I have created a variable in .env "Gemini_API_KEY", use it to test connection to the LLM and use the key to connect the agent to the underlying LLM. 

Please use context7 mcp for the google ADK, and first make a plan on how to implement the agents and allow a socket for conversation. No memory is needed, also saving sessions isn't needed for now.  

Focus in modular development and in minimal testing before implementing more changes, that is very important. 

For now there shouldn't be any database, and teh frontened should point to internal docs or objects for all frontend interactions. 

Use Python and fast api for the services. A python venv is active, you may use cli commands on your own to install dependencies. 
