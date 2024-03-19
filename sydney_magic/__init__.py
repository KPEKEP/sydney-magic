from .sydney_magic import sydney
import os
def load_ipython_extension(ipython):
    if len(os.environ.get("BING_COOKIES", ""))<1:
        raise Exception('''
Go to the Copilot web page https://copilot.microsoft.com/.
Open the developer tools in your browser (usually by pressing F12 or right-clicking on the chat dialog and selecting Inspect).
Select the Network tab to view all requests sent to Copilot.
Write a message on the chat dialog that appears on the web page.
Find a request named create?bundleVersion=XYZ and click on it.
Scroll down to the requests headers section and copy the entire value after the Cookie: field.
Then, set it as an environment variable in your shell:

export BING_COOKIES=<your-cookies>

or, in your Python code:

os.environ["BING_COOKIES"] = "<your-cookies>"

or, using the helper:

from sydney_magic.sydney_magic import helper_set_cookie
helper_set_cookie("<your-cookies>")
''')
        
    ipython.register_magic_function(sydney, 'line_cell', 'sydney')

def unload_ipython_extension(ipython):
    pass
