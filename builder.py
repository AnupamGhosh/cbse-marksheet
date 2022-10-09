import asyncio
from typing import Dict, List

from csv_writer import CSVWriter
from make_request import HTTPRequest
from marksheet import Student, Subject
from result_parser import ResultParser

class MarksheetBuilder:
    def __init__(self) -> None:
        self.result_parser = ResultParser()
        self.http_request = HTTPRequest()
        self.post_url = "https://resultsarchives.nic.in/cbseresults/cbseresults2011/class1211/cbse1211.asp"
        self.post_headers = {
            HTTPRequest.CONTENT_TYPE: 'application/x-www-form-urlencoded', 
            HTTPRequest.REFERER: 'https://resultsarchives.nic.in/cbseresults/cbseresults2011/class1211/cbse1211.htm'
        }

        self.students: List[Student] = []

    async def _get_student(self, roll: str) -> Student:
        params =  { 'regno': roll, 'B1': 'Submit' }
        async with self.http_request.post(self.post_url, params, self.post_headers) as response:
            content = await response.raw_response()

        marks = self.result_parser.parse_marks(content)
        student = self.result_parser.parse_student(content)
        for mark in marks:
            student.add_marks(mark)

        return student

    async def download_student_marks(self, start_roll: int, end_roll: int) -> None:
        tasks = []
        for roll in range(start_roll, end_roll + 1):
            asyncio_task = asyncio.create_task(self._get_student(roll))
            tasks.append(asyncio_task)

        students = await asyncio.gather(*tasks)
        self.students.extend(students)

    def all_subjects(self) -> List[Subject]:
        '''Exhaustive list of subjects from the downloaded marks'''
        subject_codes = set()
        subjects = []
        for student in self.students:
            for mark in student.marks:
                if mark.subject.code not in subject_codes:
                    subject_codes.add(mark.subject.code)
                    subjects.append(mark.subject)

        return sorted(subjects)

    def create_csv(self, filepath: str) -> None:
        subjects = self.all_subjects()
        other_columns = []
        header = { 
            'name': 'Name', 
            'roll': 'Roll No.', 
            'eng4': 'Best 4',
            'pcm4': 'Best 4 PCM',
            'eng5': 'Best 5',
            'pcm5': 'Best 5 PCM'
        }
        for subject in subjects:
            grade_col = f'{subject.code}_grade'
            other_columns.append(subject.code)
            other_columns.append(grade_col)
            header[subject.code] = subject.name
            header[grade_col] = 'Grade'

        columns = ['roll', 'name'] + other_columns + ['eng4', 'pcm4', 'eng5', 'pcm5']
        csv_writer = CSVWriter(filepath, columns)
        csv_writer.write_header(header)
        csv_writer.write_body(self._csv_body())

    def _csv_body(self) -> List[Dict[str, str]]:
        rows = []
        for student in self.students:
            csv_row = { 
                'name': student.name,
                'roll': student.roll,
                'eng4': student.best_of_four() or 0,
                'pcm4': student.best_of_four_PCM() or 0,
                'eng5': student.best_of_five() or 0,
                'pcm5': student.best_of_five_PCM() or 0
            }
            for mark in student.marks:
                grade_col = f'{mark.subject.code}_grade'
                csv_row[mark.subject.code] = mark.raw_score
                csv_row[grade_col] = mark.grade

            rows.append(csv_row)

        return rows
