
import pandas as pd
import combiner
from datetime import time
from typing import List


pd.set_option('display.max_columns', None)

class Schedule(pd.DataFrame):
    # generate this time series only once, since it's shared by all instances
    time_series = pd.date_range(start='07:00', end='22:00', freq='30T').time

    def __init__(self):
        super().__init__('', index=Schedule.time_series, columns= list(combiner.weekdays_list))

    def add_course_block(self, course_block: combiner.CourseBlock, subject_name: str) -> None:
        self.loc[course_block.start_time : course_block.end_time, course_block.weekday].iloc[:-1] = subject_name

    def add_combination(self, subjects: List[combiner.Subject], combination: combiner.Combination) -> None:
        for subject, comission in zip(subjects, combination):
            sub_name = subject.name
            for block in comission.block_list:
                self.add_course_block(block, sub_name)


def save_to_excel(subjects: List[combiner.Subject], combinations: List[combiner.Combination]):
    """
    This function saves a list of combinations to a single excel file
    """
    with pd.ExcelWriter('output_excels/combinations.xlsx') as writer:
        for index, combination in enumerate(combinations):
            # add the current combination to a new schedule
            df = Schedule()
            df.add_combination(subjects, combination)

            # drop seconds in the index time
            df.index = df.index.map(lambda t: t.strftime('%H:%M'))

            # add to a new sheet
            df.to_excel(writer, sheet_name=f"Combination {index + 1}")


def test_scheduler():
    """
    to test the schedule maker, the combinations generated by the combiner test
    will be used as an example
    """

    subjects, combinations = combiner.test_combiner()
    save_to_excel(subjects, combinations)


if __name__ == '__main__':
    test_scheduler()



