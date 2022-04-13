from random import random, randint
from time import sleep, strftime
from typing import Union, List, Tuple

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
    ElementNotInteractableException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
    element_to_be_clickable,
)
from selenium.webdriver.support.ui import WebDriverWait as Wait

from auth import *
from settings import *

option = webdriver.ChromeOptions()
option.add_argument("-incognito")
option.add_argument("--no-sandbox")


class TooManyReloadsException(Exception):
    def __init__(self):
        pass


def now():
    return int(strftime("%H%M"))


def add(a: int, b: int) -> int:
    small = a % 100 + b % 100
    return ((a // 100 + b // 100) % 24 * 100) + (small // 60 * 100) + (small % 60)


def subtract(a: int, b: int) -> int:
    small = a % 100 - b % 100
    return ((a // 100 - b // 100) % 24 * 100) + (small // 60 * 100) + (small % 60)


def send_votes(
    num_votes: int, delay: Union[int, float], delay_offset_range: Union[float, int] = 0
) -> None:
    print("Sending votes")
    votes_so_far = 0
    try:
        with open(counter_file, "r") as f:
            counter = int(f.read())
    except ValueError:
        counter = 0
    except FileNotFoundError:
        open(counter_file, "x").close()
        counter = 0
    while votes_so_far < num_votes:
        try:
            browser = webdriver.Chrome(
                executable_path=chromedriver_path, options=option
            )
            browser.get(forms_link)

            # Sign in
            textbox = Wait(browser, 10).until(
                element_to_be_clickable((By.XPATH, '//*[@id="identifierId"]'))
            )
            textbox.send_keys(username)
            browser.find_element(
                By.ID, "identifierNext"
            ).click()  # Find and click "Next"

            # Password
            textbox = Wait(browser, 10).until(
                element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/"
                        "span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input",
                    )
                )
            )
            browser.find_element(By.ID, "passwordNext").click()  # Find and click "Next"
            print("Logged in!")

            # Doing the actual voting
            reloads_in_a_row = 0
            try:
                while votes_so_far < num_votes:
                    submit = Wait(browser, 10).until(
                        element_to_be_clickable(
                            (
                                By.XPATH,
                                "/html/body/div/div[2]/form/div[2]/div/div[3]/div/div[1]/div",
                            )
                        )
                    )
                    for i in range(len(picks)):  # Click all chosen answer choices
                        if picks[i] == 0:
                            continue
                        question = i + 1  # The XPATH is 1-indexed
                        answer = picks[i]
                        browser.find_element(
                            by=By.XPATH,
                            value=f'//*[@id="mG61Hd"]/div[2]/div/div[2]/div[{question}]/'
                            f"div/div/div[2]/div[1]/div/span/div/div[{answer}]/label",
                        ).click()
                        del answer  # For debugging reasons

                    submit.click()

                    # Click "Submit another response"
                    try:
                        Wait(browser, 10).until(
                            presence_of_element_located(
                                (
                                    By.XPATH,
                                    "/html/body/div[1]/div[2]/div[1]/div/div[4]/a[2]",
                                )
                            )
                        ).click()
                    except TimeoutException:  # This will happen if there is no "See previous responses" button
                        Wait(browser, 10).until(
                            presence_of_element_located(
                                (
                                    By.XPATH,
                                    "/html/body/div[1]/div[2]/div[1]/div/div[4]/a[1]",
                                )
                            )
                        ).click()
                    counter += 1
                    votes_so_far += 1
                    reloads_in_a_row = 0
                    if votes_so_far < num_votes:
                        offset = random() * delay_offset_range * 2 - delay_offset_range
                        print(f"Delay for {delay + offset} seconds...")
                        sleep(delay + offset)
            except NoSuchElementException:
                if "answer" in locals():
                    print(f"Could not find element {answer}")
                elif "submit" in locals():
                    print('Could not find "Submit another response" button')
                else:
                    print("Could not find submit button")
                if reloads_in_a_row < 5:
                    reloads_in_a_row += 1
                    print(f"Error. Reloading for the {reloads_in_a_row}th time...")
                    browser.refresh()
                else:
                    raise TooManyReloadsException()
            except ElementClickInterceptedException or TimeoutException:
                if reloads_in_a_row < 5:
                    reloads_in_a_row += 1
                    print(f"Error. Reloading for the {reloads_in_a_row}th time...")
                    browser.refresh()
                else:
                    raise TooManyReloadsException()
        except TooManyReloadsException:
            print("Too many errors in a row. Restarting...")
            if "browser" in locals():
                browser.close()
            continue
    if "browser" in locals():
        browser.close()
    with open(counter_file, "w") as f:
        f.write(str(counter))


def day(
    times: List[int],
    num_votes: Tuple[int, int],
    delay: Union[float, int],
    delay_offset_range: Union[float, int],
    times_offset_range: Union[float, int] = 0,
) -> None:
    if now() > times[-1]:
        print("Waiting for it to be tomorrow...")
        sleep(60 * (2400 - now() + 1))
    start = 0
    while times[start] < now():
        start += 1
    for i in range(start, len(times)):
        if random() < 0.1:
            continue
        if subtract(times[i], times_offset_range) < now():
            send_votes(randint(num_votes[0], num_votes[1]), delay, delay_offset_range)
            continue
        offset = random() * times_offset_range * 2 - times_offset_range
        print(f"Waiting for it to be {times[i] + offset}")
        while now() < times[i] + offset:
            sleep(30)
        send_votes(randint(num_votes[0], num_votes[1]), delay, delay_offset_range)


def main():
    delay = 10
    delay_offset_range = 3
    votes_offset_range = 3
    time_offset_range = 2
    curr = int(strftime("%w"))
    while True:
        times_file = f"..\\times\\{schedules[curr]}"
        print(f"Using file {times_file} for today...")
        with open(times_file, "r") as f:
            times = list(map(int, f.read().splitlines()))
        day(
            times,
            (
                votes_per_batch - votes_offset_range,
                votes_per_batch + votes_offset_range,
            ),
            delay,
            delay_offset_range,
            time_offset_range,
        )
        curr = (curr + 1) % 7


if __name__ == "__main__":
    # send_votes(10, 10, 3)
    main()
