import datetime
import re

import dateutil
import parsedatetime
from dateparser import search, parse
from discord.ext import commands
from pytimeparse import parse as ptp_parse

from . import embeds, parser, misc


class HumanTimeParser(commands.Converter):
    # Source: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/time.py#L9 but modified
    # To my best knowledge this regex first creates a capture group named by its unit (years, months, etc)
    # This stores the quantity and the next part just parses its unit out. This gets repeated across multiple
    # units
    short_time_parse = re.compile("""(?:(?P<years>[0-9]{1,3})(?:years?|yr?))?             # e.g. 2y
                             (?:(?P<months>[0-9]{1,2})(?:months?|mo))?     # e.g. 2months
                             (?:(?P<weeks>[0-9]{1,4})(?:weeks?|wk?))?        # e.g. 10w
                             (?:(?P<days>[0-9]{1,5})(?:days?|d))?          # e.g. 14d
                             (?:(?P<hours>[0-9]{1,5})(?:hours?|hr?))?        # e.g. 12h
                             (?:(?P<minutes>[0-9]{1,5})(?:minutes?|m))?    # e.g. 10m
                             (?:(?P<seconds>[0-9]{1,5})(?:seconds?|s))?    # e.g. 15s
                          """, re.VERBOSE)
    calendar = parsedatetime.Calendar()

    def __init__(self, check=0):
        """Parses a natural datetime into one understood by the bot
        if check is 0 then it'll check to see if the timestamp is in the future
        if check is 1 then it'll check to see if the timestamp is from the past
        """
        self.check = check

    async def regex_match(self, ctx, argument, match):
        if match is not None and match.group(0):
            date_format = {unit: int(quantity) for unit, quantity in match.groupdict(default=0).items()}
            date = datetime.datetime.utcnow() + dateutil.relativedelta.relativedelta(**date_format)
            match_span = match.span()
            if await self.validate(date):
                return date, (argument[:match_span[0]] + argument[match_span[1] + 1:])

    async def detect_and_plus_space(self, match_objects, argument):
        """
        :param The list of re match objects:
        :param argument is the base message itself:
        :return: a few exit codes based on a few conditions:
        0: Nothing eventful has been found
        1. Regex statements is interconnected via "And"s
        2. Regex statements is seperated by a space in which it is removed
        """
        spans: list = [m.span() for m in match_objects]
        highest = max(map(max, spans))
        lowest = min(map(min, spans))

        string = argument[lowest:highest]
        if "and" in string and string.count("and") == len(spans)-1:
            return string, 1

        spans = [item for subtuple in spans for item in subtuple]
        string, lowest, highest = await self.locate_next_eachother(argument, spans)
        results = self.short_time_parse.fullmatch("".join(string.split()))
        if results:
            return results, 2, [lowest, highest]
        return None, 0

    async def locate_next_eachother(self, argument, spans):
        almost_final_spans, accumulator = [], [0, 0]
        for low, high in zip(*[iter(spans)]*2):
            if accumulator[1]+1 == low:
                almost_final_spans.append(accumulator[0]), almost_final_spans.append(accumulator[1])
                almost_final_spans.append(low), almost_final_spans.append(high)
            accumulator = [low, high]

        if almost_final_spans:
            highest = max(almost_final_spans)
            lowest = min(almost_final_spans)
            string = argument[lowest:highest]
            return string, lowest, highest
        return "None", None, None

    async def cal_adjacent(self, argument, cal_result):
        spans = []
        for results in cal_result:
            _, _, start, end, _ = results
            spans.append(start), spans.append(end)
        return self.locate_next_eachother(argument, spans)

    async def convert(self, ctx, argument):
        skip_regex_checks = False
        try:
            matches = self.short_time_parse.finditer(argument)
            match, time_string_storage = [], set()
            for m in matches:
                if m and m.group(0) and m.group(0) not in time_string_storage:
                    time_string_storage.add(m.group(0))
                    match.append(m)

            if match:
                detection_results = await self.detect_and_plus_space(match, argument)
                if detection_results[1] is 1:
                    skip_regex_checks = True
                elif detection_results[1] is 2:
                    date_format = {unit: int(quantity) for unit, quantity in detection_results[0].groupdict(default=0).items()}
                    date = datetime.datetime.utcnow() + dateutil.relativedelta.relativedelta(**date_format)
                    indices = detection_results[2]
                    if await self.validate(date):
                        return date, (argument[:indices[0]] + argument[indices[1]+1:])

            if len(match) > 1 and not skip_regex_checks:
                parsed_list = []
                for m in match:
                    parsed_list.append((await self.regex_match(ctx, argument, m)))
                return await self.search_variant_cl(ctx, parsed_list)
            elif len(match) == 1 and not skip_regex_checks:
                return await self.regex_match(ctx, argument, match[0])

            # Extracts the text using parsedatetime
            pdt_dates = self.calendar.nlp(argument, sourceTime=(datetime.datetime.utcnow()))
            raw_date_strings = []
            if pdt_dates:
                for data in pdt_dates:
                    raw_date_strings.append(data[4])

                if raw_date_strings:
                    results = []
                    for time_string in raw_date_strings:
                        time_exp_parsed = ptp_parse(time_string)
                        if time_exp_parsed:
                            time_exp_parsed = dateutil.relativedelta.relativedelta(seconds=time_exp_parsed)
                            results.append((datetime.datetime.utcnow() + time_exp_parsed,
                                            argument.replace(time_string, "").strip()))
                        else:
                            dp_parsed = await self.dateparser_parse(ctx, time_string)
                            if dp_parsed:
                                dp_parsed = list(dp_parsed)
                                dp_parsed[1] = argument.replace(dp_parsed[1], "").strip()
                                results.append(dp_parsed)

                    # If more than one result was found then it'll send a embed telling users to pick
                    if results and len(results) > 1:
                        return await self.search_variant_cl(ctx, results)
                    elif results:
                        return results[0]

            dp_result = await self.dateparser_search(ctx, argument)
            if dp_result is None or not await self.validate(dp_result[0]):
                raise ctx.error("Invalid date! Use something like \"2 Weeks\", \"2 hours 50 min\"")
            else:
                return dp_result[0], dp_result[1]

        except OverflowError:
            raise ctx.error("The time value you have specified is too far away from today! "
                            "Please try something closer to today.")

        except Exception as e:
            raise e

    async def validate(self, date):
        if date is None:
            return False
        elif self.check is 0:
            if date > datetime.datetime.utcnow():
                return True
        elif self.check is 1:
            if date < datetime.datetime.utcnow():
                return True
        return False

    @staticmethod
    async def simple_future_timestamp_parser(message):
        async def parse_time(message, each=3):
            timestamp, remove = None, None

            if len(message) % 2 is 0:
                message += ["Placeholder"]

            for back_front in zip(*[iter(message)] * each):
                backup = back_front

                # If next is in the phase then it would likely be in a format such as
                # "next day" or "next week". Therefore when we got the index of where
                # "next" is located, the index the term after it would be the subject
                # IE day, week, etc.
                if "next" in back_front:
                    index_of_next = message.index("next")
                    back_front = [message[index_of_next], message[index_of_next + 1]]
                elif "tomorrow" in back_front:
                    backup = ["tomorrow"]
                    back_front = ["tomorrow"]
                elif "in" not in back_front and len(og_msg) == 2:
                    back_front = ["in"] + og_msg

                timestamp = parse(" ".join(back_front), languages=["en"], settings={"RELATIVE_BASE": datetime.datetime.utcnow()})

                if timestamp:
                    remove = list(backup)
                    break

            if not timestamp or not remove:
                return False

            if "in" in message[:3] or "in" in message[-3:]:
                remove.insert(0, "in")

            return timestamp, " ".join(message).replace(f"{' '.join(remove)}", "")

        og_msg = message.copy()

        result = await parse_time(message, each=2)
        if result is False:
            result = await parse_time(message, each=3)
            return result if result else False
        else:
            return result

    async def dateparser_search(self, ctx, message, return_raw=False):
        all_parsed_times = []
        datetime_parsed = search.search_dates(message, languages=["en"],
                                              settings={"RELATIVE_BASE": datetime.datetime.utcnow()})
        if datetime_parsed:
            for parsed_time in datetime_parsed:
                valid_time = await self.validate(parsed_time[1])
                if valid_time is False:
                    og_tm_text = parsed_time[0]
                    time = "in " + og_tm_text
                    time = search.search_dates(time, languages=["en"], settings={"RELATIVE_BASE": datetime.datetime.utcnow()})

                    if time and await self.validate(time[0][1]):
                        all_parsed_times.append((time[0][1], message.replace(og_tm_text, "")))

                elif valid_time is True:
                    all_parsed_times.append((parsed_time[1], message.replace(parsed_time[0], "")))
        if not all_parsed_times:
            two_term_timestamp = await self.simple_future_timestamp_parser(message.split())
            if two_term_timestamp:
                return two_term_timestamp
        else:
            if len(all_parsed_times) > 1:
                if return_raw:
                    return all_parsed_times
                else:
                    return await self.search_variant_cl(ctx, all_parsed_times)
            else:
                return all_parsed_times[0]

    async def dateparser_parse(self, ctx, message):
        dp_result = parse(message, languages=["en"], settings={"RELATIVE_BASE": datetime.datetime.utcnow()})
        if dp_result:
            if await self.validate(dp_result):
                return dp_result, message
            elif "in" not in message:
                return await self.dateparser_parse(ctx, f"in {message}")
        else:
            return None

    async def search_variant_cl(self, ctx, time_list):
        gather_human_readable = []
        possible_choices = []
        for index, time in enumerate(time_list):
            if await self.validate(time[0]):
                read = await parser.human_readable_datetime_parser(ctx, time[0])
                possible_choices.append(time)
                gather_human_readable.append(f"**{len(gather_human_readable) + 1}**{' in ' if self.check is 0 else ''}"
                                             f"{read}{' ago ' if self.check is 1 else ''}\n\n")

        tm_amt = len(gather_human_readable)
        gather_human_readable = await misc.distribute_pages(gather_human_readable, per_page=5)

        pick_timestamp = embeds.InputChooserPager(ctx, gather_human_readable, tm_amt - 1,
                                                  title="It seems like multiple time values were parsed out. "
                                                        "Please go ahead and choose the correct one. "
                                                        "If none of the following is correct try a different format!")
        option = await pick_timestamp.start()
        if option is None:
            return None
        else:
            return possible_choices[option - 1]


class NoCtxHumanTimeParser:
    short_time_parse = re.compile("""(?:(?P<years>[0-9])(?:years?|y))?             # e.g. 2y
                             (?:(?P<months>[0-9]{1,2})(?:months?|mo))?     # e.g. 2months
                             (?:(?P<weeks>[0-9]{1,4})(?:weeks?|w))?        # e.g. 10w
                             (?:(?P<days>[0-9]{1,5})(?:days?|d))?          # e.g. 14d
                             (?:(?P<hours>[0-9]{1,5})(?:hours?|h))?        # e.g. 12h
                             (?:(?P<minutes>[0-9]{1,5})(?:minutes?|m))?    # e.g. 10m
                             (?:(?P<seconds>[0-9]{1,5})(?:seconds?|s))?    # e.g. 15s
                          """, re.VERBOSE)
    calendar = parsedatetime.Calendar()

    def __init__(self, check=0):
        """Parses a natural datetime into one understood by the bot
        if check is 0 then it'll check to see if the timestamp is in the future
        if check is 1 then it'll check to see if the timestamp is from the past
        """
        self.check = check

    async def regex_match(self, argument, match):
        if match is not None and match.group(0):
            date_format = {unit: int(quantity) for unit, quantity in match.groupdict(default=0).items()}
            date = datetime.datetime.utcnow() + dateutil.relativedelta.relativedelta(**date_format)
            match_span = match.span()
            if await self.validate(date):
                return date, (argument[:match_span[0]] + argument[match_span[1] + 1:])

    async def convert(self, argument):
        try:
            matches = self.short_time_parse.finditer(argument)
            match = [m for m in matches if m is not None and m.group(0)]
            if match:
                return await self.regex_match(argument, match[0])

            data = self.calendar.nlp(argument, sourceTime=datetime.datetime.utcnow())
            test_to_see_if_more_dates = len(search.search_dates(argument, settings={"RELATIVE_BASE":
                                                                                    datetime.datetime.utcnow()}))
            if data is None or len(data) == 0 or test_to_see_if_more_dates > 1:
                old_time = await self.old_timestamp_parser(argument)
                if await self.validate(old_time[0]):
                    return old_time
                else:
                    pass

            dt, _, start, end, dt_string = data[0]
            if await self.validate(dt):
                return dt, (dt_string[:start] + dt_string[end+1:])
        except Exception as e:
            raise e

    async def validate(self, date):
        if date is None:
            return False
        if self.check is 0:
            if date > datetime.datetime.utcnow():
                return True
        elif self.check is 1:
            if date < datetime.datetime.utcnow():
                return True
        return False

    @staticmethod
    async def simple_future_timestamp_parser(message):
        async def parse_time(message, each=3):
            timestamp, remove = None, None

            if len(message) % 2 is 0:
                message += ["Placeholder"]

            for back_front in zip(*[iter(message)] * each):
                backup = back_front

                # If next is in the phase then it would likely be in a format such as
                # "next day" or "next week". Therefore when we got the index of where
                # "next" is located, the index the term after it would be the subject
                # IE day, week, etc.
                if "next" in back_front:
                    index_of_next = message.index("next")
                    back_front = [message[index_of_next], message[index_of_next + 1]]
                elif "tomorrow" in back_front:
                    backup = ["tomorrow"]
                    back_front = ["tomorrow"]
                elif "in" not in back_front and len(og_msg) == 2:
                    back_front = ["in"] + og_msg

                timestamp = parse(" ".join(back_front), languages=["en"], settings={"RELATIVE_BASE": datetime.datetime.utcnow()})

                if timestamp:
                    remove = list(backup)
                    break

            if not timestamp or not remove:
                return False

            if "in" in message[:3] or "in" in message[-3:]:
                remove.insert(0, "in")

            return timestamp, " ".join(message).replace(f"{' '.join(remove)}", "")

        og_msg = message.copy()

        result = await parse_time(message, each=2)
        if result is False:
            result = await parse_time(message, each=3)
            return result if result else False
        else:
            return result

    async def old_timestamp_parser(self, message):
        async def remove_content_from_timestamp(returned_timestamp_list):
            new_timestamp = []
            for letters in returned_timestamp_list.split():
                if len(letters) == 1 and not letters.isdigit():
                    pass
                else:
                    new_timestamp.append(letters)
            return new_timestamp

        parsed_complex_timestamp = None
        parsed_time = search.search_dates(message, languages=["en"],
                                          settings={"RELATIVE_BASE": datetime.datetime.utcnow()})

        # If more than two datetimes were parsed out, this would select the first
        if parsed_time and len(parsed_time) > 1:
            parsed_time = (parsed_time[0],)

        # Makes sure a timestamp was parsed.
        if parsed_time:
            if await self.validate(parsed_time[0][1]) is False:
                time_denotion_string = " ".join(await remove_content_from_timestamp(parsed_time[0][0]))
                time = "in " + time_denotion_string
                time = search.search_dates(time, languages=["en"], settings={"RELATIVE_BASE": datetime.datetime.utcnow()})

                if time and await self.validate(time[0][1]):
                    parsed_complex_timestamp = (time[0][1], message.replace(time_denotion_string, ""))

            elif await self.validate(parsed_time[0][1]) is True:
                timestamp = " ".join(await remove_content_from_timestamp(parsed_time[0][0]))
                parsed_complex_timestamp = (parsed_time[0][1], message.replace(timestamp, ""))
        if parsed_complex_timestamp is None:
            two_term_timestamp = await self.simple_future_timestamp_parser(message.split())
            if two_term_timestamp:
                return two_term_timestamp
        else:
            return parsed_complex_timestamp
