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


@dataclass
class CreateTeamResponse(DBResponse):
    status: str
    team_name: str = None
    disc_name: str = None
    owner: str = None
    msg: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.status == "created":
            self.msg = f"Your League team '{self.team_name}' has been created."
        elif self.status == "not_verified":
            self.msg = f"You have to link your league account before creating a team '!link <SummonerName>'."
        elif self.status == "exists":
            self.msg = f"A team with this name does already exist."

    def discord_msg(self):
        return self.msg


@dataclass
class InviteUserResponse(DBResponse):
    status: str
    team_name: str = None
    user_name: str = None
    invitee_name: str = None
    msg: str = field(init=False, repr=False)

    def discord_msg(self):
        return self.msg

    def __post_init__(self) -> None:
        if self.status == "team_notfound":
            self.msg = f"No team with the given name has been found in the database."
        elif self.status == "invitee_not_verified":
            self.msg = f"The player you are trying to invite is not verified."
        elif self.status == "not_owner":
            self.msg = f"Only the team owner is allowed to invite new players."
        elif self.status == "success":
            self.msg = f"{self.user_name} has been successfully invited to '{self.team_name}'."
        elif self.status == "already_invited":
            self.msg = f"User is already invited."


@dataclass
class TeamJoinResponse(DBResponse):
    status: str
    team_name: str = None
    user_name: str = None
    invitee_name: str = None
    msg: str = field(init=False, repr=False)

    def discord_msg(self):
        return self.msg

    def __post_init__(self) -> None:
        if self.status == "team_notfound":
            self.msg = f"No team named '{self.team_name}' has been found in the database."
        elif self.status == "no_invitation":
            self.msg = f"No open invitation for {self.ctx.author}."
        elif self.status == "not_verfied":
            self.msg = f"You have to be verified before interacting with teams."
        elif self.status == "success":
            self.msg = f"You successfully joined '{self.team_name}'."


@dataclass
class TeamLeaveResponse(DBResponse):
    status: str
    team_id: int = None
    user_id: int = None
    msg: str = field(init=False, repr=False)

    def discord_msg(self):
        return self.msg

    def __post_init__(self) -> None:
        if self.status == "team_notfound":
            self.msg = f"No team with id '{self.team_id}' has been found in the database.\n"
        elif self.status == "no_member":
            self.msg = f"You are not a member of team:'{self.team_id}'."
        elif self.status == "success":
            self.msg = f"You successfully left team'{self.team_id}'."


@dataclass
class TeamDeleteResponse(DBResponse):
    status: str
    team_id: int = None
    user_id: int = None
    msg: str = field(init=False, repr=False)

    def discord_msg(self):
        return self.msg

    def __post_init__(self) -> None:
        if self.status == "team_notfound":
            self.msg = f"No team with id '{self.team_id}' has been found in the database.\n"
        elif self.status == "not_owner":
            self.msg = f"You are not the owner of the team with id '{self.team_id}'."
        elif self.status == "success":
            self.msg = f"You successfully deleted the team with id '{self.team_id}'."


@dataclass
class TeamShowResponse(DBResponse):
    status: str
    team_name: str = None
    teamObj: dict = None
    members: list = None
    msg: str = field(init=False, repr=False)

    def discord_msg(self):
        return self.msg

    def __post_init__(self) -> None:
        if self.status == "team_notfound":
            self.msg = f"No team named '{self.team_name}' has been found in the database.\n"
        else:
            self.msg = f"Teamname: {self.team_name}\n "
            for x in self.members:
                self.msg += f"Player: {x['summoner_name']}\n"


@dataclass
class TeamListResponse(DBResponse):
    status: str
    teams: list = None

    def discord_msg(self):
        return self.msg

    def __post_init__(self) -> None:
        self.msg = ""
        if self.status == "no_team":
            self.msg = f"Currently is no team included in the database."
        else:
            for team in self.teams:
                self.msg += f"Teamname: {team['name']}.\n"
