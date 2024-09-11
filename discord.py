from requests import post, get, put, delete
from log import Log
from util import Util
from time import sleep
from json import loads

class Discord:
    def __init__(self, auth_key : str, log_location : str, full_error_log_location : str):
        self.key = auth_key
        self.header = {'Authorization': self.key}
        self.log_messages = log_location != ""
        self.log_full_error_messages = full_error_log_location != ""
        self.log_location = None
        self.log = None 
        self.full_error_log = None
        self.full_log_location = None

        if self.log_messages:
            self.log_location = log_location
            self.log = Log(self.log_location)

        if self.log_full_error_messages:
            self.full_log_location = full_error_log_location
            self.full_error_log = Log(self.full_log_location)

    def handle_error_messages(self, status : int, message : dict, event : str) -> None: 
        if self.log != None:
            self.log.error(f"FAILED TO {event} DUE TO {message["message"].upper()}")
        
        if self.log != None:
            self.full_error_log.error(str(message))

    def handle_success_messages(self, status : int, message : dict, event : str) -> None:
        if self.log != None:
            self.log.info(f"SUCCESS TO {event}")

    def clear_all_logs(self) -> None:
        self.log.clear()
        self.full_error_log.clear()
        print("All Logs Cleared")

    def send_message(self, channel_id : int, message : str) -> bool:
        URL = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        response = post(URL, data={'content': message}, headers=self.header)
        status = response.status_code 
        response_text = {} if response.text == "" else loads(response.text)

        if status == 200:
            self.handle_success_messages(status, response_text, f"SEND MESSAGE IN CHANNEL {channel_id}")
            return True 
        else:
            self.handle_error_messages(status, response_text, f"SEND MESSAGE IN CHANNEL {channel_id}")
            return False

    def send_messages(self, channel_id : int, messages : list[str], wait_time : int = 0) -> tuple[bool, str]:
        last_messages_sent = None
        num_of_messages = len(messages)

        Util.init_progress_bar(num_of_messages, "Starting To Send Messages")

        for i in range(num_of_messages):
            message = message[i]
            success = self.send_message(channel_id, message)
            if not success:
                Util.progress_bar(num_of_messages, num_of_messages, "Error Sending Messages")
                return False, last_messages_sent
            else:
                Util.progress_bar(i + 1, num_of_messages, "Fetching Messages")
                last_messages_sent = message
            sleep(wait_time)

        Util.progress_bar(num_of_messages, num_of_messages, "Finished Sending Messages")
        return True, last_messages_sent

    def get_message(self, channel_id : int, limit : int, parameters : dict) -> tuple[bool, list[dict]]:
        if limit > 100:
            return False, {}
        
        URL = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}&" + "&".join([f"{i}={parameters[i]}" for i in parameters])
        response = get(URL, headers=self.header)
        status = response.status_code 
        response_text = {} if response.text == "" else loads(response.text)

        if status == 200:
            response_text = [Util.parse_message(i) for i in response_text]
            for i in response_text:
                reactions = [j["name"] if j["id"] == None else f"{j["name"]}:{j["id"]}" for j in i.get("reactions")]
                reactions_data = self.get_reactions_of_message(i.get("channel_id"), i.get("message_id"), reactions)
                for j in range(len(i.get("reactions", []))):
                    i.get("reactions")[j]["users"] = reactions_data[1][j][list(reactions_data[1][j].keys())[0]]

            self.handle_success_messages(status, response_text, f"FETCH {len(response_text)} MESSAGE(S) FROM CHANNEL {channel_id}")
            return True, response_text 
        else:
            self.handle_error_messages(status, response_text, f"FETCH {len(response_text)} MESSAGE(S) FROM CHANNEL {channel_id}")
            return False, response_text

    def get_messages(self, channel_id : int, limit : int, wait_time : int = 0, parameters : dict = {}) -> tuple[bool, list[dict]]:
        messages_gotten = []
        last_message_id = None
        max_messages = limit 
        Util.init_progress_bar(max_messages, "Starting To Fetch Messages")

        while limit > 0:
            success, response = self.get_message(channel_id, min(50, limit), parameters)
            if not success:
                Util.progress_bar(max_messages, max_messages, "Error Fetching Messages")
                return False, messages_gotten
            elif response != []:
                Util.progress_bar(max_messages - limit + len(response), max_messages, "Fetching Messages")
                
                if parameters == {} or list(parameters.keys())[0] != "after":
                    messages_gotten += response
                else:
                    messages_gotten += response[::-1]

                last_message_id = response[-1]["message_id"]
                parameters = {list(parameters.keys())[0] if parameters != {} else "before": last_message_id}

                if len(response) < min(50, limit):
                    limit = 0
                else:
                    limit = max(0, limit - len(response))
            else:
                limit = 0
            sleep(wait_time)

        Util.progress_bar(max_messages, max_messages, "Finished Fetching Messages")
        return True, messages_gotten

    def get_reaction_of_message(self, channel_id : int, message_id : int, reaction : str) -> tuple[bool, list[int]]:
        URL = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{reaction}"
        response = get(URL, headers=self.header)
        status = response.status_code 
        response_text = {} if response.text == "" else loads(response.text)

        if status == 200:
            response_text = [i.get("id") for i in response_text]
            self.handle_success_messages(status, response_text, f"FETCH REACTION {reaction} FROM MESSAGE {message_id} IN CHANNEL {channel_id}")
            return True, response_text 
        else:
            self.handle_error_messages(status, response_text, f"FETCH REACTION {reaction} FROM MESSAGE {message_id} IN CHANNEL {channel_id}")
            return False, response_text

    def get_reactions_of_message(self, channel_id : int, message_id : int, reactions : list[str]) -> tuple[bool, dict[str, list[int]]]:
        reactions_of_message = []
        for i in reactions:
            success, response = self.get_reaction_of_message(channel_id, message_id, i)
            if not success:
                return False, reactions_of_message
            else:
                reactions_of_message += [{
                    i: response
                }]
        
        return True, reactions_of_message

    def add_reaction(self, channel_id : int, message_id : int, reaction : str) -> bool:
        URL = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{reaction}/@me"
        response = put(URL, headers=self.header)
        status = response.status_code 
        response_text = {} if response.text == "" else loads(response.text)

        if status == 200:
            self.handle_success_messages(status, response_text, f"ADD REACTION {reaction} ON MESSAGE {message_id} IN CHANNEL {channel_id}")
            return True 
        else:
            self.handle_error_messages(status, response_text, f"ADD REACTION {reaction} ON MESSAGE {message_id} IN CHANNEL {channel_id}")
            return False

    def delete_reaction(self, channel_id : int, message_id : int, reaction : str) -> bool:
        URL = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{reaction}/0/@me"
        response = delete(URL, headers=self.header)
        status = response.status_code 
        response_text = {} if response.text == "" else loads(response.text)

        if status == 200:
            self.handle_success_messages(status, response_text, f"REMOVE REACTION {reaction} ON MESSAGE {message_id} IN CHANNEL {channel_id}")
            return True 
        else:
            self.handle_error_messages(status, response_text, f"REMOVE REACTION {reaction} ON MESSAGE {message_id} IN CHANNEL {channel_id}")
            return False