

def command_rankedinfo(data):
    soloq = data['soloq']
    flex = data['flex']

    send_msg = ""

    if not soloq:
        send_msg = "**SoloQ**\nNo SoloQ Information Found\n"
    else:
        send_msg = f"**SoloQ**\nCurrent Tier: {soloq['tier']} {soloq['div']} - {soloq['lp']} LP\n"
        if soloq['in_promo']:
            send_msg += "You are currently in **Promotion**\n"
        send_msg += f"Record: {soloq['wins']}-{soloq['losses']} " \
                    f"(**{100*soloq['wins'] / (soloq['wins']+soloq['losses']):.2f}%**)\n"

    send_msg += 40*"-"
    send_msg += "\n"

    if not flex:
        send_msg += "No FlexQ Information Found"
    else:
        send_msg += f"**Flex**\nCurrent Tier: {flex['tier']} {flex['div']} - {flex['lp']} LP\n"
        if flex['in_promo']:
            send_msg += "You are currently in **Promotion**\n"
        send_msg += f"Record: {flex['wins']}-{flex['losses']} " \
                    f"(**{100*flex['wins'] / (flex['wins'] + flex['losses']):.2f}%**)\n"

    return send_msg