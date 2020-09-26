from enum import Enum


class Member(Enum):

    NON_MEMBER = "非会員"
    MEMBER = "正会員"
    MEMBER_TEACHER = "正会員（初等中等教育機関の教職員）"
    MEMBER_STUDENT_ = "学生会員"
    MEMBER_SUPPORT = "協賛会員"
