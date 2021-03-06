from flexmock import flexmock
from mock import patch, PropertyMock
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.ncaab.boxscore import Boxscore


class MockBoxscore:
    def __init__(self, name):
        self._name = name

    def __call__(self, scheme):
        return self._name


class MockName:
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self._name

    def text(self):
        return self._name.replace('<a>cbb/schools</a>', '')


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class TestNCAABBoxscore:
    @patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        self.boxscore = Boxscore(None)

    def test_away_team_wins(self):
        fake_away_points = PropertyMock(return_value=75)
        fake_home_points = PropertyMock(return_value=70)
        type(self.boxscore)._away_points = fake_away_points
        type(self.boxscore)._home_points = fake_home_points

        assert self.boxscore.winner == AWAY

    def test_home_team_wins(self):
        fake_away_points = PropertyMock(return_value=70)
        fake_home_points = PropertyMock(return_value=75)
        type(self.boxscore)._away_points = fake_away_points
        type(self.boxscore)._home_points = fake_home_points

        assert self.boxscore.winner == HOME

    def test_winning_name_di_is_home(self):
        expected_name = 'Home Name'
        test_name = '<a>cbb/schools</a>Home Name'

        fake_winner = PropertyMock(return_value=HOME)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_non_di_is_home(self):
        expected_name = 'Home Name'
        test_name = 'Home Name'

        fake_winner = PropertyMock(return_value=HOME)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_di_is_away(self):
        expected_name = 'Away Name'
        test_name = '<a>cbb/schools</a>Away Name'

        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_non_di_is_away(self):
        expected_name = 'Away Name'
        test_name = 'Away Name'

        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.winning_name == expected_name

    def test_winning_abbr_di_is_home(self):
        expected_name = 'Home'
        test_name = '<a>cbb/schools</a>HOME'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=HOME)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_non_di_is_home(self):
        expected_name = 'HOME'
        test_name = 'HOME'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=HOME)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_di_is_away(self):
        expected_name = 'AWAY'
        test_name = '<a>cbb/schools</a>AWAY'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_non_di_is_away(self):
        expected_name = 'AWAY'
        test_name = 'AWAY'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.winning_abbr == expected_name

    def test_losing_name_di_is_home(self):
        expected_name = 'Home Name'
        test_name = '<a>cbb/schools</a>Home Name'

        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_non_di_is_home(self):
        expected_name = 'Home Name'
        test_name = 'Home Name'

        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_di_is_away(self):
        expected_name = 'Away Name'
        test_name = '<a>cbb/schools</a>Away Name'

        fake_winner = PropertyMock(return_value=HOME)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_non_di_is_away(self):
        expected_name = 'Away Name'
        test_name = 'Away Name'

        fake_winner = PropertyMock(return_value=HOME)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.losing_name == expected_name

    def test_losing_abbr_di_is_home(self):
        expected_name = 'HOME'
        test_name = '<a>cbb/schools</a>HOME'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_non_di_is_home(self):
        expected_name = 'HOME'
        test_name = 'HOME'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_di_is_away(self):
        expected_name = 'AWAY'
        test_name = '<a>cbb/schools</a>AWAY'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=HOME)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_non_di_is_away(self):
        expected_name = 'AWAY'
        test_name = 'AWAY'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=HOME)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.losing_abbr == expected_name

    def test_invalid_away_record_returns_default_wins(self):
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(self.boxscore)._away_record = fake_record

        assert self.boxscore.away_wins == 0

    def test_invalid_away_record_returns_default_losses(self):
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(self.boxscore)._away_record = fake_record

        assert self.boxscore.away_losses == 0

    def test_invalid_home_record_returns_default_wins(self):
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(self.boxscore)._home_record = fake_record

        assert self.boxscore.home_wins == 0

    def test_invalid_home_record_returns_default_losses(self):
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(self.boxscore)._home_record = fake_record

        assert self.boxscore.home_losses == 0

    def test_invalid_url_returns_none(self):
        result = Boxscore(None)._retrieve_html_page('')

        assert result is None

    def test_parsing_name_for_non_di_school(self):
        name = 'Away name'
        boxscore = MockBoxscore(name)

        result = self.boxscore._parse_name('away_name', boxscore)

        assert result == name

    def test_no_home_free_throw_percentage_returns_default(self):
        fake_percentage = PropertyMock(return_value='')
        type(self.boxscore)._home_free_throw_percentage = fake_percentage

        assert self.boxscore.home_free_throw_percentage == 0.0

    def test_no_away_free_throw_percentage_returns_default(self):
        fake_percentage = PropertyMock(return_value='')
        type(self.boxscore)._away_free_throw_percentage = fake_percentage

        assert self.boxscore.away_free_throw_percentage == 0.0

    def test_empty_boxscore_class_returns_dataframe_of_none(self):
        fake_points = PropertyMock(return_value=None)
        type(self.boxscore)._home_points = fake_points
        type(self.boxscore)._away_points = fake_points

        assert self.boxscore._home_points is None
        assert self.boxscore._away_points is None
        assert self.boxscore.dataframe is None

    def test_away_win_percentage_no_games_played_returns_default(self):
        fake_games = PropertyMock(return_value=0)
        type(self.boxscore).away_wins = fake_games
        type(self.boxscore).away_losses = fake_games

        assert self.boxscore.away_wins == 0
        assert self.boxscore.away_losses == 0
        assert self.boxscore.away_win_percentage == 0.0

    def test_home_win_percentage_no_games_played_returns_default(self):
        fake_games = PropertyMock(return_value=0)
        type(self.boxscore).home_wins = fake_games
        type(self.boxscore).home_losses = fake_games

        assert self.boxscore.home_wins == 0
        assert self.boxscore.home_losses == 0
        assert self.boxscore.home_win_percentage == 0.0
