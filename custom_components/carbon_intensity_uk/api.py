import aiohttp
import logging
from datetime import datetime, timezone

_LOGGER = logging.getLogger(__name__)


class CarbonIntentisityApi:
    """Carbon Intensity API"""

    def __init__(self, postcode):
        self.postcode = postcode
        self.headers = {"Accept": "application/json"}
        _LOGGER.debug(str(self))

    def __str__(self):
        return "{ postcode: %s, headers: %s }" % (self.postcode, self.headers)


    async def async_get_lowest_intensity_for_next_day_period(self, from_time=datetime.now()):
        request_url = "https://api.carbonintensity.org.uk/regional/intensity/%s/fw24h/postcode/%s" % (from_time.strftime("%Y-%m-%dT%H:%MZ"), self.postcode)
        _LOGGER.debug("Request: %s" % request_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as resp:
                json_response = await resp.json()
                periods = dict()
                for period in json_response["data"]["data"]:
                   periods[period["intensity"]["forecast"]] = { "from": period["from"], "to": period["to"], "index": period["intensity"]["index"] }
                minimum_key = min(periods.keys())
                response = {
                    "data": {
                        "current_period_from": datetime.strptime(json_response["data"]["data"][0]["from"],"%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc),
                        "current_period_to": datetime.strptime(json_response["data"]["data"][0]["to"],"%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc),
                        "current_period_forecast": json_response["data"]["data"][0]["intensity"]["forecast"],
                        "current_period_index": json_response["data"]["data"][0]["intensity"]["index"],
                        "lowest_period_from": datetime.strptime(periods[minimum_key]["from"],"%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc),
                        "lowest_period_to": datetime.strptime(periods[minimum_key]["to"],"%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc),
                        "lowest_period_forecast": minimum_key,
                        "lowest_period_index": periods[minimum_key]["index"],
                        "unit": "gCO2/kWh",
                        "postcode": self.postcode,
                    }
                }
                _LOGGER.debug("Response: %s" % response)
                return response
