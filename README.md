Hello! This is a Google Forms bot that I made to automate voting for a
thing that my high school did. Obviously, because Google Forms bots are
no longer allowed for this thing, and I would never break the rules, I can
no longer use this, but anyone else can for their own purposes.

Currently, this only works for a Google Form that has one page of only
multiple choice questions, and has a required Google login. Additionally, you must
have Google Chrome installed. To use it, clone the project using
`git clone https://github.com/Angainor64/RinnForTheWinn.git` and make sure you 
have a python interpreter (Python 3.10+, available at
[python.org](https://www.python.org/downloads)). Then, do the following:

1. Install the `selenium` package with `python -m pip install selenium`
2. Open Google Chrome, click the three little dots in the top right corner, go to
"Help", then "About Google Chrome". You should see something that says "Chrome is
up to date". If you don't, restart Google Chrome. Then, make a note of the version
number of Google Chrome (should look something like 99.0.4844.82). Go to 
[this page](https://chromedriver.chromium.org/downloads) and download the correct
version of ChromeDriver for your version of Google Chrome. Make a note of the
download location, you'll need it for step 3. 
3. Create a new file called `auth.py` and insert:
```python
username = '{your Google email}'
password = '{your password}'
chromedriver_path = '{path_to_ChromeDriver}'
```
3. In `sneaky.py` redefine the `counter_file` variable to be the path to a file that
will keep track of the number of votes so far, and redefine the `forms_link` 
variable to be the link to the Google Form
4. In line 14 of `sneaky.py` redefine the `picks` variable to be the votes for each
question in the Google Form. For example, `[1, 2, 0, 1]` will vote for the first
option for the first question, vote for the second option for the second question, 
skip the third question, and vote for the first option in the fourth question. Any
additional question in the Google Form will be ignored. 
5. `python sneaky.py` to run the script