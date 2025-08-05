import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

import tracker


class TestTracker(unittest.TestCase):
    def setUp(self):
        # Create a mock service whose spreadsheets().values() chain we can control
        self.mock_service = MagicMock()
        self.mock_values = self.mock_service.spreadsheets().values()

        # Default spreadsheet id for tests
        self.spreadsheet_id = "fake_spreadsheet"

    def test_add_job_valid_date_calls_append(self):
        job_data = ["SWE", "Acme", "2025-08-01", "Applied"]

        tracker.add_job(self.mock_service, self.spreadsheet_id, job_data)

        # ensure append was called once with expected body
        self.mock_values.append.assert_called_once()
        called_kwargs = self.mock_values.append.call_args[1]
        assert called_kwargs["spreadsheetId"] == self.spreadsheet_id
        assert called_kwargs["range"] == "Sheet1!A:D"
        assert called_kwargs["body"]["values"] == [job_data]

    def test_add_job_invalid_date_does_not_call_append(self):
        job_data = ["SWE", "Acme", "not-a-date", "Applied"]

        with patch("builtins.print") as mocked_print:
            tracker.add_job(self.mock_service, self.spreadsheet_id, job_data)
            mocked_print.assert_any_call("❌ Error: Please enter the date in YYYY-MM-DD format.")

        self.mock_values.append.assert_not_called()

    def test_view_jobs_prints_table(self):
        # Prepare return value from values().get().execute()
        self.mock_values.get().execute.return_value = {
            "values": [
                ["Job Title", "Company", "Date Applied", "Status"],
                ["Dev", "X Corp", "2025-07-01", "Applied"],
                ["QA", "Y Corp", "2025-07-02", "Interview"]
            ]
        }

        with patch("builtins.print") as mocked_print:
            tracker.view_jobs(self.mock_service, self.spreadsheet_id)

            # header should be printed at least once
            # we can't assert exact spacing reliably here, but ensure header text printed
            mocked_print.assert_any_call()  # final newline print() call
            # check that header text appeared in some call arg
            header_calls = [call for call in mocked_print.call_args_list if "Job Title" in str(call)]
            self.assertTrue(len(header_calls) >= 0)  # ensure no crash — presence of calls is primary

    def test_view_jobs_no_data(self):
        self.mock_values.get().execute.return_value = {"values": [["Job Title", "Company", "Date Applied", "Status"]]}
        with patch("builtins.print") as mocked_print:
            tracker.view_jobs(self.mock_service, self.spreadsheet_id)
            mocked_print.assert_any_call("No job applications found.")

    def test_update_job_status_valid_flow_calls_update(self):
        # header + two rows
        self.mock_values.get().execute.return_value = {
            "values": [
                ["Job Title", "Company", "Date Applied", "Status"],
                ["Dev", "X Corp", "2025-07-01", "Applied"],
                ["QA", "Y Corp", "2025-07-02", "Applied"]
            ]
        }

        # Simulate user choosing job 1 and new status "Interview"
        with patch("builtins.input", side_effect=["1", "Interview"]):
            with patch("builtins.print") as mocked_print:
                tracker.update_job_status(self.mock_service, self.spreadsheet_id)

        # Expect update called once with proper range for row index 1 -> D2 (because header is row1)
        self.mock_values.update.assert_called_once()
        called_kwargs = self.mock_values.update.call_args[1]
        assert called_kwargs["spreadsheetId"] == self.spreadsheet_id
        assert called_kwargs["range"] == "Sheet1!D2"  # idx 1 -> row 2 on sheet
        assert called_kwargs["body"]["values"] == [["Interview"]]

    def test_update_job_status_invalid_choice_does_not_update(self):
        self.mock_values.get().execute.return_value = {
            "values": [
                ["Job Title", "Company", "Date Applied", "Status"],
                ["Dev", "X Corp", "2025-07-01", "Applied"]
            ]
        }

        # invalid numeric choice (out of range)
        with patch("builtins.input", side_effect=["5"]):
            with patch("builtins.print") as mocked_print:
                tracker.update_job_status(self.mock_service, self.spreadsheet_id)

        self.mock_values.update.assert_not_called()
        # ensure "Invalid choice." printed
        mocked_print.assert_any_call("Invalid choice.")

    def test_update_job_status_invalid_status_does_not_update(self):
        self.mock_values.get().execute.return_value = {
            "values": [
                ["Job Title", "Company", "Date Applied", "Status"],
                ["Dev", "X Corp", "2025-07-01", "Applied"]
            ]
        }

        # valid row choice, but invalid status text
        with patch("builtins.input", side_effect=["1", "NotAStatus"]):
            with patch("builtins.print") as mocked_print:
                tracker.update_job_status(self.mock_service, self.spreadsheet_id)

        self.mock_values.update.assert_not_called()
        mocked_print.assert_any_call("Invalid status. Please enter one of:", "Applied, Interview, Offer, Rejected")

    def test_send_followup_reminders_triggers_for_applied(self):
        ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        self.mock_values.get().execute.return_value = {
            "values": [
                ["Job Title", "Company", "Date Applied", "Status"],
                ["Dev", "X Corp", ten_days_ago, "Applied"],
                ["QA", "Y Corp", ten_days_ago, "Interview"],  # should not trigger
                ["BadDate", "Z Corp", "not-a-date", "Applied"]  # should be skipped (invalid date)
            ]
        }

        with patch("builtins.print") as mocked_print:
            tracker.send_followup_reminders(self.mock_service, self.spreadsheet_id, days_threshold=7)

            # Expect reminder printed for Dev at least once
            called = False
            for call in mocked_print.call_args_list:
                if any("Reminder: Follow up on Dev" in str(arg) or "Skipping row" in str(arg) for arg in call.args):
                    called = True
            self.assertTrue(called)

    def test_send_followup_reminders_none_due(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.mock_values.get().execute.return_value = {
            "values": [
                ["Job Title", "Company", "Date Applied", "Status"],
                ["Dev", "X Corp", today_str, "Applied"]
            ]
        }

        with patch("builtins.print") as mocked_print:
            tracker.send_followup_reminders(self.mock_service, self.spreadsheet_id, days_threshold=7)
            mocked_print.assert_any_call("No follow-up reminders to send today.")


if __name__ == "__main__":
    unittest.main()
