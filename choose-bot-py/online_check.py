import os
import json

announce_channel_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "data/announce_channel.json")

async def get_channel_data():
    try:
        with open(announce_channel_path, 'r') as f:
            announce = json.load(f)
    except FileNotFoundError:
        # create a new json file
        announce = {}
        with open(announce_channel_path, 'w') as f:
            json.dump(announce, f, indent=4)
    except json.JSONDecodeError:
        print("Error: JSON decode failed. File may be corrupted.")

    return announce

async def set_announce_channel(guild, channel):
    announce = await get_channel_data()
    channel_id = channel.id

    if str(guild.id) in announce:
        if announce[str(guild.id)]['channel_id'] == channel_id:
            return False
        else:
            announce[str(guild.id)]['channel_id'] = channel_id
    else:
        announce.update({str(guild.id): {"channel_id": channel_id}})


    with open(announce_channel_path, 'w') as f:
        json.dump(announce, f, indent=4)
        return