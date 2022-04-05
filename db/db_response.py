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

@dataclass
class RankedInfoResponse(DBResponse):
    status: str
    data: dict = field(default_factory=dict)
    msg: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.status == "error":
            self.msg = "Error connecting to the RIOT API. Try again later or contact an administrator"
            return
        if self.status == "not_verified":
            self.msg = "Only available to verified Users. Link your account using !link"
            return

        soloq = self.data['soloq']
        flex = self.data['flex']

        send_msg = ""

        if not soloq:
            send_msg += "**SoloQ**\nNo SoloQ Information Found\n"
        else:
            send_msg += f"**SoloQ**\nCurrent Tier: {soloq['tier']} {soloq['div']} - {soloq['lp']} LP\n"
            if soloq['in_promo']:
                send_msg += "You are currently in **Promotion**\n"
            send_msg += f"Record: {soloq['wins']}-{soloq['losses']} " \
                        f"(**{100 * soloq['wins'] / (soloq['wins'] + soloq['losses']):.2f}%**)\n"

        send_msg += 40 * "-"
        send_msg += "\n"

        if not flex:
            send_msg += "No FlexQ Information Found"
        else:
            send_msg += f"**Flex**\nCurrent Tier: {flex['tier']} {flex['div']} - {flex['lp']} LP\n"
            if flex['in_promo']:
                send_msg += "You are currently in **Promotion**\n"
            send_msg += f"Record: {flex['wins']}-{flex['losses']} " \
                        f"(**{100 * flex['wins'] / (flex['wins'] + flex['losses']):.2f}%**)\n"

        self.msg = send_msg

    def discord_msg(self):
        return self.msg