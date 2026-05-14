class InvalidResetTokenException(Exception):
    def __init__(self):
        self.message = "Invalid or expired password reset token."
        super().__init__(self.message)


class ExpiredResetTokenException(Exception):
    def __init__(self):
        self.message = "Password reset token has expired."
        super().__init__(self.message)
