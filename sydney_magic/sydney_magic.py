import asyncio
import ipynbname
import nest_asyncio
import nbformat
import os
import shlex
import sys
import traceback
from IPython.core.magic import register_line_cell_magic
from sydney import SydneyClient
from sydney.exceptions import (
    NoConnectionException,
    ConnectionTimeoutException,
    NoResponseException,
    ThrottledRequestException,
    CaptchaChallengeException,
    ConversationLimitException,
    CreateConversationException,
    GetConversationsException,
)

# Apply nest_asyncio to enable asyncio's event loop in IPython notebooks
nest_asyncio.apply()


class SydneyMagic:
    """Class providing IPython magic commands to interact with Sydney API."""

    def __init__(self):
        self.client = None
        self.loop = asyncio.get_event_loop()
        self.commands = {
            'ask': self._ask_command,
            'compose': self._compose_command,
            'explain': self._explain_command,
            'error': self._error_command,
            'readme': self._readme_command,
            'unknown': lambda x, y: print("Command not recognized. Use 'help' for more information.")
        }

    async def _ask_command(self, command, **kwargs):
        """Ask a question or make a request to Sydney API, streaming the response."""
        async for response in self.client.ask_stream(command, **kwargs):
            print(response, end="", flush=True)

    async def _compose_command(self, command, **kwargs):
        """Request Sydney API to compose content, streaming the response."""
        async for response in self.client.compose_stream(command, **kwargs):
            print(response, end="", flush=True)

    async def _explain_command(self, command, **kwargs):
        """Request Sydney API to explain the current notebook's code."""
        code = get_notebook_code()
        query = f'Explain the code and how it works. Code:\n{code}'
        async for response in self.client.ask_stream(query, **kwargs):
            print(response, end="", flush=True)

    async def _error_command(self, command, **kwargs):
        """Request Sydney API to explain the last occurred error."""
        error = get_last_error()
        code = get_notebook_code()
        if not error:
            print("There is no error to explain.")
            return

        query = f'Explain the error and how to fix it. Code:\n{code}\nError:\n{error}'

        async for response in self.client.ask_stream(query, **kwargs):
            print(response, end="", flush=True)

    async def _readme_command(self, command, **kwargs):
        """Generates a README.md file for the notebook's code using Sydney API."""
        code = get_notebook_code()
        query = f'''Create a README.md markdown for the following code. 
                    IMPORTANT: put the contents of the markdown in between <sydney_response> and </sydney_response> tags. 
                    Code:\n{code}'''

        result = ''
        async for response in self.client.ask_stream(query, **kwargs):
            result += response
            print(response, end="", flush=True)

        if os.path.exists("README.md"):
            if input("File already exists. Overwrite? (y/n)").lower() != "y":
                return

        contents = result.split("<sydney_response>")[1].split("</sydney_response>")[0] if "<sydney_response>" in result else result

        with open("README.md", "wt") as f:
            f.write(contents)

        print("Done: README.md has been created!")

    async def _run_sydney_command(self, command, **kwargs):
        """Runs a command using Sydney API, handling connection and API exceptions."""
        try:
            if not self.client:
                self.client = SydneyClient()
                await self.client.start_conversation()

            verb = command.split(" ", 2)[0]
            adjusted_command = command[len(verb):].strip()
            handler = self.commands.get(verb, self.commands['unknown'])
            await handler(adjusted_command, **kwargs)
        except ConversationLimitException:
            print("Warning: Reached conversation limit. Resetting conversation and continuing.")
            await self.client.reset_conversation()
            await self._run_sydney_command(command, **kwargs)
        except Exception as e:
            self._handle_exception(e)

    def _handle_exception(self, e):
        """Handles exceptions by printing an appropriate error message."""
        if isinstance(e, (NoConnectionException, ConnectionTimeoutException, NoResponseException, ThrottledRequestException,
                          CaptchaChallengeException, CreateConversationException, GetConversationsException)):
            print(f"Error: {e}.")
        else:
            print(f"An unexpected error occurred: {str(e)}")

    def print_help(self):
        """Prints the help text for using Sydney magic commands."""
        help_text = """
        Use `%sydney [command]` for line magic or `%%sydney [command]` for cell magic.
        Commands:
          - ask [prompt]: Ask a question or make a request to Copilot.
              Options:
                --attachment=[image url or path]
                --context=[web-page-source]
                --citations=[True|False] 
                --suggestions: Include suggested responses.
                --raw=[True|False]: Get raw JSON response.
          - compose [prompt]: Compose content with a specific format and tone.
            Options:
              --tone=[professional|casual|enthusiastic|informational|funny]: Set the tone for composition.
              --format=[paragraph|email|blogpost|ideas]: Set the format for composition.
              --length=[short|medium|long]: Set the length for composition.
              --suggestions: Include suggested responses.
              --raw=[True|False]: Get raw JSON response.
          - explain: Explain the current notebook code.
          - error: Explain the last occurred error.
          - readme: Generates README.md in the current directory.
        Example:
          `%sydney ask "What is Python?" --citations`
        """
        print(help_text.strip())

    async def close_client(self):
        """Closes the Sydney client session."""
        if self.client:
            await self.client.close_conversation()
            self.client = None


sydney_magic_instance = SydneyMagic()


def sydney(line, cell=None):
    """Main function to execute Sydney magic commands."""
    if line.strip() == "help" or (cell and cell.strip() == "help"):
        sydney_magic_instance.print_help()
        return

    kwargs = {}
    try:
        if cell:
            args = shlex.split(line)
            command, kwargs = parse_arguments(args)
            command_call = f'{command} "{cell}"'
            sydney_magic_instance.loop.run_until_complete(sydney_magic_instance._run_sydney_command(command_call, **kwargs))
        else:
            args = shlex.split(line)
            command, kwargs = parse_arguments(args)
            sydney_magic_instance.loop.run_until_complete(sydney_magic_instance._run_sydney_command(command, **kwargs))
    finally:
        sydney_magic_instance.loop.run_until_complete(sydney_magic_instance.close_client())


def parse_arguments(args):
    """Parses arguments from the line or cell magic command."""
    kwargs = {}
    command = args[0] if args else ""
    for arg in args[1:]:
        if arg.startswith("--"):
            key, value = arg[2:].split('=', 1)
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            kwargs[key] = value
        else:
            command += f" {arg}"
    return command, kwargs


def helper_set_cookie(cookie):
    """Sets the environment variable for the cookie needed by Sydney-py."""
    os.environ["BING_COOKIES"] = cookie


def get_last_error():
    """Retrieves the last error that occurred in the IPython environment."""
    if hasattr(sys, 'last_type') and hasattr(sys, 'last_value') and hasattr(sys, 'last_traceback'):
        exc_type, exc_value, exc_traceback = sys.last_type, sys.last_value, sys.last_traceback
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        return error_message
    else:
        return None


def get_notebook_name():
    """Returns the file path of the current notebook."""
    return ipynbname.path()


def get_notebook_code():
    """Extracts and returns the code from all code cells in the current notebook."""
    with open(get_notebook_name(), 'r', encoding='utf-8') as nb_file:
        nb_contents = nbformat.read(nb_file, as_version=4)
    all_code = ""
    for cell in nb_contents['cells']:
        if cell['cell_type'] == 'code':
            all_code += cell['source'] + "\n\n"
    return all_code.strip()

