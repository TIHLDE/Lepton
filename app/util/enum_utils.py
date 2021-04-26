from app.common.enums import UserClass, UserStudy


class EnumUtils:
    @staticmethod
    def get_user_enums(**kwargs):
        user_class = (
            UserClass.ALUMNI
            if int(kwargs["user_class"]) == -1
            else UserClass(int(kwargs["user_class"]))
        )
        user_study = UserStudy(int(kwargs["user_study"]))
        return user_class, user_study
