import re

from typing import List
from marksheet import Marks, Student

class ResultParser:
    def __init__(self) -> None:
        self.marks_regex = re.compile(r"td align=\"middle\".*(\d\d\d).*\n.*<font.*>.*?([A-Z& ]+).*\n.*<font.*>.*?(\d\d\d|-).*\n.*<font.*>.*?(\w\d)")
        self.name_regex = re.compile(r"Name:.*\n.*<b>.*?([A-Z ]+)")
        self.roll_regex = re.compile(r"Roll No:.*\n.*<font.*>.*?(\d{7})")

    def parse_marks(self, html: str) -> List[Marks]:
        matches = self.marks_regex.finditer(html, re.MULTILINE)
        result = []

        for match in matches:
            code = match.group(1)
            subject = match.group(2)
            score = match.group(3)
            grade = match.group(4)
            result.append(Marks(subject, code, grade, score))

        return result

    def parse_student(self, html: str) -> Student:
        name = self.name_regex.search(html, re.MULTILINE).group(1)
        roll = self.roll_regex.search(html, re.MULTILINE).group(1)
        return Student(name, roll)


async def main():
    req = HTTPRequest()
    # get_url = "https://resultsarchives.nic.in/cbseresults/cbseresults2011/class1211/cbse1211.htm"
    # async with req.get(get_url) as response:
    #     print(await response.raw_response())

    post_url = "https://resultsarchives.nic.in/cbseresults/cbseresults2011/class1211/cbse1211.asp"
    params = { 'regno': 6619017, 'B1': 'Submit' }
    headers = { 
        HTTPRequest.CONTENT_TYPE: 'application/x-www-form-urlencoded', 
        HTTPRequest.REFERER: 'https://resultsarchives.nic.in/cbseresults/cbseresults2011/class1211/cbse1211.htm'
    }
    result_parser = ResultParser()
    async with req.post(post_url, params, headers) as response:
        content = await response.raw_response()

    marks: List[Marks] = result_parser.parse_marks(content)
    student: Student = result_parser.parse_student(content)
    for mark in marks:
        student.add_marks(mark)
    print(student)

import asyncio
from make_request import HTTPRequest
if __name__ == "__main__":
    asyncio.run(main())