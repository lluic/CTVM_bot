import logging

from telegram import Update
from telegram.ext import ContextTypes

from CTVM_bot.restaurant_list import RestaurantList


class PollManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PollManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.poll_mapping = {}

        self._initialized = True

    async def poll_update_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        poll = update.poll
        if poll.id in self.poll_mapping:
            restaurant_name = self.poll_mapping[poll.id]
            total_votes = sum(option.voter_count for option in poll.options)
            if total_votes > 0:
                rating_sum = sum(
                    (i + 1) * option.voter_count
                    for i, option in enumerate(poll.options)
                )
                average = rating_sum / total_votes
            else:
                average = 0
            RestaurantList().update_rating_and_votes(
                name=restaurant_name,
                rating=average,
                total_votes=total_votes,
            )
            logging.getLogger(__name__).info(
                f"Updated rating for {restaurant_name}: {average:.1f} from {total_votes} votes"
            )
