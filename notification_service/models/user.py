from notification_service.exceptions import InvalidInputException


class User:

    def __init__(self, user_id: str, email_address: str | None = None,
                 phone_number: int | None= None):

        if not(isinstance(user_id, str)) or not user_id.strip():
            raise InvalidInputException("User Id is not Proper")

        self._user_id = user_id
        self._email_address = email_address.strip() if email_address else None
        self._phone_number = phone_number


    def get_id(self) -> str:
        """
        Returns the user_id
        :return:
        """
        return self._user_id

    def get_email(self) -> str | None:
        """
        Returns the email
        :return:
        """
        return self._email_address

    def get_phone(self) -> int| None:
        """
        Returns the Phone
        :return:
        """
        return self._phone_number

    def has_phone(self) -> bool:
        """
        Checks if a phone number info is present
        :return:
        """
        return True if self._phone_number else False


    def has_email(self) -> bool:
        """

        :return:
        """
        return  True if self._email_address else False

    def __repr__(self):
        return (f"User(ID='{self._user_id}', Email='{self._email_address or 'N/A'}', "
                f"Phone='{self._phone_number or 'N/A'}')")



