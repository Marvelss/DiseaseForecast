"""
@Author : SakuraFox
@Time: 2024-04-07 9:41
@File : test7.py
@Description : 测试处理后字段名称变化
"""
from pages.pages_utils import getHandledField
import unittest


class GetHandledFieldTest(unittest.TestCase):

    def test_original_field(self):
        self.assertEqual(getHandledField('age'), 'age_预处理后')

    def test_processed_field_with_increment(self):
        self.assertEqual(getHandledField('gender_预处理后3'), 'gender_预处理后4')

    def test_original_field_with_special_character(self):
        self.assertEqual(getHandledField('occupation'), 'occupation_预处理后')

    def test_original_field_with_space(self):
        self.assertEqual(getHandledField('job_title'), 'job_title_预处理后')

    def test_processed_field_with_space(self):
        self.assertEqual(getHandledField('job_title_预处理后2'), 'job_title_预处理后3')


if __name__ == '__main__':
    unittest.main()
