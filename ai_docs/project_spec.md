# Create Generative UI Chat Components.

## High Level Overview
- Use upgraded sonnet 3.5 to generate a tool call to create a component.
- Use the component type to dynamically create a component.
- Create components for each type.
- Add submission logic to each component.
- Add server/client state management for messages via SQLite database.

## Team
- client coding agent: `sh scripts/aider_client.sh`
- server coding agent: `sh scripts/aider_server.sh`
- docs editor agent: `sh scripts/doc_editor.sh`
- bash agent: `sh scripts/bash.sh`

## Setup
- server: `/add server/`, `/read-only src/components/GenUIChat.vue`
- client: `/add src/`, `/read-only server/`

- Collect documentation for ai assistants `ai_docs/*`
  
  ```bash
  dotenv -- aloe1 collect {tool use docs} > ai_docs/tool-use-raw.md

  aloe1 editor "read ai_docs/tool-use-raw.md. Create ai_docs/tool-use.md with examples and docs specifically around tool use"

  dotenv -- aloe1 collect {dynamic component docs} > ai_docs/dynamic-component-raw.md

  aloe1 editor "read ai_docs/dynamic-component-raw.md. Create ai_docs/dynamic-component.md with examples and docs specifically around dynamic components"
  ```

- server `/read-only ai_docs/tool-use.md`
- client `/read-only ai_docs/`

## Tasks
1. (server) Add /tool endpoint
   ```aider
   update server.ts:
      create /tool endpoint.

         reference tool_use.md doc to create tool_prompt(prompt: str) -> Tool.

         use force_tool = gen_ui.build gen_ui tool with properties: {
            "component_type": {
               "type": "string",
               "enum": ["text", "starRating", "colorPicker", "contactForm"],
               "description": "The type of UI component to generate",
            },
            "textResponse": {
               "type": "string",
               "description": "Optional response text for text-based components",
               }
         }.
   ```

2. (client) Call /tool endpoint
   
   ```aider
   update GenUIChat.vue:
      call /tool endpoint after enter is pressed.
      use entire object as response.
   ```
2.2. (client) Update messages type to store response from /tool endpoint and setup for load/save
   ```aider
      update GenUIChat.vue:
      update Message: add {componentType: str, componentProps: Record, submitResponse: Record, createdAt: int, id: str}
      when we add messages generate these.
   ```

3. (client) Create the UI components & dynamic component
   ```aider
   create src/components/GenUIText.vue:
   <GenUIText :textResponse="textResponse" @handleSubmit="handleDynamicSubmit" />

   create src/components/GenUIStarRating.vue:
   <GenUIStarRating @handleSubmit="handleDynamicSubmit" />

   create src/components/GenUIColorPicker.vue:
   <GenUIColorPicker @handleSubmit="handleDynamicSubmit" />

   create src/components/GenUIContactForm.vue:
   <GenUIContactForm @handleSubmit="handleDynamicSubmit" />

   update GenUIChat.vue:
   use dynamic component instead of raw text of response.
```
4. (server) Create SQLite database in server/app.db
   ```bash
   aloe1 bash "Create sqlite db in server/app.db. New table: messages {id: str, text?: str, isUser: bool, componentType?: str, componentProps?: json, submitResponse?: json, createdAt: int}"
   ```

5. (server) Create /load-chat and /save-chat endpoints
   aider
   Notes:
   SQLite database is saved in server/app.db.
   Table already exists.

   create server/database.ts:
   create loadMessages() -> Message[]
   create saveMessages(messages: Message[])
   insert or update (on id) every message.

   update server.ts:
   create /load-chat endpoint:
   return all messages from messages table.
   create /save-chat endpoint:
   save (upsert) all messages to messages table, skip matching id.

6. (client) Add load chat and save chat logic
   aider
   update GenUIChat.vue:
   update Message: add id: str, createdAt: int.
   When we add messages, generate these.

   Add load chat and save chat logic.
   On mounted, hit /load-chat endpoint and save response to messages.
   On enter press and on submit, hit /save-chat endpoint with all messages.
