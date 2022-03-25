import cassiopeia as cass
import os
from dotenv import load_dotenv
import logging
import uuid

# Initialize Logging - File and Command Line Output
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    handlers=[
                        logging.FileHandler("lolapi.log"),
                        logging.StreamHandler()
                    ])

load_dotenv()
RIOT_API = os.getenv('RIOT_API')

cass.set_riot_api_key(RIOT_API)


def get_summ_data(name, region="EUW"):
    summoner = cass.get_summoner(name=name, region=region)
    get_queues(summoner)

def get_queue_info(queue):
    try:
        div = queue.division.value
        tier = queue.tier.value
        in_promo = queue.promos is not None
        lp = queue.league_points

        return tier, div, lp, in_promo
    except (AttributeError, ValueError) as e:
        logging.warning("Requested queue does not exist")
        return None


def get_queues(summoner):
    if len(summoner.league_entries) == 0:
        logging.warning(f"{summoner.name} has no queue information")
        return

    try:
        soloq = summoner.league_entries.fives
        soloq_info = get_queue_info(soloq)
        print_queue_info(soloq_info, "SoloQ", summoner.name)

    except (AttributeError, ValueError) as e:
        logging.warning(f"No SoloQ Ranking for {summoner.name}")

    try:
        flex = summoner.league_entries.flex
        flex_info = get_queue_info(flex)
        print_queue_info(flex_info, "FlexQ", summoner.name)
    except (AttributeError, ValueError) as e:
        logging.warning(f"No Flex Ranking for {summoner.name}")



def print_queue_info(queue_info, queue_name, summoner_name):
    print(f"Player {summoner_name}")

    if queue_info is None:
        print(f"No information about {queue_name} was found!")
        return

    print(f"{queue_name}: {queue_info[0]} {queue_info[1]} - {queue_info[2]} LP")

    if queue_info[3]:
        print("Currently in Promo!")


#print(uuid.uuid4())
#print(uuid.uuid4())
#print(uuid.uuid4())
#print(uuid.uuid4())
#print(uuid.uuid4())
get_summ_data("Cpt Aw")
#get_summ_data("Secr3t")
#get_summ_data("Diviine")
#get_summ_data("EarnAce")
#get_summ_data("VictoriousMuffin")


