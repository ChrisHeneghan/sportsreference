import pandas as pd
import re
from pyquery import PyQuery as pq
from .. import utils
from .constants import (BOXSCORE_ELEMENT_INDEX,
                        BOXSCORE_SCHEME,
                        BOXSCORE_URL,
                        BOXSCORES_URL)
from sportsreference import utils
from sportsreference.constants import AWAY, HOME


class Boxscore(object):
    """
    Detailed information about the final statistics for a game.

    Stores all relevant information for a game such as the date, time,
    location, result, and more advanced metrics such as the number of fumbles
    from sacks, a team's passing completion, rushing touchdowns and much more.

    Parameters
    ----------
    uri : string
        The relative link to the boxscore HTML page, such as
        '2018-01-08-georgia'.
    """
    def __init__(self, uri):
        self._uri = uri
        self._date = None
        self._time = None
        self._stadium = None
        self._away_name = None
        self._home_name = None
        self._winner = None
        self._winning_name = None
        self._winning_abbr = None
        self._losing_name = None
        self._losing_abbr = None
        self._away_points = None
        self._away_first_downs = None
        self._away_rush_attempts = None
        self._away_rush_yards = None
        self._away_rush_touchdowns = None
        self._away_pass_completions = None
        self._away_pass_attempts = None
        self._away_pass_yards = None
        self._away_pass_touchdowns = None
        self._away_interceptions = None
        self._away_total_yards = None
        self._away_fumbles = None
        self._away_fumbles_lost = None
        self._away_turnovers = None
        self._away_penalties = None
        self._away_yards_from_penalties = None
        self._home_points = None
        self._home_first_downs = None
        self._home_rush_attempts = None
        self._home_rush_yards = None
        self._home_rush_touchdowns = None
        self._home_pass_completions = None
        self._home_pass_attempts = None
        self._home_pass_yards = None
        self._home_pass_touchdowns = None
        self._home_interceptions = None
        self._home_total_yards = None
        self._home_fumbles = None
        self._home_fumbles_lost = None
        self._home_turnovers = None
        self._home_penalties = None
        self._home_yards_from_penalties = None

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
            '2018-01-08-georgia'.

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
        game_info = items[0].split('\n')
        index = BOXSCORE_ELEMENT_INDEX[field]
        # If the game is a bowl game or a championship game, it will have a
        # different layout for the game information where the specific game
        # title, such as the name of the bowl game, will be the first line of
        # text. All other matchers should have the index matcher increased by
        # 1.
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                    'saturday', 'sunday']:
            # The day info is generally the first line in text for non-special
            # games.
            if day in game_info[0].lower():
                if index >= len(game_info):
                    return ''
                if 'sports logos.net' in game_info[index].lower() or \
                   game_info[index] == '':
                    return ''
                return game_info[index]
        index += 1
        if index >= len(game_info):
            return ''
        if 'sports logos.net' in game_info[index].lower() or \
           game_info[index] == '':
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
            '2018-01-08-georgia'.
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
               short_field == 'stadium':
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
        instantiate the class, such as '2018-01-08-georgia'.
        """
        if self._away_points is None and self._home_points is None:
            return None
        fields_to_include = {
            'away_first_downs': self.away_first_downs,
            'away_fumbles': self.away_fumbles,
            'away_fumbles_lost': self.away_fumbles_lost,
            'away_interceptions': self.away_interceptions,
            'away_pass_attempts': self.away_pass_attempts,
            'away_pass_completions': self.away_pass_completions,
            'away_pass_touchdowns': self.away_pass_touchdowns,
            'away_pass_yards': self.away_pass_yards,
            'away_penalties': self.away_penalties,
            'away_points': self.away_points,
            'away_rush_attempts': self.away_rush_attempts,
            'away_rush_touchdowns': self.away_rush_touchdowns,
            'away_rush_yards': self.away_rush_yards,
            'away_total_yards': self.away_total_yards,
            'away_turnovers': self.away_turnovers,
            'away_yards_from_penalties': self.away_yards_from_penalties,
            'date': self.date,
            'home_first_downs': self.home_first_downs,
            'home_fumbles': self.home_fumbles,
            'home_fumbles_lost': self.home_fumbles_lost,
            'home_interceptions': self.home_interceptions,
            'home_pass_attempts': self.home_pass_attempts,
            'home_pass_completions': self.home_pass_completions,
            'home_pass_touchdowns': self.home_pass_touchdowns,
            'home_pass_yards': self.home_pass_yards,
            'home_penalties': self.home_penalties,
            'home_points': self.home_points,
            'home_rush_attempts': self.home_rush_attempts,
            'home_rush_touchdowns': self.home_rush_touchdowns,
            'home_rush_yards': self.home_rush_yards,
            'home_total_yards': self.home_total_yards,
            'home_turnovers': self.home_turnovers,
            'home_yards_from_penalties': self.home_yards_from_penalties,
            'losing_abbr': self.losing_abbr,
            'losing_name': self.losing_name,
            'stadium': self.stadium,
            'time': self.time,
            'winner': self.winner,
            'winning_abbr': self.winning_abbr,
            'winning_name': self.winning_name
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
    def stadium(self):
        """
        Returns a ``string`` of the name of the stadium where the game was
        played.
        """
        return self._stadium.replace('Stadium: ', '')

    @property
    def winner(self):
        """
        Returns a ``string`` constant indicating whether the home or away team
        won.
        """
        if self.home_points > self.away_points:
            return HOME
        return AWAY

    @property
    def winning_name(self):
        """
        Returns a ``string`` of the winning team's name, such as 'Alabama'.
        """
        if self.winner == HOME:
            return self._home_name.text()
        return self._away_name.text()

    @property
    def winning_abbr(self):
        """
        Returns a ``string`` of the winning team's abbreviation, such as
        'ALABAMA'
        for the Alabama Crimson Tide.
        """
        if self.winner == HOME:
            if 'cfb/schools' not in str(self._home_name):
                return self._home_name.text()
            return utils._parse_abbreviation(self._home_name)
        if 'cfb/schools' not in str(self._away_name):
            return self._away_name.text()
        return utils._parse_abbreviation(self._away_name)

    @property
    def losing_name(self):
        """
        Returns a ``string`` of the losing team's name, such as 'Georgia'.
        """
        if self.winner == HOME:
            return self._away_name.text()
        return self._home_name.text()

    @property
    def losing_abbr(self):
        """
        Returns a ``string`` of the losing team's abbreviation, such as
        'GEORGIA' for the Georgia Bulldogs.
        """
        if self.winner == HOME:
            if 'cfb/schools' not in str(self._away_name):
                return self._away_name.text()
            return utils._parse_abbreviation(self._away_name)
        if 'cfb/schools' not in str(self._home_name):
            return self._home_name.text()
        return utils._parse_abbreviation(self._home_name)

    @property
    def away_points(self):
        """
        Returns an ``int`` of the number of points the away team scored.
        """
        return int(self._away_points)

    @property
    def away_first_downs(self):
        """
        Returns an ``int`` of the number of first downs the away team gained.
        """
        return int(self._away_first_downs)

    @property
    def away_rush_attempts(self):
        """
        Returns an ``int`` of the number of rushing plays the away team made.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._away_rush_attempts.replace('--', '-').split('-')
        return int(rush_info[0])

    @property
    def away_rush_yards(self):
        """
        Returns an ``int`` of the number of rushing yards the away team gained.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._away_rush_yards.replace('--', '-').split('-')
        return int(rush_info[1])

    @property
    def away_rush_touchdowns(self):
        """
        Returns an ``int`` of the number of rushing touchdowns the away team
        scored.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._away_rush_touchdowns.replace('--', '-').split('-')
        return int(rush_info[2])

    @property
    def away_pass_completions(self):
        """
        Returns an ``int`` of the number of completed passes the away team
        made.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._away_pass_completions.replace('--', '-').split('-')
        return int(pass_info[0])

    @property
    def away_pass_attempts(self):
        """
        Returns an ``int`` of the number of passes that were thrown by the away
        team.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._away_pass_attempts.replace('--', '-').split('-')
        return int(pass_info[1])

    @property
    def away_pass_yards(self):
        """
        Returns an ``int`` of the number of passing yards the away team gained.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._away_pass_yards.replace('--', '-').split('-')
        return int(pass_info[2])

    @property
    def away_pass_touchdowns(self):
        """
        Returns an ``int`` of the number of passing touchdowns the away team
        scored.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._away_pass_touchdowns.replace('--', '-').split('-')
        return int(pass_info[3])

    @property
    def away_interceptions(self):
        """
        Returns an ``int`` of the number of interceptions the away team threw.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._away_interceptions.replace('--', '-').split('-')
        return int(pass_info[4])

    @property
    def away_total_yards(self):
        """
        Returns an ``int`` of the total number of yards the away team gained.
        """
        return int(self._away_total_yards)

    @property
    def away_fumbles(self):
        """
        Returns an ``int`` of the number of times the away team fumbled the
        ball.
        """
        # Fumble info is in the format 'Fumbles-Lost'
        fumble_info = self._away_fumbles.replace('--', '-').split('-')
        return int(fumble_info[0])

    @property
    def away_fumbles_lost(self):
        """
        Returns an ``int`` of the number of times the away team turned the ball
        over as the result of a fumble.
        """
        # Fumble info is in the format 'Fumbles-Lost'
        fumble_info = self._away_fumbles.replace('--', '-').split('-')
        return int(fumble_info[1])

    @property
    def away_turnovers(self):
        """
        Returns an ``int`` of the number of times the away team turned the ball
        over.
        """
        return int(self._away_turnovers)

    @property
    def away_penalties(self):
        """
        Returns an ``int`` of the number of penalties called on the away team.
        """
        # Penalties info is in the format 'Penalties-Yards'
        penalties_info = self._away_penalties.replace('--', '-').split('-')
        return int(penalties_info[0])

    @property
    def away_yards_from_penalties(self):
        """
        Returns an ``int`` of the number of yards gifted as a result of
        penalties called on the away team.
        """
        # Penalties info is in the format 'Penalties-Yards'
        penalties_info = self._away_yards_from_penalties.replace('--', '-')
        penalties_info = penalties_info.split('-')
        return int(penalties_info[1])

    @property
    def home_points(self):
        """
        Returns an ``int`` of the number of points the home team scored.
        """
        return int(self._home_points)

    @property
    def home_first_downs(self):
        """
        Returns an ``int`` of the number of first downs the home team gained.
        """
        return int(self._home_first_downs)

    @property
    def home_rush_attempts(self):
        """
        Returns an ``int`` of the number of rushing plays the home team made.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._home_rush_attempts.replace('--', '-').split('-')
        return int(rush_info[0])

    @property
    def home_rush_yards(self):
        """
        Returns an ``int`` of the number of rushing yards the home team gained.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._home_rush_yards.replace('--', '-').split('-')
        return int(rush_info[1])

    @property
    def home_rush_touchdowns(self):
        """
        Returns an ``int`` of the number of rushing touchdowns the home team
        scored.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._home_rush_touchdowns.replace('--', '-').split('-')
        return int(rush_info[2])

    @property
    def home_pass_completions(self):
        """
        Returns an ``int`` of the number of completed passes the home team
        made.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._home_pass_completions.replace('--', '-').split('-')
        return int(pass_info[0])

    @property
    def home_pass_attempts(self):
        """
        Returns an ``int`` of the number of passes that were thrown by the home
        team.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._home_pass_attempts.replace('--', '-').split('-')
        return int(pass_info[1])

    @property
    def home_pass_yards(self):
        """
        Returns an ``int`` of the number of passing yards the home team gained.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._home_pass_yards.replace('--', '-').split('-')
        return int(pass_info[2])

    @property
    def home_pass_touchdowns(self):
        """
        Returns an ``int`` of the number of passing touchdowns the home team
        scored.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._home_pass_touchdowns.replace('--', '-').split('-')
        return int(pass_info[3])

    @property
    def home_interceptions(self):
        """
        Returns an ``int`` of the number of interceptions the home team threw.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._home_pass_touchdowns.replace('--', '-').split('-')
        return int(pass_info[4])

    @property
    def home_total_yards(self):
        """
        Returns an ``int`` of the total number of yards the home team gained.
        """
        return int(self._home_total_yards)

    @property
    def home_fumbles(self):
        """
        Returns an ``int`` of the number of times the home team fumbled the
        ball.
        """
        # Fumble info is in the format 'Fumbles-Lost'
        fumble_info = self._home_fumbles.replace('--', '-').split('-')
        return int(fumble_info[0])

    @property
    def home_fumbles_lost(self):
        """
        Returns an ``int`` of the number of times the home team turned the ball
        over as the result of a fumble.
        """
        # Fumble info is in the format 'Fumbles-Lost'
        fumble_info = self._home_fumbles_lost.replace('--', '-').split('-')
        return int(fumble_info[1])

    @property
    def home_turnovers(self):
        """
        Returns an ``int`` of the number of times the home team turned the ball
        over.
        """
        return int(self._home_turnovers)

    @property
    def home_penalties(self):
        """
        Returns an ``int`` of the number of penalties called on the home team.
        """
        # Penalties info is in the format 'Penalties-Yards'
        penalties_info = self._home_penalties.replace('--', '-').split('-')
        return int(penalties_info[0])

    @property
    def home_yards_from_penalties(self):
        """
        Returns an ``int`` of the number of yards gifted as a result of
        penalties called on the home team.
        """
        # Penalties info is in the format 'Penalties-Yards'
        penalties_info = self._home_yards_from_penalties.replace('--', '-')
        penalties_info = penalties_info.split('-')
        return int(penalties_info[1])


class Boxscores:
    """
    Search for NCAAF games taking place on a particular day.

    Retrieve a dictionary which contains a list of all games being played on a
    particular day. Output includes a link to the boxscore, a boolean value
    which indicates if the game is between two Division-I teams or not, and the
    names and abbreviations for both the home teams. If no games are played on
    a particular day, the list will be empty.

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

            {'boxscores' : [
                {'home_name': Name of the home team, such as 'Purdue
                              Boilermakers' (`str`),
                 'home_abbr': Abbreviation for the home team, such as
                              'PURDUE' (`str`),
                 'away_name': Name of the away team, such as 'Indiana
                              Hoosiers' (`str`),
                 'away_abbr': Abbreviation for the away team, such as
                              'INDIANA' (`str`),
                 'boxscore': String representing the boxscore URI, such as
                             '2017-09-09-michigan' (`str`),
                 'non_di': Boolean value which evaluates to True when at least
                           one of the teams does not compete in NCAA
                           Division-I football (`str`)},
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
        return BOXSCORES_URL % (date.month, date.day, date.year)

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
        uri = re.sub(r'.*cfb/boxscores/', '', str(url))
        uri = re.sub(r'\.html.*', '', uri).strip()
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
        if 'cfb/schools' not in str(abbr):
            return None
        abbr = re.sub(r'.*/schools/', '', str(abbr))
        abbr = re.sub(r'/.*', '', abbr)
        return abbr

    def _get_name(self, name):
        """
        Find a team's name and abbreviation.

        Given the team's HTML name tag, determine their name, abbreviation, and
        whether or not they compete in Division-I.

        Parameters
        ----------
        name : PyQuery object
            A PyQuery object of a team's HTML name tag in the boxscore.

        Returns
        -------
        tuple
            Returns a tuple containing the name, abbreviation, and whether or
            not the team participates in Division-I. Tuple is in the following
            order: Team Name, Team Abbreviation, boolean which evaluates to
            True if the team does not participate in Division-I.
        """
        team_name = name.text()
        abbr = self._parse_abbreviation(name)
        non_di = False
        if not abbr:
            abbr = team_name
            non_di = True
        return team_name, abbr, non_di

    def _get_team_names(self, game):
        """
        Find the names and abbreviations for both teams in a game.

        Using the HTML contents in a boxscore, find the name and abbreviation
        for both teams and determine wether or not this is a matchup between
        two Division-I teams.

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
            Name, Home Abbreviation, and a boolean which evaluates to True if
            either team does not participate in Division-I athletics.
        """
        links = [i for i in game('td a').items()]
        # The away team is the first link in the boxscore
        away = links[0]
        # The home team is the last (3rd) link in the boxscore
        home = links[-1]
        non_di = False
        away_name, away_abbr, away_non_di = self._get_name(away)
        home_name, home_abbr, home_non_di = self._get_name(home)
        non_di = away_non_di or home_non_di
        return away_name, away_abbr, home_name, home_abbr, non_di

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
            the name and abbreviations for both the home and away teams, a
            boolean value indicating whether or not both teams compete in
            Division-I, and a link to the boxscore.
        """
        all_boxscores = []

        for game in games:
            names = self._get_team_names(game)
            away_name, away_abbr, home_name, home_abbr, non_di = names
            boxscore_url = game('td[class="right gamelink"] a')
            boxscore_uri = self._get_boxscore_uri(boxscore_url)
            game_info = {
                'boxscore': boxscore_uri,
                'away_name': away_name,
                'away_abbr': away_abbr,
                'home_name': home_name,
                'home_abbr': home_abbr,
                'non_di': non_di
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
