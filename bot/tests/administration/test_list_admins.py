from datetime import date

import pytest

from bot.database.models import UserProfile
import bot.responses.administration.list_admins_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestListAdminsCommand(BaseTest):

    @pytest.mark.quick
    def test_list_admins_with_admins(self):
        admins = [
            UserProfile(
                user_id=2015344951, username="admin", full_name="Admin User", subscription_end=date.today(),
                note=None,
            ),
        ]
        self.expect_command_result_contains('/listadmins', [msg.format_admins_list(admins)])
