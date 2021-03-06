import pandas as pd
import re
from pyquery import PyQuery as pq
from .. import utils
from .constants import (BOXSCORE_ELEMENT_INDEX,
                        BOXSCORE_SCHEME,
                        BOXSCORE_URL,
                        BOXSCORES_URL,
                        DOUBLE_HEADER_INDICES)
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.mlb.constants import DAY, NIGHT


class Boxscore(object):
    """
    Detailed information about the final statistics for a game.

    Stores all relevant information for a game such as the date, time,
    location, result, and more advanced metrics such as the number of strikes,
    a pitcher's influence on the game, the number of putouts and much more.

    Parameters
    ----------
    uri : string
        The relative link to the boxscore HTML page, such as
        'BOS/BOS201806070'.
    """
    def __init__(self, uri):
        self._uri = uri
        self._date = None
        self._time = None
        self._attendance = None
        self._venue = None
        self._time_of_day = None
        self._duration = None
        self._away_name = None
        self._home_name = None
        self._winner = None
        self._winning_name = None
        self._winning_abbr = None
        self._losing_name = None
        self._losing_abbr = None
        self._losing_abbr = None
        self._away_at_bats = None
        self._away_runs = None
        self._away_hits = None
        self._away_rbi = None
        self._away_earned_runs = None
        self._away_bases_on_balls = None
        self._away_strikeouts = None
        self._away_plate_appearances = None
        self._away_batting_average = None
        self._away_on_base_percentage = None
        self._away_slugging_percentage = None
        self._away_on_base_plus = None
        self._away_pitches = None
        self._away_strikes = None
        self._away_win_probability_for_offensive_player = None
        self._away_average_leverage_index = None
        self._away_win_probability_added = None
        self._away_win_probability_subtracted = None
        self._away_base_out_runs_added = None
        self._away_putouts = None
        self._away_assists = None
        self._away_innings_pitched = None
        self._away_home_runs = None
        self._away_strikes_by_contact = None
        self._away_strikes_swinging = None
        self._away_strikes_looking = None
        self._away_grounded_balls = None
        self._away_fly_balls = None
        self._away_line_drives = None
        self._away_unknown_bat_type = None
        self._away_game_score = None
        self._away_inherited_runners = None
        self._away_inherited_score = None
        self._away_win_probability_by_pitcher = None
        self._away_base_out_runs_saved = None
        self._home_at_bats = None
        self._home_runs = None
        self._home_hits = None
        self._home_rbi = None
        self._home_earned_runs = None
        self._home_bases_on_balls = None
        self._home_strikeouts = None
        self._home_plate_appearances = None
        self._home_batting_average = None
        self._home_on_base_percentage = None
        self._home_slugging_percentage = None
        self._home_on_base_plus = None
        self._home_pitches = None
        self._home_strikes = None
        self._home_win_probability_for_offensive_player = None
        self._home_average_leverage_index = None
        self._home_win_probability_added = None
        self._home_win_probability_subtracted = None
        self._home_base_out_runs_added = None
        self._home_putouts = None
        self._home_assists = None
        self._home_innings_pitched = None
        self._home_home_runs = None
        self._home_strikes_by_contact = None
        self._home_strikes_swinging = None
        self._home_strikes_looking = None
        self._home_grounded_balls = None
        self._home_fly_balls = None
        self._home_line_drives = None
        self._home_unknown_bat_type = None
        self._home_game_score = None
        self._home_inherited_runners = None
        self._home_inherited_score = None
        self._home_win_probability_by_pitcher = None
        self._home_base_out_runs_saved = None

        self._parse_game_data(uri)

    def _retrieve_html_page(self, uri):
        """
        Download the requested HTML page.

        Given a relative link, download the requested page and strip it of all
        comment tags before returning a pyquery object which will be used to
        parse the data.

        Parameters
        ----------
        uri : string
            The relative link to the boxscore HTML page, such as
            'BOS/BOS201806070'.

        Returns
        -------
        PyQuery object
            The requested page is returned as a queriable PyQuery object with
            the comment tags removed.
        """
        url = BOXSCORE_URL % uri
        try:
            url_data = pq(url)
        except:
            return None
        return pq(utils._remove_html_comment_tags(url_data))

    def _parse_game_date_and_location(self, field, boxscore):
        """
        Retrieve the game's date and location.

        The date and location of the game follow a more complicated parsing
        scheme and should be handled differently from other tags. Both fields
        are separated by a newline character ('\n') with the first line being
        the date and the second being the location.

        Parameters
        ----------
        field : string
            The name of the attribute to parse
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.

        Returns
        -------
        string
            Depending on the requested field, returns a text representation of
            either the date or location of the game.
        """
        scheme = BOXSCORE_SCHEME[field]
        items = [i.text() for i in boxscore(scheme).items()]
        index = BOXSCORE_ELEMENT_INDEX[field]
        game_info = items[0].split('\n')
        double_header = False
        for item in items:
            if 'first game of doubleheader' in item.lower() or \
               'second game of doubleheader' in item.lower():
                double_header = True
                if field == 'date':
                    return game_info[0]
                for element in game_info:
                    if field == 'time_of_day':
                        if 'night game' in element.lower() or \
                           'day game' in element.lower():
                            return element
                        continue  # pragma: no cover
                    matcher = DOUBLE_HEADER_INDICES[field]
                    if matcher in element.lower():
                        return element
        # Triggered for double headers when a specific field is not included
        # in the game information summary. For double headers, random fields
        # are omitted for no apparent reason and should be parsed differently.
        # If the field can't be found, it should return a default value of an
        # empty string.
        if double_header:
            return ''
        return game_info[index]

    def _parse_name(self, field, boxscore):
        """
        Retrieve the team's complete name tag.

        Both the team's full name (embedded in the tag's text) and the team's
        abbreviation are stored in the name tag which can be used to parse
        the winning and losing team's information.

        Parameters
        ----------
        field : string
            The name of the attribute to parse
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.

        Returns
        -------
        PyQuery object
            The complete text for the requested tag.
        """
        scheme = BOXSCORE_SCHEME[field]
        return boxscore(scheme)

    def _parse_game_data(self, uri):
        """
        Parses a value for every attribute.

        This function looks through every attribute and retrieves the value
        according to the parsing scheme and index of the attribute from the
        passed HTML data. Once the value is retrieved, the attribute's value is
        updated with the returned result.

        Note that this method is called directly once Boxscore is invoked and
        does not need to be called manually.

        Parameters
        ----------
        uri : string
            The relative link to the boxscore HTML page, such as
            'BOS/BOS201806070'.
        """
        boxscore = self._retrieve_html_page(uri)
        # If the boxscore is None, the game likely hasn't been played yet and
        # no information can be gathered. As there is nothing to grab, the
        # class instance should just be empty.
        if not boxscore:
            return

        for field in self.__dict__:
            # Remove the '_' from the name
            short_field = str(field)[1:]
            if short_field == 'winner' or \
               short_field == 'winning_name' or \
               short_field == 'winning_abbr' or \
               short_field == 'losing_name' or \
               short_field == 'losing_abbr' or \
               short_field == 'uri':
                continue
            if short_field == 'date' or \
               short_field == 'time' or \
               short_field == 'venue' or \
               short_field == 'attendance' or \
               short_field == 'time_of_day' or \
               short_field == 'duration':
                value = self._parse_game_date_and_location(short_field,
                                                           boxscore)
                setattr(self, field, value)
                continue
            if short_field == 'away_name' or \
               short_field == 'home_name':
                value = self._parse_name(short_field, boxscore)
                setattr(self, field, value)
                continue
            index = 0
            if short_field in BOXSCORE_ELEMENT_INDEX.keys():
                index = BOXSCORE_ELEMENT_INDEX[short_field]
            value = utils._parse_field(BOXSCORE_SCHEME,
                                       boxscore,
                                       short_field,
                                       index)
            setattr(self, field, value)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the string URI that is used to
        instantiate the class, such as 'BOS201806070'.
        """
        if self._away_runs is None and self._home_runs is None:
            return None
        fields_to_include = {
            'date': self.date,
            'time': self.time,
            'venue': self.venue,
            'attendance': self.attendance,
            'duration': self.duration,
            'time_of_day': self.time_of_day,
            'winner': self.winner,
            'winning_name': self.winning_name,
            'winning_abbr': self.winning_abbr,
            'losing_name': self.losing_name,
            'losing_abbr': self.losing_abbr,
            'away_at_bats': self.away_at_bats,
            'away_runs': self.away_runs,
            'away_hits': self.away_hits,
            'away_rbi': self.away_rbi,
            'away_earned_runs': self.away_earned_runs,
            'away_bases_on_balls': self.away_bases_on_balls,
            'away_strikeouts': self.away_strikeouts,
            'away_plate_appearances': self.away_plate_appearances,
            'away_batting_average': self.away_batting_average,
            'away_on_base_percentage': self.away_on_base_percentage,
            'away_slugging_percentage': self.away_slugging_percentage,
            'away_on_base_plus': self.away_on_base_plus,
            'away_pitches': self.away_pitches,
            'away_strikes': self.away_strikes,
            'away_win_probability_for_offensive_player':
            self.away_win_probability_for_offensive_player,
            'away_average_leverage_index': self.away_average_leverage_index,
            'away_win_probability_added': self.away_win_probability_added,
            'away_win_probability_subtracted':
            self.away_win_probability_subtracted,
            'away_base_out_runs_added': self.away_base_out_runs_added,
            'away_putouts': self.away_putouts,
            'away_assists': self.away_assists,
            'away_innings_pitched': self.away_innings_pitched,
            'away_home_runs': self.away_home_runs,
            'away_strikes_by_contact': self.away_strikes_by_contact,
            'away_strikes_swinging': self.away_strikes_swinging,
            'away_strikes_looking': self.away_strikes_looking,
            'away_grounded_balls': self.away_grounded_balls,
            'away_fly_balls': self.away_fly_balls,
            'away_line_drives': self.away_line_drives,
            'away_unknown_bat_type': self.away_unknown_bat_type,
            'away_game_score': self.away_game_score,
            'away_inherited_runners': self.away_inherited_runners,
            'away_inherited_score': self.away_inherited_score,
            'away_win_probability_by_pitcher':
            self.away_win_probability_by_pitcher,
            'away_base_out_runs_saved': self.away_base_out_runs_saved,
            'home_at_bats': self.home_at_bats,
            'home_runs': self.home_runs,
            'home_hits': self.home_hits,
            'home_rbi': self.home_rbi,
            'home_earned_runs': self.home_earned_runs,
            'home_bases_on_balls': self.home_bases_on_balls,
            'home_strikeouts': self.home_strikeouts,
            'home_plate_appearances': self.home_plate_appearances,
            'home_batting_average': self.home_batting_average,
            'home_on_base_percentage': self.home_on_base_percentage,
            'home_slugging_percentage': self.home_slugging_percentage,
            'home_on_base_plus': self.home_on_base_plus,
            'home_pitches': self.home_pitches,
            'home_strikes': self.home_strikes,
            'home_win_probability_for_offensive_player':
            self.home_win_probability_for_offensive_player,
            'home_average_leverage_index': self.home_average_leverage_index,
            'home_win_probability_added': self.home_win_probability_added,
            'home_win_probability_subtracted':
            self.home_win_probability_subtracted,
            'home_base_out_runs_added': self.home_base_out_runs_added,
            'home_putouts': self.home_putouts,
            'home_assists': self.home_assists,
            'home_innings_pitched': self.home_innings_pitched,
            'home_home_runs': self.home_home_runs,
            'home_strikes_by_contact': self.home_strikes_by_contact,
            'home_strikes_swinging': self.home_strikes_swinging,
            'home_strikes_looking': self.home_strikes_looking,
            'home_grounded_balls': self.home_grounded_balls,
            'home_fly_balls': self.home_fly_balls,
            'home_line_drives': self.home_line_drives,
            'home_unknown_bat_type': self.home_unknown_bat_type,
            'home_game_score': self.home_game_score,
            'home_inherited_runners': self.home_inherited_runners,
            'home_inherited_score': self.home_inherited_score,
            'home_win_probability_by_pitcher':
            self.home_win_probability_by_pitcher,
            'home_base_out_runs_saved': self.home_base_out_runs_saved
        }
        return pd.DataFrame([fields_to_include], index=[self._uri])

    @property
    def date(self):
        """
        Returns a ``string`` of the date the game took place.
        """
        return self._date

    @property
    def time(self):
        """
        Returns a ``string`` of the time the game started.
        """
        return self._time.replace('Start Time: ', '')

    @property
    def venue(self):
        """
        Returns a ``string`` of the name of the ballpark where the game was
        played.
        """
        return self._venue.replace('Venue: ', '')

    @property
    def attendance(self):
        """
        Returns an ``int`` of the game's listed attendance.
        """
        attendance = self._attendance.replace('Attendance: ', '')
        try:
            return int(attendance.replace(',', ''))
        except ValueError:
            return 0

    @property
    def duration(self):
        """
        Returns a ``string`` of the game's duration in the format 'H:MM'.
        """
        return self._duration.replace('Game Duration: ', '')

    @property
    def time_of_day(self):
        """
        Returns a ``string`` constant indicated whether the game was played
        during the day or at night.
        """
        if 'night' in self._time_of_day.lower():
            return NIGHT
        return DAY

    @property
    def winner(self):
        """
        Returns a ``string`` constant indicating whether the home or away team
        won.
        """
        if self.home_runs > self.away_runs:
            return HOME
        return AWAY

    @property
    def winning_name(self):
        """
        Returns a ``string`` of the winning team's name, such as 'Houston
        Astros'.
        """
        if self.winner == HOME:
            return self._home_name.text()
        return self._away_name.text()

    @property
    def winning_abbr(self):
        """
        Returns a ``string`` of the winning team's abbreviation, such as 'HOU'
        for the Houston Astros.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._home_name)
        return utils._parse_abbreviation(self._away_name)

    @property
    def losing_name(self):
        """
        Returns a ``string`` of the losing team's name, such as 'Los Angeles
        Dodgers'.
        """
        if self.winner == HOME:
            return self._away_name.text()
        return self._home_name.text()

    @property
    def losing_abbr(self):
        """
        Returns a ``string`` of the losing team's abbreviation, such as 'LAD'
        for the Los Angeles Dodgers.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._away_name)
        return utils._parse_abbreviation(self._home_name)

    @property
    def away_at_bats(self):
        """
        Returns an ``int`` of the number of at bats the away team had.
        """
        return int(self._away_at_bats)

    @property
    def away_runs(self):
        """
        Returns an ``int`` of the number of runs the away team scored.
        """
        return int(self._away_runs)

    @property
    def away_hits(self):
        """
        Returns an ``int`` of the number of hits the away team had.
        """
        return int(self._away_hits)

    @property
    def away_rbi(self):
        """
        Returns an ``int`` of the number of runs batted in the away team
        registered.
        """
        return int(self._away_rbi)

    @property
    def away_earned_runs(self):
        """
        Returns a ``float`` of the number of runs the away team earned.
        """
        return float(self._away_earned_runs)

    @property
    def away_bases_on_balls(self):
        """
        Returns an ``int`` of the number of bases the away team registerd as a
        result of balls.
        """
        return int(self._away_bases_on_balls)

    @property
    def away_strikeouts(self):
        """
        Returns an ``int`` of the number of times the away team was struck out.
        """
        return int(self._away_strikeouts)

    @property
    def away_plate_appearances(self):
        """
        Returns an ``int`` of the number of plate appearances the away team
        made.
        """
        return int(self._away_plate_appearances)

    @property
    def away_batting_average(self):
        """
        Returns a ``float`` of the batting average for the away team.
        """
        return float(self._away_batting_average)

    @property
    def away_on_base_percentage(self):
        """
        Returns a ``float`` of the percentage of at bats that result in the
        batter getting on base.
        """
        return float(self._away_on_base_percentage)

    @property
    def away_slugging_percentage(self):
        """
        Returns a ``float`` of the slugging percentage for the away team based
        on the number of bases gained per at-bat with bigger plays getting more
        weight.
        """
        return float(self._away_slugging_percentage)

    @property
    def away_on_base_plus(self):
        """
        Returns a ``float`` of the on base percentage plus the slugging
        percentage. Percentage ranges from 0-1.
        """
        return float(self._away_on_base_plus)

    @property
    def away_pitches(self):
        """
        Returns an ``int`` of the number of pitches the away team faced.
        """
        return int(self._away_pitches)

    @property
    def away_strikes(self):
        """
        Returns an ``int`` of the number of times a strike was called against
        the away team.
        """
        return int(self._away_strikes)

    @property
    def away_win_probability_for_offensive_player(self):
        """
        Returns a ``float`` of the overall influence the away team's offense
        had on the outcome of the game where 0.0 denotes no influence and 1.0
        denotes the offense was solely responsible for the outcome.
        """
        return float(self._away_win_probability_for_offensive_player)

    @property
    def away_average_leverage_index(self):
        """
        Returns a ``float`` of the amount of pressure the away team's pitcher
        faced during the game. 1.0 denotes average pressure while numbers less
        than 0 denote lighter pressure.
        """
        return float(self._away_average_leverage_index)

    @property
    def away_win_probability_added(self):
        """
        Returns a ``float`` of the total positive influence the away team's
        offense had on the outcome of the game.
        """
        return float(self._away_win_probability_added)

    @property
    def away_win_probability_subtracted(self):
        """
        Returns a ``float`` of the total negative influence the away team's
        offense had on the outcome of the game.
        """
        return float(self._away_win_probability_subtracted)

    @property
    def away_base_out_runs_added(self):
        """
        Returns a ``float`` of the number of base out runs added by the away
        team.
        """
        return float(self._away_base_out_runs_added)

    @property
    def away_putouts(self):
        """
        Returns an ``int`` of the number of putouts the away team registered.
        """
        return int(self._away_putouts)

    @property
    def away_assists(self):
        """
        Returns an ``int`` of the number of assists the away team registered.
        """
        return int(self._away_assists)

    @property
    def away_innings_pitched(self):
        """
        Returns a ``float`` of the number of innings the away team pitched.
        """
        return float(self._away_innings_pitched)

    @property
    def away_home_runs(self):
        """
        Returns an ``int`` of the number of times the away team gave up a home
        run.
        """
        return int(self._away_home_runs)

    @property
    def away_strikes_by_contact(self):
        """
        Returns an ``int`` of the number of times the away team struck out a
        batter who made contact with the pitch.
        """
        return int(self._away_strikes_by_contact)

    @property
    def away_strikes_swinging(self):
        """
        Returns an ``int`` of the number of times the away team struck out a
        batter who was swinging.
        """
        return int(self._away_strikes_swinging)

    @property
    def away_strikes_looking(self):
        """
        Returns an ``int`` of the number of times the away team struck out a
        batter who was looking.
        """
        return int(self._away_strikes_looking)

    @property
    def away_grounded_balls(self):
        """
        Returns an ``int`` of the number of grounded balls the away team
        allowed.
        """
        return int(self._away_grounded_balls)

    @property
    def away_fly_balls(self):
        """
        Returns an ``int`` of the number of fly balls the away team allowed.
        """
        return int(self._away_fly_balls)

    @property
    def away_line_drives(self):
        """
        Returns an ``int`` of the number of line drives the away team allowed.
        """
        return int(self._away_line_drives)

    @property
    def away_unknown_bat_type(self):
        """
        Returns an ``int`` of the number of away at bats that were not properly
        tracked and therefore cannot be safely placed in another statistical
        category.
        """
        return int(self._away_unknown_bat_type)

    @property
    def away_game_score(self):
        """
        Returns an ``int`` of the starting away pitcher's score determine by
        many factors, such as number of runs scored against, number of strikes,
        etc.
        """
        return int(self._away_game_score)

    @property
    def away_inherited_runners(self):
        """
        Returns an ``int`` of the number of runners a pitcher inherited when he
        entered the game.
        """
        try:
            return int(self._away_inherited_runners)
        except ValueError:
            return 0

    @property
    def away_inherited_score(self):
        """
        Returns an ``int`` of the number of scorers a pitcher inherited when he
        entered the game.
        """
        try:
            return int(self._away_inherited_score)
        except ValueError:
            return 0

    @property
    def away_win_probability_by_pitcher(self):
        """
        Returns a ``float`` of the amount of influence the away pitcher had on
        the game's result with 0.0 denoting zero influence and 1.0 denoting he
        was solely responsible for the team's win.
        """
        return float(self._away_win_probability_by_pitcher)

    @property
    def away_base_out_runs_saved(self):
        """
        Returns a ``float`` of the number of runs saved by the away pitcher
        based on the number of players on bases. 0.0 denotes an average value.
        """
        return float(self._away_base_out_runs_saved)

    @property
    def home_at_bats(self):
        """
        Returns an ``int`` of the number of at bats the home team had.
        """
        return int(self._home_at_bats)

    @property
    def home_runs(self):
        """
        Returns an ``int`` of the number of runs the home team scored.
        """
        return int(self._home_runs)

    @property
    def home_hits(self):
        """
        Returns an ``int`` of the number of hits the home team had.
        """
        return int(self._home_hits)

    @property
    def home_rbi(self):
        """
        Returns an ``int`` of the number of runs batted in the home team
        registered.
        """
        return int(self._home_rbi)

    @property
    def home_earned_runs(self):
        """
        Returns a ``float`` of the number of runs the home team earned.
        """
        return float(self._home_earned_runs)

    @property
    def home_bases_on_balls(self):
        """
        Returns an ``int`` of the number of bases the home team registerd as a
        result of balls.
        """
        return int(self._home_bases_on_balls)

    @property
    def home_strikeouts(self):
        """
        Returns an ``int`` of the number of times the home team was struck out.
        """
        return int(self._home_strikeouts)

    @property
    def home_plate_appearances(self):
        """
        Returns an ``int`` of the number of plate appearances the home team
        made.
        """
        return int(self._home_plate_appearances)

    @property
    def home_batting_average(self):
        """
        Returns a ``float`` of the batting average for the home team.
        """
        return float(self._home_batting_average)

    @property
    def home_on_base_percentage(self):
        """
        Returns a ``float`` of the percentage of at bats that result in the
        batter getting on base.
        """
        return float(self._home_on_base_percentage)

    @property
    def home_slugging_percentage(self):
        """
        Returns a ``float`` of the slugging percentage for the home team based
        on the number of bases gained per at-bat with bigger plays getting more
        weight.
        """
        return float(self._home_slugging_percentage)

    @property
    def home_on_base_plus(self):
        """
        Returns a ``float`` of the on base percentage plus the slugging
        percentage. Percentage ranges from 0-1.
        """
        return float(self._home_on_base_plus)

    @property
    def home_pitches(self):
        """
        Returns an ``int`` of the number of pitches the home team faced.
        """
        return int(self._home_pitches)

    @property
    def home_strikes(self):
        """
        Returns an ``int`` of the number of times a strike was called against
        the home team.
        """
        return int(self._home_strikes)

    @property
    def home_win_probability_for_offensive_player(self):
        """
        Returns a ``float`` of the overall influence the home team's offense
        had on the outcome of the game where 0.0 denotes no influence and 1.0
        denotes the offense was solely responsible for the outcome.
        """
        return float(self._home_win_probability_for_offensive_player)

    @property
    def home_average_leverage_index(self):
        """
        Returns a ``float`` of the amount of pressure the home team's pitcher
        faced during the game. 1.0 denotes average pressure while numbers less
        than 0 denote lighter pressure.
        """
        return float(self._home_average_leverage_index)

    @property
    def home_win_probability_added(self):
        """
        Returns a ``float`` of the total positive influence the home team's
        offense had on the outcome of the game.
        """
        return float(self._home_win_probability_added)

    @property
    def home_win_probability_subtracted(self):
        """
        Returns a ``float`` of the total negative influence the home team's
        offense had on the outcome of the game.
        """
        return float(self._home_win_probability_subtracted)

    @property
    def home_base_out_runs_added(self):
        """
        Returns a ``float`` of the number of base out runs added by the home
        team.
        """
        return float(self._home_base_out_runs_added)

    @property
    def home_putouts(self):
        """
        Returns an ``int`` of the number of putouts the home team registered.
        """
        return int(self._home_putouts)

    @property
    def home_assists(self):
        """
        Returns an ``int`` of the number of assists the home team registered.
        """
        return int(self._home_assists)

    @property
    def home_innings_pitched(self):
        """
        Returns a ``float`` of the number of innings the home team pitched.
        """
        return float(self._home_innings_pitched)

    @property
    def home_home_runs(self):
        """
        Returns an ``int`` of the number of times the home team gave up a home
        run.
        """
        return int(self._home_home_runs)

    @property
    def home_strikes_by_contact(self):
        """
        Returns an ``int`` of the number of times the home team struck out a
        batter who made contact with the pitch.
        """
        return int(self._home_strikes_by_contact)

    @property
    def home_strikes_swinging(self):
        """
        Returns an ``int`` of the number of times the home team struck out a
        batter who was swinging.
        """
        return int(self._home_strikes_swinging)

    @property
    def home_strikes_looking(self):
        """
        Returns an ``int`` of the number of times the home team struck out a
        batter who was looking.
        """
        return int(self._home_strikes_looking)

    @property
    def home_grounded_balls(self):
        """
        Returns an ``int`` of the number of grounded balls the home team
        allowed.
        """
        return int(self._home_grounded_balls)

    @property
    def home_fly_balls(self):
        """
        Returns an ``int`` of the number of fly balls the home team allowed.
        """
        return int(self._home_fly_balls)

    @property
    def home_line_drives(self):
        """
        Returns an ``int`` of the number of line drives the home team allowed.
        """
        return int(self._home_line_drives)

    @property
    def home_unknown_bat_type(self):
        """
        Returns an ``int`` of the number of home at bats that were not properly
        tracked and therefore cannot be safely placed in another statistical
        category.
        """
        return int(self._home_unknown_bat_type)

    @property
    def home_game_score(self):
        """
        Returns an ``int`` of the starting home pitcher's score determine by
        many factors, such as number of runs scored against, number of strikes,
        etc.
        """
        return int(self._home_game_score)

    @property
    def home_inherited_runners(self):
        """
        Returns an ``int`` of the number of runners a pitcher inherited when he
        entered the game.
        """
        try:
            return int(self._home_inherited_runners)
        except ValueError:
            return 0

    @property
    def home_inherited_score(self):
        """
        Returns an ``int`` of the number of scorers a pitcher inherited when he
        entered the game.
        """
        try:
            return int(self._home_inherited_score)
        except ValueError:
            return 0

    @property
    def home_win_probability_by_pitcher(self):
        """
        Returns a ``float`` of the amount of influence the home pitcher had on
        the game's result with 0.0 denoting zero influence and 1.0 denoting he
        was solely responsible for the team's win.
        """
        return float(self._home_win_probability_by_pitcher)

    @property
    def home_base_out_runs_saved(self):
        """
        Returns a ``float`` of the number of runs saved by the home pitcher
        based on the number of players on bases. 0.0 denotes an average value.
        """
        return float(self._home_base_out_runs_saved)


class Boxscores:
    """
    Search for MLB games taking place on a particular day.

    Retrieve a dictionary which contains a list of all games being played on a
    particular day. Output includes a link to the boxscore, and the names and
    abbreviations for both the home teams. If no games are played on a
    particular day, the list will be empty.

    Parameters
    ----------
    date : datetime object
        The date to search for any matches. The month, day, and year are
        required for the search, but time is not factored into the search.
    """
    def __init__(self, date):
        self._boxscores = {'boxscores': []}

        self._find_games(date)

    @property
    def games(self):
        """
        Returns a ``dictionary`` object representing all of the games played on
        the requested day. Dictionary is in the following format::

            {
                'boxscores': [
                    'home_name': Name of the home team, such as 'New York
                                 Yankees' (`str`),
                    'home_abbr': Abbreviation for the home team, such as 'NYY'
                                 (`str`),
                    'away_name': Name of the away team, such as 'Houston
                                 Astros' (`str`),
                    'away_abbr': Abbreviation for the away team, such as 'HOU'
                                 (`str`),
                    'boxscore': String representing the boxscore URI, such as
                                'SLN/SLN201807280' (`str`)},
                    { ... },
                    ...
                ]
            }

        If no games were played during the requested day, the list for
        ['boxscores'] will be empty.
        """
        return self._boxscores

    def _create_url(self, date):
        """
        Build the URL based on the passed datetime object.

        In order to get the proper boxscore page, the URL needs to include the
        requested month, day, and year.

        Parameters
        ----------
        date : datetime object
            The date to search for any matches. The month, day, and year are
            required for the search, but time is not factored into the search.

        Returns
        -------
        string
            Returns a ``string`` of the boxscore URL including the requested
            date.
        """
        return BOXSCORES_URL % (date.year, date.month, date.day)

    def _get_requested_page(self, url):
        """
        Get the requested page.

        Download the requested page given the created URL and return a PyQuery
        object.

        Parameters
        ----------
        url : string
            The URL containing the boxscores to find.

        Returns
        -------
        PyQuery object
            A PyQuery object containing the HTML contents of the requested
            page.
        """
        return pq(url)

    def _get_boxscore_uri(self, url):
        """
        Find the boxscore URI.

        Given the boxscore tag for a game, parse the embedded URI for the
        boxscore.

        Parameters
        ----------
        url : PyQuery object
            A PyQuery object containing the game's boxscore tag which has the
            boxscore URI embedded within it.

        Returns
        -------
        string
            Returns a ``string`` containing the link to the game's boxscore
            page.
        """
        uri = re.sub(r'.*/boxes/', '', str(url))
        uri = re.sub(r'\.shtml.*', '', uri).strip()
        return uri

    def _parse_abbreviation(self, abbr):
        """
        Parse a team's abbreviation.

        Given the team's HTML name tag, parse their abbreviation.

        Parameters
        ----------
        abbr : string
            A string of a team's HTML name tag.

        Returns
        -------
        string
            Returns a ``string`` of the team's abbreviation.
        """
        abbr = re.sub(r'.*/teams/', '', str(abbr))
        abbr = re.sub(r'/.*', '', abbr)
        return abbr

    def _get_name(self, name):
        """
        Find a team's name and abbreviation.

        Given the team's HTML name tag, determine their name, and abbreviation.

        Parameters
        ----------
        name : PyQuery object
            A PyQuery object of a team's HTML name tag in the boxscore.

        Returns
        -------
        tuple
            Returns a tuple containing the name and abbreviation for a team.
            Tuple is in the following order: Team Name, Team Abbreviation.
        """
        team_name = name.text()
        abbr = self._parse_abbreviation(name)
        return team_name, abbr

    def _get_team_names(self, game):
        """
        Find the names and abbreviations for both teams in a game.

        Using the HTML contents in a boxscore, find the name and abbreviation
        for both teams.

        Parameters
        ----------
        game : PyQuery object
            A PyQuery object of a single boxscore containing information about
            both teams.

        Returns
        -------
        tuple
            Returns a tuple containing the names and abbreviations of both
            teams in the following order: Away Name, Away Abbreviation, Home
            Name, Home Abbreviation.
        """
        links = [i for i in game('td a').items()]
        # The away team is the first link in the boxscore
        away = links[0]
        # The home team is the last (3rd) link in the boxscore
        home = links[-1]
        away_name, away_abbr = self._get_name(away)
        home_name, home_abbr = self._get_name(home)
        return away_name, away_abbr, home_name, home_abbr

    def _extract_game_info(self, games):
        """
        Parse game information from all boxscores.

        Find the major game information for all boxscores listed on a
        particular boxscores webpage and return the results in a list.

        Parameters
        ----------
        games : generator
            A generator where each element points to a boxscore on the parsed
            boxscores webpage.

        Returns
        -------
        list
            Returns a ``list`` of dictionaries where each dictionary contains
            the name and abbreviations for both the home and away teams, and a
            link to the game's boxscore.
        """
        all_boxscores = []

        for game in games:
            names = self._get_team_names(game)
            away_name, away_abbr, home_name, home_abbr = names
            boxscore_url = game('td[class="right gamelink"] a')
            boxscore_uri = self._get_boxscore_uri(boxscore_url)
            game_info = {
                'boxscore': boxscore_uri,
                'away_name': away_name,
                'away_abbr': away_abbr,
                'home_name': home_name,
                'home_abbr': home_abbr
            }
            all_boxscores.append(game_info)
        return all_boxscores

    def _find_games(self, date):
        """
        Retrieve all major games played on a given day.

        Builds a URL based on the requested date and downloads the HTML
        contents before parsing any and all games played during that day. Any
        games that are found are added to the boxscores dictionary with
        high-level game information such as the home and away team names and a
        link to the boxscore page.

        Parameters
        ----------
        date : datetime object
            The date to search for any matches. The month, day, and year are
            required for the search, but time is not factored into the search.
        """
        url = self._create_url(date)
        page = self._get_requested_page(url)
        games = page('table[class="teams"]').items()
        boxscores = self._extract_game_info(games)
        self._boxscores = {'boxscores': boxscores}
