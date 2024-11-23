Developer Newsletter

[tool use course](https://github.com/anthropics/courses/tree/master/tool_use)
[form](https://forms.gle/BFnYc6iCkWoRzFgk7)


## ​How tool use works


- Define tools with names, descriptions, and input schemas in your API request.
- Include a user prompt that might require these tools, e.g., “What’s the weather in San Francisco?”

- Claude assesses if any tools can help with the user’s query.
- If yes, Claude constructs a properly formatted tool use request.
- The API response has a stop_reason of tool_use, signaling Claude’s intent.

- On your end, extract the tool name and input from Claude’s request.
- Execute the actual tool code client-side.
- Continue the conversation with a new user message containing a tool_result content block.

- Claude analyzes the tool results to craft its final response to the original user prompt.

computer use (beta)


## ​How to implement tool use


### ​Choosing a model

### ​Specifying tools


```
tools
```

```
name
```

```
^[a-zA-Z0-9_-]{1,64}$
```

```
description
```

```
input_schema
```

[JSON Schema](https://json-schema.org/)

```JSON
{
"name": "get_weather",
"description": "Get the current weather in a given location",
"input_schema": {
"type": "object",
"properties": {
"location": {
"type": "string",
"description": "The city and state, e.g. San Francisco, CA"
},
"unit": {
"type": "string",
"enum": ["celsius", "fahrenheit"],
"description": "The unit of temperature, either 'celsius' or 'fahrenheit'"
}
},
"required": ["location"]
}
}
```

```
get_weather
```

```
location
```

```
unit
```


#### ​Tool use system prompt


```
tools
```

```plaintext
In this environment you have access to a set of tools you can use to answer the user's question.
{{ FORMATTING INSTRUCTIONS }}
String and scalar parameters should be specified as is, while lists and objects should use JSON format. Note that spaces for string values are not stripped. The output is not expected to be valid XML and is parsed with regular expressions.
Here are the functions available in JSONSchema format:
{{ TOOL DEFINITIONS IN JSON SCHEMA }}
{{ USER SYSTEM PROMPT }}
{{ TOOL CONFIGURATION }}
```


#### ​Best practices for tool definitions


- Provide extremely detailed descriptions. This is by far the most important factor in tool performance. Your descriptions should explain every detail about the tool, including:

What the tool does
When it should be used (and when it shouldn’t)
What each parameter means and how it affects the tool’s behavior
Any important caveats or limitations, such as what information the tool does not return if the tool name is unclear. The more context you can give Claude about your tools, the better it will be at deciding when and how to use them. Aim for at least 3-4 sentences per tool description, more if the tool is complex.
- Prioritize descriptions over examples. While you can include examples of how to use a tool in its description or in the accompanying prompt, this is less important than having a clear and comprehensive explanation of the tool’s purpose and parameters. Only add examples after you’ve fully fleshed out the description.

```JSON
{
"name": "get_stock_price",
"description": "Retrieves the current stock price for a given ticker symbol. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. The tool will return the latest trade price in USD. It should be used when the user asks about the current or most recent price of a specific stock. It will not provide any other information about the stock or company.",
"input_schema": {
"type": "object",
"properties": {
"ticker": {
"type": "string",
"description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
}
},
"required": ["ticker"]
}
}
```

```JSON
{
"name": "get_stock_price",
"description": "Gets the stock price for a ticker.",
"input_schema": {
"type": "object",
"properties": {
"ticker": {
"type": "string"
}
},
"required": ["ticker"]
}
}
```

```
ticker
```


### ​Controlling Claude’s output


#### ​Forcing tool use


```
tool_choice
```

```plaintext
tool_choice = {"type": "tool", "name": "get_weather"}
```

- auto allows Claude to decide whether to call any provided tools or not. This is the default value.
- any tells Claude that it must use one of the provided tools, but doesn’t force a particular tool.
- tool allows us to force Claude to always use a particular tool.

```
tool_choice
```

```
any
```

```
tool
```

```
text
```

```
tool_use
```

```
{"type": "auto"}
```

```
tool_choice
```

```
user
```

```
What's the weather like in London? Use the get_weather tool in your response.
```


#### ​JSON output


```
record_summary
```

tool use examples


#### ​Chain of thought


```
tool_choice
```

```
auto
```

Forcing tool use

```JSON
{
"role": "assistant",
"content": [
{
"type": "text",
"text": "<thinking>To answer this question, I will: 1. Use the get_weather tool to get the current weather in San Francisco. 2. Use the get_time tool to get the current time in the America/Los_Angeles timezone, which covers San Francisco, CA.</thinking>"
},
{
"type": "tool_use",
"id": "toolu_01A09q90qw90lq917835lq9",
"name": "get_weather",
"input": {"location": "San Francisco, CA"}
}
]
}
```

```
"Before answering, explain your reasoning step-by-step in tags."
```

```
<thinking>
```

```
<thinking>
```


#### ​Disabling parallel tool use


```
disable_parallel_tool_use=true
```

```
tool_choice
```

- When tool_choice type is auto, this ensures that Claude uses at most one tool
- When tool_choice type is any or tool, this ensures that Claude uses exactly one tool

### ​Handling tool use and tool result content blocks


```
stop_reason
```

```
tool_use
```

```
tool_use
```

- id: A unique identifier for this particular tool use block. This will be used to match up the tool results later.
- name: The name of the tool being used.
- input: An object containing the input being passed to the tool, conforming to the tool’s input_schema.

```JSON
{
"id": "msg_01Aq9w938a90dw8q",
"model": "claude-3-5-sonnet-20241022",
"stop_reason": "tool_use",
"role": "assistant",
"content": [
{
"type": "text",
"text": "<thinking>I need to use the get_weather, and the user wants SF, which is likely San Francisco, CA.</thinking>"
},
{
"type": "tool_use",
"id": "toolu_01A09q90qw90lq917835lq9",
"name": "get_weather",
"input": {"location": "San Francisco, CA", "unit": "celsius"}
}
]
}
```

1. Extract the name, id, and input from the tool_use block.
2. Run the actual tool in your codebase corresponding to that tool name, passing in the tool input.
3. [optional] Continue the conversation by sending a new message with the role of user, and a content block containing the tool_result type and the following information:

tool_use_id: The id of the tool use request this is a result for.
content: The result of the tool, as a string (e.g. "content": "15 degrees") or list of nested content blocks (e.g. "content": [{"type": "text", "text": "15 degrees"}]). These content blocks can use the text or image types.
is_error (optional): Set to true if the tool execution resulted in an error.

```JSON
{
"role": "user",
"content": [
{
"type": "tool_result",
"tool_use_id": "toolu_01A09q90qw90lq917835lq9",
"content": "15 degrees"
}
]
}
```

```JSON
{
"role": "user",
"content": [
{
"type": "tool_result",
"tool_use_id": "toolu_01A09q90qw90lq917835lq9",
"content": [
{"type": "text", "text": "15 degrees"},
{
"type": "image",
"source": {
"type": "base64",
"media_type": "image/jpeg",
"data": "/9j/4AAQSkZJRg...",
}
}
]
}
]
}
```

```JSON
{
"role": "user",
"content": [
{
"type": "tool_result",
"tool_use_id": "toolu_01A09q90qw90lq917835lq9",
}
]
}
```

```
tool
```

```
function
```

```
user
```

```
assistant
```

```
text
```

```
image
```

```
tool_use
```

```
tool_result
```

```
user
```

```
tool_result
```

```
assistant
```

```
tool_use
```


### ​Troubleshooting errors


```
content
```

```
"is_error": true
```

```JSON
{
"role": "user",
"content": [
{
"type": "tool_result",
"tool_use_id": "toolu_01A09q90qw90lq917835lq9",
"content": "ConnectionError: the weather service API is not available (HTTP 500)",
"is_error": true
}
]
}
```

```
max_tokens
```

```
max_tokens
```

```
description
```

```
tool_result
```

```JSON
{
"role": "user",
"content": [
{
"type": "tool_result",
"tool_use_id": "toolu_01A09q90qw90lq917835lq9",
"content": "Error: Missing required 'location' parameter",
"is_error": true
}
]
}
```


## ​Tool use examples


```JSON
{
"id": "msg_01Aq9w938a90dw8q",
"model": "claude-3-5-sonnet-20241022",
"stop_reason": "tool_use",
"role": "assistant",
"content": [
{
"type": "text",
"text": "<thinking>I need to call the get_weather function, and the user wants SF, which is likely San Francisco, CA.</thinking>"
},
{
"type": "tool_use",
"id": "toolu_01A09q90qw90lq917835lq9",
"name": "get_weather",
"input": {"location": "San Francisco, CA", "unit": "celsius"}
}
]
}
```

```
get_weather
```

```
user
```

```JSON
{
"id": "msg_01Aq9w938a90dw8q",
"model": "claude-3-5-sonnet-20241022",
"stop_reason": "stop_sequence",
"role": "assistant",
"content": [
{
"type": "text",
"text": "The current weather in San Francisco is 15 degrees Celsius (59 degrees Fahrenheit). It's a cool day in the city by the bay!"
}
]
}
```

```
get_weather
```

```
get_time
```

```
get_weather
```

```
get_time
```

```
tool_use
```

```
tool_result
```

```
user
```

```
get_weather
```

```JSON
{
"type": "tool_use",
"id": "toolu_01A09q90qw90lq917835lq9",
"name": "get_weather",
"input": {"location": "New York, NY", "unit": "fahrenheit"}
}
```

```
get_location
```

```
get_weather
```

```
get_location
```

```
tool_result
```

```
get_weather
```

1. Claude first realizes it needs the user’s location to answer the weather question, so it calls the get_location tool.
2. The user (i.e. the client code) executes the actual get_location function and returns the result “San Francisco, CA” in a tool_result block.
3. With the location now known, Claude proceeds to call the get_weather tool, passing in “San Francisco, CA” as the location parameter (as well as a guessed unit parameter, as unit is not a required parameter).
4. The user again executes the actual get_weather function with the provided arguments and returns the weather data in another tool_result block.
5. Finally, Claude incorporates the weather data into a natural language response to the original question.

```
Answer the user's request using relevant tools (if they are available). Before calling a tool, do some analysis within \<thinking>\</thinking> tags. First, think about which of the provided tools is the relevant tool to answer the user's request. Second, go through each of the required parameters of the relevant tool and determine if the user has directly provided or given enough information to infer a value. When deciding if the parameter can be inferred, carefully consider all the context to see if it supports a specific value. If all of the required parameters are present or can be reasonably inferred, close the thinking tag and proceed with the tool call. BUT, if one of the values for a required parameter is missing, DO NOT invoke the function (not even with fillers for the missing params) and instead, ask the user to provide the missing parameters. DO NOT ask for more information on optional parameters if it is not provided.
```

- You usually want to provide a single tool
- You should set tool_choice (see Forcing tool use) to instruct the model to explicitly use that tool
- Remember that the model will pass the input to the tool, so the name of the tool and description should be from the model’s perspective.

```
record_summary
```


## ​Pricing


```
tools
```

- The tools parameter in API requests (tool names, descriptions, and schemas)
- tool_use content blocks in API requests and responses
- tool_result content blocks in API requests

```
tools
```

```
auto
```

```
any
```

```
tool
```

```
auto
```

```
any
```

```
tool
```

```
auto
```

```
any
```

```
tool
```

```
auto
```

```
any
```

```
tool
```

```
auto
```

```
any
```

```
tool
```

models overview table

```
usage
```


## ​Next Steps


[Calculator ToolLearn how to integrate a simple calculator tool with Claude for precise numerical computations.](https://github.com/anthropics/anthropic-cookbook/blob/main/tool_use/calculator_tool.ipynb)
[Customer Service AgentBuild a responsive customer service bot that leverages client-side tools to enhance support.](https://github.com/anthropics/anthropic-cookbook/blob/main/tool_use/customer_service_agent.ipynb)
[JSON ExtractorSee how Claude and tool use can extract structured data from unstructured text.](https://github.com/anthropics/anthropic-cookbook/blob/main/tool_use/extracting_structured_json.ipynb)

Vision
Computer use (beta)

- How tool use works
- How to implement tool use
- Choosing a model
- Specifying tools
- Tool use system prompt
- Best practices for tool definitions
- Controlling Claude’s output
- Forcing tool use
- JSON output
- Chain of thought
- Disabling parallel tool use
- Handling tool use and tool result content blocks
- Troubleshooting errors
