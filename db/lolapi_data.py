import os

import cassiopeia as cass
import logging
from dotenv import load_dotenv

load_dotenv()
cass.set_riot_api_key(os.getenv("RIOT_API"))


def get_queue_info(queue):
    try:
        div = queue.division.value
        tier = queue.tier.value
        in_promo = queue.promos is not None
        lp = queue.league_points
        losses = queue.losses
        wins = queue.wins

        return tier, div, lp, in_promo, losses, wins
    except (AttributeError, ValueError) as e:
        logging.warning("Requested queue does not exist")
        return None


# noinspection PyTypedDict
def get_info(summoner_id, region="EUW"):
    logging.info(f"Querying LOL API for Summoner '{summoner_id}'")
    summoner = cass.get_summoner(id=summoner_id, region=region)

    data = {}

    try:
        soloq = summoner.league_entries.fives
        soloq_info = get_queue_info(soloq)
        data['soloq'] = {
            "tier": soloq_info[0],
            "div": soloq_info[1],
            "lp": soloq_info[2],
            "in_promo": soloq_info[3],
            "losses": soloq_info[4],
            "wins": soloq_info[5]
        }

    except (AttributeError, ValueError) as e:
        logging.warning(f"No SoloQ Ranking for {summoner.name}")
        data['soloq'] = False

    try:
        flex = summoner.league_entries.flex
        flex_info = get_queue_info(flex)
        data['flex'] = {
            "tier": flex_info[0],
            "div": flex_info[1],
            "lp": flex_info[2],
            "in_promo": flex_info[3],
            "losses": flex_info[4],
            "wins": flex_info[5]
        }
    except (AttributeError, ValueError) as e:
        logging.warning(f"No Flex Ranking for {summoner.name}")
        data['flex'] = False

    return data