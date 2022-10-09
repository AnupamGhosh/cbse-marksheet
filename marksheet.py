from typing import List, Optional, Set

class Subject:
    def __init__(self, name: str, code: str) -> None:
        self.name = name
        self.code = code

    def __lt__(self, other: "Subject") -> bool:
        return self.code < other.code

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
    
class Marks:
    def __init__(self, subject_name: str, code: str, grade: str, score: Optional[int]) -> None:
        self.subject = Subject(subject_name, code)
        self.grade = grade
        self.raw_score = score
        try:
            self.score = int(score)
        except ValueError: # student might have been absent on the exam day
            self.score = 0

    def __lt__(self, other: "Marks") -> bool:
        return self.score > other.score # higher score comes first

    def __str__(self) -> str:
        return f'{self.code} {self.subject} {self.raw_score} {self.grade}'


class Student:
    def __init__(self, name: str, roll: int) -> None:
        self.name = name
        self.roll = roll
        self.marks: List[Marks] = []

    def add_marks(self, marks: Marks) -> None:
        self.marks.append(marks)

    def top_score_avg(self, count: int, mandatory: Set[str]) -> float:
        self.marks.sort()
        total = 0
        found = 0
        other_marks: List[Marks] = []
        # print(mandatory, count)
        for i, mark in enumerate(self.marks):
            if mark.subject.code in mandatory:
                # print(mark.score, mark.subject)
                total += mark.score
                found += 1
            else:
                other_marks.append(mark)

        if (found != len(mandatory)): # student doesn't have the mandatory subjects
            # return -float('inf')
            return None
        for i in range(min(count - found, len(other_marks))):
            # print(other_marks[i].score, other_marks[i].subject)
            total += other_marks[i].score

        # print(total / count)
        # print()

        return total / count

    def best_of_four(self) -> float:
        ''' Eng + any 3 others'''
        return self.top_score_avg(4, {'301'})

    def best_of_four_PCM(self) -> float:
        '''PCM + any 1 other'''
        return self.top_score_avg(4, {'041', '042', '043'})

    def best_of_five(self) -> float:
        '''Eng + any 4 others'''
        return self.top_score_avg(5, {'301'})

    def best_of_five_PCM(self) -> float:
        '''PCM + any 2 other'''
        return self.top_score_avg(5, {'041', '042', '043'})

    def __lt__(self, other: "Student") -> bool:
        return int(self.roll) < int(other.roll) # show students in asc order of roll no.

    def __str__(self) -> str:
        marks_str = ''
        for mark in self.marks:
            marks_str += f'{mark}\n'
        return f'{self.roll} {self.name}\n{marks_str}'
