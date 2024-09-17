import unittest
from unittest.mock import patch, MagicMock
from pypeprompts import PromptAnalyticsTracker


class TestPromptAnalyticsTracker(unittest.TestCase):

    @patch("requests.post")
    def test_track_without_sending_data(self, mock_post):
        # Set up the mock to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_post.return_value = mock_response

        # Initialize the tracker with a fake project token
        tracker = PromptAnalyticsTracker(project_token="fake-project-token")

        # Prepare test data
        workflow_name = "test_workflow"
        properties = {
            "prompt": "Test prompt",
            "output": "Test output",
            "processingTime": 0.5,
            "tags": ["test"],
            "attributes": {"test_key": "test_value"},
        }

        # Call the track method
        prompt_id = tracker.track(workflow_name, properties)

        # Assert that a prompt_id was returned (it should be a UUID string)
        self.assertIsInstance(prompt_id, str)

        # Assert that requests.post was called once
        mock_post.assert_called_once()

        # Check that the correct URL and headers were used
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], tracker.dashboard_url)
        self.assertEqual(
            kwargs["headers"]["Authorization"], f"Bearer {tracker.project_token}"
        )

        # Check that the sent data contains the expected fields
        sent_data = kwargs["json"]
        self.assertEqual(sent_data["name"], workflow_name)
        self.assertEqual(sent_data["input"], properties["prompt"])
        self.assertEqual(sent_data["output"], properties["output"])
        self.assertEqual(sent_data["processingTime"], properties["processingTime"])
        self.assertEqual(sent_data["tags"], properties["tags"])
        self.assertEqual(sent_data["attributes"], properties["attributes"])

        print("Tracking test completed without sending actual data.")


if __name__ == "__main__":
    unittest.main()
