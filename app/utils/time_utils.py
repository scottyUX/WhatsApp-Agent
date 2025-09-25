from datetime import datetime, timezone


class TimeUtils:
    @staticmethod
    def get_datetime() -> datetime:
        """
        Get the current date and time.
        return:
            return datetime object
        """
        return datetime.now(timezone.utc)


    @staticmethod
    def get_seconds() -> int:
        """
        Get the current timestamp in seconds.
        return:
            return int timestamp in seconds
        """
        return int(datetime.now(timezone.utc).timestamp())


    @staticmethod
    def get_milliseconds() -> int:
        """
        Converts the current timestamp to a milliseconds value.
        return:
            return int milliseconds value
        """
        return round(datetime.now(timezone.utc).timestamp() * 1000)
