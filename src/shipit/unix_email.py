from typing import List, Dict
from pydantic import BaseModel, EmailStr

class UnixEmailSystem(BaseModel):
    users: Dict[EmailStr, List[str]] = {}
    mailing_lists: Dict[str, List[EmailStr]] = {}

    def register_user(self, email: EmailStr):
        if email not in self.users:
            self.users[email] = []

    def create_mailing_list(self, list_name: str, members: List[EmailStr]):
        if list_name not in self.mailing_lists:
            self.mailing_lists[list_name] = members

    def send_email(self, from_email: EmailStr, to_emails: List[EmailStr], subject: str, body: str):
        if from_email not in self.users:
            print(f"Sender '{from_email}' is not registered.")
            return

        recipients = set(to_emails)
        for mailing_list, members in self.mailing_lists.items():
            if mailing_list in recipients:
                recipients.remove(mailing_list)
                recipients.update(members)

        for to_email in recipients:
            if to_email not in self.users:
                print(f"Recipient '{to_email}' is not registered.")
            else:
                email = f"From: {from_email}\nTo: {to_email}\nSubject: {subject}\nBody: {body}"
                self.users[to_email].append(email)

    def get_emails(self, email: EmailStr) -> List[str]:
        if email not in self.users:
            print(f"User '{email}' is not registered.")
            return []

        mailbox = self.users[email]
        return mailbox

    def get_mailing_list_members(self, list_name: str) -> List[EmailStr]:
        if list_name not in self.mailing_lists:
            print(f"Mailing list '{list_name}' does not exist.")
            return []

        members = self.mailing_lists[list_name]
        return members
