# Sydney Magic for IPython

Sydney Magic is an IPython extension that provides line and cell magics for interacting with [Sydney.py](https://github.com/vsakkas/sydney.py), an unofficial Python client for Copilot (formerly named Bing Chat), also known as Sydney. This extension allows users to easily use Copilot's capabilities directly within IPython notebooks or shells.

## Features

- Ask questions or make requests to Copilot with `%sydney ask "<prompt>"`.
- Compose content with specific formats and tones using `%sydney compose "<prompt>"`.
- Supports streaming responses for real-time interaction.
- Automatically handles conversation limits by resetting the conversation.

## Installation

To install Sydney Magic, follow these steps:

1. Clone this repository or download the source code.
2. Navigate to the directory containing `setup.py`.
3. Install the module using pip:

```bash
pip install .
```

This command installs Sydney Magic and its dependencies.

## Setting Up the Cookie Environment Variable

Sydney Magic requires a cookie from the Copilot web page to authenticate requests to the Copilot API. To set up this cookie:

1. Go to the [Copilot web page](https://copilot.microsoft.com/).
2. Open the developer tools in your browser (usually by pressing `F12` or right-clicking on the chat dialog and selecting `Inspect`).
3. Select the `Network` tab to view all requests sent to Copilot.
4. Write a message on the chat dialog that appears on the web page.
5. Find a request named `create?bundleVersion=XYZ` and click on it.
6. Scroll down to the requests headers section and copy the entire value after the `Cookie:` field.

Then, set it as an environment variable in your shell:

```bash
export BING_COOKIES="<your-cookies>"
```

Alternatively, you can set the cookie within your IPython notebook or script using the `helper_set_cookie("<your-cookies>")` function provided by Sydney Magic.

## Usage

After installation, load the extension in your IPython environment:

```python
%load_ext sydney_magic
```

### Examples

Ask Copilot a question:

```python
%sydney ask "What is the weather like today?"
```

Compose content with specific formatting:

```python
%sydney compose "Write a short story about a robot" --format=blogpost --tone=enthusiastic
```

For more information on commands and options, use:

```python
%sydney help
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/yourusername/sydney_magic/LICENSE) file for details.
