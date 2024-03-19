from IPython.core.magic import register_line_cell_magic
import asyncio
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
import os
import nest_asyncio
import shlex

nest_asyncio.apply()

class SydneyMagic:
    def __init__(self):
        self.client = None
        self.loop = asyncio.get_event_loop()

    async def _run_sydney_command(self, command, **kwargs):
        try:
            if not self.client:
                self.client = SydneyClient()
                await self.client.start_conversation()

            if command.startswith("ask"):
                async for response in self.client.ask_stream(command[4:], **kwargs):
                    print(response, end="", flush=True)
            elif command.startswith("compose"):
                async for response in self.client.compose_stream(command[8:], **kwargs):
                    print(response, end="", flush=True)
            else:
                print("Command not recognized. Use 'help' for more information.")
        except ConversationLimitException:
            print("Warning: Reached conversation limit. Resetting conversation and continuing.")
            await self.client.reset_conversation()
            await self._run_sydney_command(command, **kwargs)
        except Exception as e:
            self._handle_exception(e)

    def _handle_exception(self, e):
        if isinstance(e, NoConnectionException):
            print("Error: No connection to Copilot. Please check your internet connection and try again.")
        elif isinstance(e, ConnectionTimeoutException):
            print("Error: Connection to Copilot timed out. Please try again later.")
        elif isinstance(e, NoResponseException):
            print("Error: No response was returned from Copilot. Check your query or try again later.")
        elif isinstance(e, ThrottledRequestException):
            print("Error: Request is throttled. Too many requests have been made in a short period. Wait and try again later.")
        elif isinstance(e, CaptchaChallengeException):
            print("Error: Captcha challenge must be solved. Please solve the CAPTCHA and use a new cookie.")
        elif isinstance(e, CreateConversationException):
            print("Error: Failed to create conversation. Retry or check if Copilot service is available.")
        elif isinstance(e, GetConversationsException):
            print("Error: Failed to retrieve conversations. Please try again.")
        else:
            print(f"An unexpected error occurred: {str(e)}")

    def print_help(self):
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
        Example:
          `%sydney ask "What is Python?" --citations`
        """
        print(help_text)

    async def close_client(self):
        if self.client:
            await self.client.close_conversation()
            self.client = None

sydney_magic_instance = SydneyMagic()

def sydney(line, cell=None):
    if line.strip() == "help" or cell and cell.strip() == "help":
        sydney_magic_instance.print_help()
        return
    try:
        if cell:
            commands = cell.split('\n')
            for command in commands:
                sydney_magic_instance.loop.run_until_complete(sydney_magic_instance._run_sydney_command(command))
        else:
            sydney_magic_instance.loop.run_until_complete(sydney_magic_instance._run_sydney_command(line))
    finally:
        sydney_magic_instance.loop.run_until_complete(sydney_magic_instance.close_client())


def sydney(line, cell=None):
    if line.strip() == "help" or (cell and cell.strip() == "help"):
        sydney_magic_instance.print_help()
        return

    # Initialize an empty dictionary for kwargs
    kwargs = {}
    try:
        if cell:
            # Process each line in the cell
            commands = cell.split('\n')
            for command in commands:
                # Split command into arguments
                args = shlex.split(command)
                command, kwargs = parse_arguments(args)
                sydney_magic_instance.loop.run_until_complete(sydney_magic_instance._run_sydney_command(command, **kwargs))
        else:
            # Split line into arguments
            args = shlex.split(line)
            command, kwargs = parse_arguments(args)
            sydney_magic_instance.loop.run_until_complete(sydney_magic_instance._run_sydney_command(command, **kwargs))
    finally:
        sydney_magic_instance.loop.run_until_complete(sydney_magic_instance.close_client())

def parse_arguments(args):
    """Parse arguments from the magic command and return the command with kwargs."""
    kwargs = {}
    command = args[0] if args else ""
    for arg in args[1:]:
        if arg.startswith("--"):
            assert ("=" in arg), "Argmuent format must be arg=value"
            key, value = arg[2:].split('=')
            if value.lower() == 'true': value = True
            elif value.lower() == 'false': value = False
            kwargs[key] = value
        else:
            command += " " + arg  # Append to command if it's not a kwarg
    return command, kwargs

def helper_set_cookie(cookie):
    '''
    Set env var for the cookie needed for sydney-py
    '''
    os.environ["BING_COOKIES"] = cookie