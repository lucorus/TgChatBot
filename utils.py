# ошибки среди введёных юзером данных
class UserInputException(BaseException):
    def __init__(self, message="Invalid user input"):
      self.message = message
      super().__init__(self.message)
