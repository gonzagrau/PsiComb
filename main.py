from datetime import time
from typing import Tuple, List

weekdays_set = {'LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO'}

def str_to_time_tuple(time_str: str) -> Tuple[int, int]:
    """
    :param time_str: string starting in 'hh' and ending in 'mm', where h and m are ints
    :return: int tuple (hh, mm)
    """
    time_str = time_str.strip()
    assert len(time_str) > 3, f'time_str too short, len == {len(time_str)}'
    try:
        hh = int(time_str[:2])
        mm = int(time_str[-2:])
    except ValueError:
        raise ValueError("Invalid hour or minute")
    assert hh//24 == 0 and hh >= 0, f'Hour must be in range(24), got hour == {hh}'
    assert mm//60 == 0 and mm >= 0, f'minute must be in range(60), got minute == {mm}'
    
    return hh, mm


class CourseBlock(object):
    """
    A course block represents a grouping of a weekday and a time interval,
    delimited by the start time and the end time
    """
    def __init__(self, weekday: str, start_time: time, end_time: time):
        for x in start_time, end_time:
            assert isinstance(x, time), 'Invalid start or end time'
        assert start_time < end_time, 'Start time should be smaller than endtime'
        weekday = weekday.upper()
        assert weekday in weekdays_set, 'Invalid weekday'
        self.weekday = weekday
        self.start_time = start_time
        self.end_time = end_time


    def __eq__(self, other):
        return self.weekday == other.weekday and self.start_time == other.start_time and self.end_time == other.end_time

    def __str__(self):
        return f"{self.weekday}\n{self.start_time.isoformat(timespec='minutes')} - {self.end_time.isoformat(timespec='minutes')}"

    def collides_with(self, other):
        if self.weekday != other.weekday:
            return False
        return other.start_time <= self.start_time < other.end_time \
               or self.start_time <= other.start_time < self.end_time


class Comission(object):
    """
    A comission is a grouping of course blocks, with a unique identifier
    """
    def __init__(self, identifyer: str, *blocks: CourseBlock):
        assert type(identifyer) == str, 'Invalid comission id'
        self.identifyer = identifyer
        self.block_list = []
        for block in blocks:
            assert isinstance(block, CourseBlock), 'Invalid course block'
            self.block_list.append(block)

    def add_course_block(self, c_block: CourseBlock):
        self.block_list.append(c_block)

    def __str__(self):
        string_rep = self.identifyer + '\n'
        for block in self.block_list:
            string_rep += str(block) + '\n'
        return f"{self.identifyer}\n" + ''.join([f"{str(block)}\n" for block in self.block_list])

    def collides_with(self, other):
        for sblock in self.block_list:
            for oblock in other.block_list:
                if sblock.collides_with(oblock):
                    return True
        return False

class Subject(object):
    """
    A subject has a name and a list of comissions
    """
    def __init__(self, name: str, *comissions: Comission):
        self.name = name
        self.comission_list = []
        for comission in comissions:
            assert isinstance(comission, Comission), 'Invalid comission'
            self.comission_list.append(comission)

    def __str__(self):
        return f"{len(self.name)*'_'}\n{self.name}\n{len(self.name)*'_'}\n" + \
               ''.join([f"{str(comission)}\n" for comission in self.comission_list])


class Combination(List[Comission]):
    """
    A combination is simply a list of comissionissions
    """
    def is_valid(self):
        for i in range(len(self)):
            for j in range(i+1, len(self)):
                if self[i].collides_with(self[j]):
                    return False
        return True

    def copy(self):
    # overrides copy to return a Combination object
        new = Combination()
        for el in self:
            new.append(el)
        return new
    def __str__(self):
        return '[' + ', '.join([str(comission.identifyer) for comission in self]) + ']'


def find_combinations(subjects: List[Subject], current_combination=None, index: int = 0) -> List[Combination]:
    """
    :param subjects: list of Subject objects
    :param current_combination: Combination object (defaults to newly created Combination object)
    :param index: index to the current subject at the subjects list
    :return: comb_list, a list of all possible combinations
    """
    if current_combination is None:
        current_combination = Combination()
    comb_list = []
    current_subject = subjects[index]

    for comission in current_subject.comission_list:
        # append to a copy of the ongoing combination in case the current comission collides with it
        new_combination = current_combination.copy()
        new_combination.append(comission)
        if not new_combination.is_valid():
            continue
        if index == len(subjects) - 1: # if the recursion reached the last subject, save the combination
            comb_list.append(new_combination)
        else: # move on to the next subject
            new_comb_list = find_combinations(subjects, new_combination, index+1)
            comb_list = comb_list + new_comb_list

    return comb_list


def test_combiner():
    # Algebra Lineal
    linalg_A = Comission('A')
    linalg_A.add_course_block(CourseBlock('lunes', time(14), time(16)))
    linalg_A.add_course_block(CourseBlock('jueves', time(14), time(16)))
    linalg_A.add_course_block(CourseBlock('viernes', time(9), time(11)))

    linalg_B = Comission('B')
    linalg_B.add_course_block(CourseBlock('lunes', time(12), time(14)))
    linalg_B.add_course_block(CourseBlock('miercoles', time(10), time(12)))
    linalg_B.add_course_block(CourseBlock('jueves', time(12), time(14)))

    linalg_C = Comission('C')
    linalg_C.add_course_block(CourseBlock('lunes', time(8), time(10)))
    linalg_C.add_course_block(CourseBlock('jueves', time(11), time(13)))
    linalg_C.add_course_block(CourseBlock('viernes', time(10), time(12)))

    linalg_D = Comission('D')
    linalg_D.add_course_block(CourseBlock('lunes', time(10), time(12)))
    linalg_D.add_course_block(CourseBlock('miercoles', time(10), time(12)))
    linalg_D.add_course_block(CourseBlock('jueves', time(10), time(12)))

    linalg = Subject('Algebra Lineal', linalg_A, linalg_B, linalg_C, linalg_D)

    # Matematica II

    mateii_A = Comission('A')
    mateii_A.add_course_block(CourseBlock('martes', time(15), time(17)))
    mateii_A.add_course_block(CourseBlock('miercoles', time(15), time(17)))
    mateii_A.add_course_block(CourseBlock('viernes', time(10), time(12)))

    mateii_B = Comission('B')
    mateii_B.add_course_block(CourseBlock('lunes', time(12), time(14)))
    mateii_B.add_course_block(CourseBlock('martes', time(13), time(15)))
    mateii_B.add_course_block(CourseBlock('viernes', time(12), time(14)))

    mateii_C = Comission('C')
    mateii_C.add_course_block(CourseBlock('martes', time(14), time(16)))
    mateii_C.add_course_block(CourseBlock('miercoles', time(12), time(14)))
    mateii_C.add_course_block(CourseBlock('viernes', time(14), time(16)))

    mateii_D = Comission('D')
    mateii_D.add_course_block(CourseBlock('lunes', time(9), time(11)))
    mateii_D.add_course_block(CourseBlock('martes', time(12), time(14)))
    mateii_D.add_course_block(CourseBlock('viernes', time(10), time(12)))

    mateii = Subject('Matematica II', mateii_A, mateii_B, mateii_C, mateii_D)

    # Analisis y Tratamiento de Imagenes
    imag_S = Comission('S')
    imag_S.add_course_block(CourseBlock('jueves', time(8), time(10)))

    imag = Subject('Analisis y Tratamiento de Imagenes', imag_S)


    # combine
    subjects = [linalg, mateii, imag]
    combinations = find_combinations(subjects)

    for combination in combinations:
        for subject, comission in zip(subjects, combination):
            print(f"{subject.name} - {comission.identifyer}", end='\t')
        print()


    print(len(combinations))


if __name__ == '__main__':
    test_combiner()
