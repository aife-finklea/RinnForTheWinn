from random import random, randint
from time import sleep, strftime
from typing import Union, List, Tuple

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    InvalidSessionIdException,
)
from selenium.webdriver.common.by import By

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
            next_button = browser.find_element(by=By.ID, value="identifierNext")
            textbox = browser.find_element(by=By.XPATH, value='//*[@id="identifierId"]')
            textbox.send_keys(username)
            next_button.click()
            sleep(3)

            # Password
            error_ct = 0
            while True:
                try:
                    next_button = browser.find_element(by=By.ID, value="passwordNext")
                    textbox = browser.find_element(
                        by=By.XPATH,
                        value="/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/"
                        "form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input",
                    )
                    textbox.send_keys(password)
                    next_button.click()
                    break
                except NoSuchElementException as e:
                    if error_ct > 5:
                        raise e
                    else:
                        error_ct += 1
                        sleep(0.5)
            print("Logged in!")
            sleep(5)
            reloads_in_a_row = 0
            try:
                while votes_so_far < num_votes:
                    error_ct = 0
                    while True:
                        try:
                            submit = browser.find_element(
                                by=By.XPATH,
                                value="/html/body/div/div[2]/form/div[2]/div/div[3]/div/div[1]/div",
                            )
                            for i in range(len(picks)):
                                if picks[i] == 0:
                                    continue
                                question = i + 1
                                answer = picks[i]
                                browser.find_element(
                                    by=By.XPATH,
                                    value=f'//*[@id="mG61Hd"]/div[2]/div/div[2]/div[{question}]/'
                                    f"div/div/div[2]/div[1]/div/span/div/div[{answer}]/label",
                                ).click()
                            break
                        except NoSuchElementException as e:
                            if error_ct > 5:
                                raise e
                            else:
                                error_ct += 1
                                sleep(0.5)
                    submit.click()
                    browser.find_element(
                        By.XPATH,
                        value="/html/body/div[1]/div[2]/div[1]/div/div[4]/a[2]",
                    ).click()
                    counter += 1
                    votes_so_far += 1
                    reloads_in_a_row = 0
                    if votes_so_far < num_votes:
                        offset = random() * delay_offset_range * 2 - delay_offset_range
                        print(f"Delay for {delay + offset} seconds...")
                        sleep(delay + offset)
            except NoSuchElementException:
                if reloads_in_a_row < 5:
                    reloads_in_a_row += 1
                    print(f"Error. Reloading for the {reloads_in_a_row}th time...")
                    browser.refresh()
                    sleep(3)
                else:
                    raise TooManyReloadsException()
            except ElementClickInterceptedException:
                if reloads_in_a_row < 5:
                    reloads_in_a_row += 1
                    print(f"Error. Reloading for the {reloads_in_a_row}th time...")
                    browser.refresh()
                    sleep(3)
                else:
                    raise TooManyReloadsException()
        except TooManyReloadsException:
            print("Too many errors in a row. Restarting...")
            if "browser" in locals():
                browser.close()
            continue
        except Exception:
            print("Restarting because of big error...")
            try:
                browser.close()
            except InvalidSessionIdException:
                pass
            continue
    if "browser" in locals():
        browser.close()
    with open(counter_file, "w") as f:
        f.write(str(counter))


def day(
    times: List[int],
    num_votes: Tuple[int, int],
    timing_offset_range: Union[float, int] = 0,
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
        if subtract(times[i], timing_offset_range) < now():
            send_votes(randint(num_votes[0], num_votes[1]), 30, 10)
            continue
        offset = random() * timing_offset_range * 2 - timing_offset_range
        print(f"Waiting for it to be {times[i] + offset}")
        while now() < times[i] + offset:
            sleep(30)
        send_votes(randint(num_votes[0], num_votes[1]), 30, 10)


def main():
    offset_range = 3
    curr = int(strftime("%w"))
    while True:
        times_file = schedules[curr]
        print(f"Using file {times_file} for today...")
        with open(times_file, "r") as f:
            times = list(map(int, f.read().splitlines()))
        day(times, (votes_per_batch - offset_range, votes_per_batch + offset_range), 2)
        curr = (curr + 1) % 7


if __name__ == "__main__":
    main()
