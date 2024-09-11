from pprint import pprint
import sys, os
os.system("")

class Util:
    def __init__(self):
        pass 

    @staticmethod
    def init_progress_bar(maximum : int, message : str, length : int = 50) -> None:
        print(f"[{"-" * length}] 0% - 0 / {maximum} {message}", end="")
        sys.stdout.flush()

    @staticmethod
    def progress_bar(current : int, maximum : int, message : str, length : int = 50) -> None:
        progress = int(current/maximum * length)
        print("\x1b[2K", end="\r")
        print(f'[{"*" * progress}{"-" * (length - progress)}] {current/maximum*100:.2f}% - {current} / {maximum} {message}', end="")
        sys.stdout.flush()

    @staticmethod 
    def parse_message(message : dict) -> dict:

        try:
            message_id = message.get("id")
            author = message.get("author").get("id")
            channel_id = message.get("channel_id")
            content = message.get("content")
            timestamp = message.get("timestamp")
            edited = message.get("edited_timestamp") != None
            mention_everyone = message.get("mention_everyone")
            mention_people = [mentions.get("id") for mentions in message.get("mentions", [])]
            mention_roles = [int(mention) for mention in message.get("mention_roles", [])]
            pinned = message.get("pinned")
            message_type = message.get("type")
            stickers = message.get("sticker_items")

            attachments = [{
                "id": attachment.get("id"),
                "filename": attachment.get("filename"), 
                "type": attachment.get("content_type"),
                "size": attachment.get("size"),
                "url": attachment.get("proxy_url")
            } for attachment in message.get("attachments", [])]

            embeds = [{
                "type": embed.get("type"),
                "url": embed.get("url")
            } if embed.get("type") in ["article", "image", "video", "gifv", "link"] else embed for embed in message.get("embeds", [])]

            reactions = [reaction.get("emoji") for reaction in message.get("reactions", [])]

            reference = {key: message.get("message_reference", {})[key] for key in message.get("message_reference", {}) if key != "type"}

            if (reference != {} and "guild_id" not in reference):
                reference["guild_id"] = None

            return {
                "message_id": message_id,
                "author": author,
                "channel_id": channel_id,
                "content": content,
                "timestamp": timestamp,
                "edited": edited,
                "mentioned_everyone": mention_everyone,
                "mentioned_people": mention_people,
                "mentioned_roles": mention_roles,
                "pinned": pinned,
                "message_type": message_type,
                "stickers": stickers,
                "attachments": attachments,
                "embeds": embeds,
                "reactions": reactions,
                "reference": reference
            }
        except Exception as e:
            print()
            pprint(e)
            pprint(message)
            exit()

