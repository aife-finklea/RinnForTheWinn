![GitHub](https://img.shields.io/github/license/Angainor64/RinnForTheWinn)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/selenium)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### Hello! This is a Google Forms bot that I made to automate voting for a thing that my high school did.
Because Google Forms bots are no longer allowed for said thing, and I would obviously never break the rules, I can no 
longer use this, but anyone else can for their own purposes.

This tries to act vaguely human-like. To achieve this, instead of sending in as many votes as fast as possible, it sends
votes in batches on a schedule. The number of votes per batch and the times on the schedule are configurable.

## How to use:
Currently, this only works for a Google Form that has one page of only multiple choice questions, and has a required 
Google login. Additionally, you must have Google Chrome installed. To use it, clone the project using `git clone 
https://github.com/Angainor64/RinnForTheWinn.git` and make sure you have a python interpreter (Python 3.10+, available
at [python.org](https://www.python.org/downloads)). Then, do the following:

1. Install the `selenium` package with `python -m pip install selenium`
2. Open Google Chrome, click the three little dots in the top right corner, go to "Help", then "About Google Chrome".
You should see something that says "Chrome is up-to-date". If you don't, restart Google Chrome. Then, make a note of the
version number of Google Chrome (should look something like 99.0.4844.82). Go to 
[this page](https://chromedriver.chromium.org/downloads) and download the correct version of ChromeDriver for your
version of Google Chrome. Make a note of the download location, you'll need it for step 3. 
3. Create a new file called `auth.py` (outside of `src`) and insert:
```python
username = '{your Google email}'
password = '{your password}'
chromedriver_path = '{path_to_ChromeDriver}'
forms_link = 'https://example.com/'  # Link to the Google Form to submit responses to
```
3. Edit `settings.py` to contain the following values:
```python
counter_file = 'path'  # Path to a txt file that will keep track of the number of votes so far
picks = [1, 2, 0, 1]  # Votes for each question in the Google Form. For example, `[1, 2, 0, 1]` will vote for the first
# option for the first question, vote for the second option for the second question, skip the third question, and vote 
# for the first option in the fourth question. Any additional questions in the Google Form will be ignored. 
votes_per_batch = 10  # Number of votes to be sent in per batch
schedules = ['times.txt', 'times.txt', 'times.txt', 'wed_times.txt', 'times.txt', 'times.txt', 'times.txt']
# This is the list of schedules to use for each day, starting with Sunday
```
4. Edit `times.txt`, `wed_times.txt`, and create and edit any other txt files you want to fit the desired timings for 
batches. The format for these files is simply a sorted, newline-separated list of times, with each time being 24-hour 
without a colon. For example, 8:15 PM would be `2015`, and 12:34 AM would be `0034`
5. `python main.py` to run the script