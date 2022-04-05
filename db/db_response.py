from dataclasses import dataclass, field
from abc import ABC, abstractmethod

class DBResponse(ABC):
    @abstractmethod
    def discord_msg(self) -> str:
        pass

@dataclass
class LinkResponse(DBResponse):
    status: str
    summoner_name: str = None
    verification_id: str = None
    msg: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.status == "created":
            self.msg = f"Your Discord account has been linked to Summoner '{self.summoner_name}'.\n" \
                   f"To verify that this account belong to you please enter the following code:\n" \
                   f"{self.verification_id}\n" \
                   f"You can enter this code in the League of Legends settings under 'Verification'."
        if self.status == "verified":
            self.msg = f"You have already verified Summoner '{self.summoner_name}'\n " \
                       f"Use !unlink to remove all verifications for this Discord User."
        if self.status == "rejected":
            self.msg = f"Summoner '{self.summoner_name}' has already been verified by another user."
        if self.status == "invalid":
            self.msg = f"Summoner '{self.summoner_name}' does not exist on EUW."

    def discord_msg(self):
        return self.msg