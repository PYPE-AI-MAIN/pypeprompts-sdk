import pytest
import asyncio
import os
from dotenv import load_dotenv
from pypeprompts import PromptAnalyticsTracker, PromptAnalyticsError

# Load environment variables
load_dotenv()

# PROJECT_TOKEN = os.getenv("PROJECT_TOKEN")
PROJECT_TOKEN = "aa534570d07fd3f99885f698097a3ede1b9b2fac3059d2c936a6f79d279e9e00"
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:3000/api/analytics")


@pytest.fixture
def tracker():
    print("Project Token:", PROJECT_TOKEN)
    return PromptAnalyticsTracker(project_token=PROJECT_TOKEN, enabled=True)


def test_tracker_initialization(tracker):
    assert tracker.project_token == PROJECT_TOKEN
    assert tracker.enabled == True
    assert tracker.dashboard_url == DASHBOARD_URL


def test_tracker_initialization_error():
    with pytest.raises(PromptAnalyticsError, match="project_token is required"):
        PromptAnalyticsTracker(project_token="")


def test_sync_tracking(tracker):
    input_msg = """

    {https://storage.googleapis.com/data-scaling/without-rag-final-wireframe/input/Image%2012-without-rag-basic-prompt.jpg +

You are a critic UX Designer and Product Designer. Based on the image of a UI screen and your task is to analyze the screen image and give a primary purpose, user actions and info display about the UI screen. The information should include the primary purpose of the screen, user actions that can be performed on the screen, and specific information that should be displayed on the screen in a visual order.

You will get this from the user: Image of UI screen

Output Requirements:

Based on the above context, generate the following details about the given screen: Primary Purpose: What is the main purpose of this screen? User Actions: What actions should users be able to perform on this screen? (Write this in order to elements in screen) Information Display: What specific information should be displayed on this screen? (Write this in order with user actions)

You can have more than three User Actions and Information Display if required; Create a list by completely analysing the screen.

IMPORTANT: You can use exact phrases and text from the image screen to describe User Actions and Information Display but add them like an example, keep the description generalised to the explain what user can do on these type of screens. Example: Do not output "Tabs to switch between 'Work' and 'About' sections", instead you must output: "Tabs to switch between sections".

Provide the output in the following <JSON> format:

{ "primaryPurpose": "Brief description of the main purpose of the screen", "userActions": [ "Action 1", "Action 2", "Action 3" ], "informationDisplay": [ "Information 1", "Information 2", "Information 3" ] }

Example Context:

Example Input for a UI Image of Settings & Preferences screen of a Shopping app with image

Example Output :

{ "primaryPurpose": "Provide users an interface to manage their account and app settings within a shopping application.", "userActions": [ "Navigate back to the previous screen", "Navigate to different settings categories", "View and Modify Settings", "Log out of the app" ], "informationDisplay": [ "User profile details", "Payment settings", "Communication preferences", "In-store offer settings", "Login settings", "Legal information", "Log Out Option" ] }

Use the provided context and examples to generate a relevant and detailed response for the specified Image of the UI screen.}
"""
    # input_msg = """

    # - You are a highly skilled UI Designer, you know how to structure information, order components, what components are useful and can create in good user experiences.
    # - You are tasked with creating a UI design that fulfills a specific screen objective.
    # - To achieve this, you must analyze the provided screen objective,
    #   and then select and order the appropriate UI components to construct the final UI screen such that it best conveys the necessary information.
    # - With Components you will also be provided with their type, analyse them carefully and according to instructions below answer the query

    # Available UI Components:
    #     ['Padding-Spacing', 'Padding-Overlay', 'Buttons-Button', 'Buttons-Button with text', 'Buttons-Floating Button', 'Buttons-Social button', 'Buttons-Stepper', 'Pagination-circles', 'Pagination-page number', 'Pagination-With button', 'Categories-Rounded', 'Categories-Landscape', 'Categories-Tall', 'Categories-Badge', 'Text sections-Body', 'Text sections-Title', 'Input field-Card input', 'Input field-Text input', 'Input field-Phone input', 'Carousel-Landscape', 'Carousel-Square', 'Carousel-Tall', 'Search-Default', 'Search-With button', 'Ecommerce cards-Coupon', 'Ecommerce cards-Checkout card', 'Ecommerce cards-Product card', 'Food Delivery cards-Coupon', 'Food Delivery cards-Checkout card', 'Food Delivery cards-Grocery card', 'Food Delivery cards-Storefront', 'Food Delivery cards-Product card', 'Social media cards-Default', 'Social media cards-Thread', 'Social media cards-Stories', 'Social media cards-Blog card', 'Social media cards-Profile card', 'Travel and booking-Real estate card', 'Travel and booking-Flight booking card', 'Review card-Default', 'Status bars-Popup bar', 'Status bars-Top bar', 'Status bars-Bottom bar', 'Bottom navigation bar-Default', 'Tab menu-Line indicator', 'Tab menu-Badge', 'Segmented menu-Default', 'Top navigation bar-Text only', 'Top navigation bar-Centered', 'Top navigation bar-Left aligned', 'Accordian & collapsible-Default', 'Seperator-Default', 'Seperator-Title', 'text and messaging-Text-left', 'text and messaging-Voice-right', 'text and messaging-Text-right', 'text and messaging-chat input field', 'text and messaging-Voice-left', 'Notification-Snack bar', 'Notification-Toast', 'Calendar-Calendar', 'Calendar-Event item', 'Video cards-thumbnail', 'Video cards-Scrollable video', 'Video cards-Video player', 'Progress-Progress bar', 'Progress-Steps', 'Progress-Slider', 'Helper elements-QR code', 'Helper elements-Overlay background', 'Helper elements-Over lay bar', 'List-Button', 'List-Radio button', 'List-Switch', 'List-Check box', 'List-Image landscape', 'List-Avatar', 'List-Text', 'List-Icon only', 'Pricing and paywall-Table', 'Pricing and paywall-Checkbox', 'Pricing and paywall-paywall', 'map-Default']

    # You can only choose components from the above list, give your output strictly in below list format

    # For example :
    # [
    # "Status bars-Top bar"
    # "Top navigation bar-Text only"
    # ]

    # Important Considerations:

    # - Prioritize analyzing the screen objective.
    # - Ensure the selected components and their order align with the primary goal of fulfilling the screen objective.
    # - **Utilize all available UI components** to ensure a comprehensive and innovative approach to fulfilling the screen objective.
    # - Be meticulous in the selection and ordering to create a cohesive and functional UI design.

    # Use the given considerations, analysis, and available UI components to deliver a well-structured and objective-focused UI screen design in the specified format.
    #  + {'primaryPurpose': 'To collect basic user health details for personalization and relevant information delivery within a health app.', 'userActions': ['Navigate back to the previous screen', 'Input first name', 'Input last name', 'Input date of birth', 'Select Sex', 'Input height', 'Input weight', 'Proceed to the next screen'], 'informationDisplay': ['Screen title: Set up Health Details', 'Explanation: brief on why the app requires this information', 'First name input field', 'Last name input field', 'Date of birth input field', 'Sex selection field', 'Height input field', 'Weight input field', 'Next button']}
    #         """

    messages = [
        {input_msg},
    ]

    response_content = """
    {
  "response": [
    {
      "component_type": "markdown",
      "data": "### Test Automation Plan Example\n\nIn this exercise, you will create a basic structure of a test automation plan using Python. Imagine you are working on a project where you need to automate the testing of a web application. Your task is to outline the key components of the test automation plan in code.\n\n**Key Components to Include:**\n1. **Objectives**: Define the goals of your test automation.\n2. **Scope**: Specify what will be automated and what will not.\n3. **Timeline**: Outline the schedule for the automation tasks.\n4. **Tools**: List the tools and technologies you will use.\n5. **Resources**: Identify the team members and their roles.\n\nUse the following template to get started:"
    },
    {
      "component_type": "code_editor",
      "url":"https://pypeai.com/",
      "data": {
        "question": "Create a basic structure of a test automation plan in Python. Include objectives, scope, timeline, tools, and resources.",
        "language": "python",
        "default": "class TestAutomationPlan:\n    def __init__(self):\n        self.objectives = []\n        self.scope = []\n        self.timeline = {}\n        self.tools = []\n        self.resources = {}\n\n    def add_objective(self, objective):\n        self.objectives.append(objective)\n\n    def add_scope(self, item):\n        self.scope.append(item)\n\n    def set_timeline(self, phase, duration):\n        self.timeline[phase] = duration\n\n    def add_tool(self, tool):\n        self.tools.append(tool)\n\n    def add_resource(self, role, person):\n        self.resources[role] = person\n\n# Example usage\nplan = TestAutomationPlan()\nplan.add_objective('Increase test coverage')\nplan.add_scope('Automate login tests')\nplan.set_timeline('Phase 1', '2 weeks')\nplan.add_tool('Selenium')\nplan.add_resource('QA Engineer', 'John Doe')\nprint(plan.objectives)\nprint(plan.scope)\nprint(plan.timeline)\nprint(plan.tools)\nprint(plan.resources)",
        "output": "['Increase test coverage']\n['Automate login tests']\n{'Phase 1': '2 weeks'}\n['Selenium']\n{'QA Engineer': 'John Doe'}"
      }
    },
    {
      "component_type": "markdown",
      "data": "📺 **Resource:** [Showcasing Projects in Selenium Automation Testing Interviews](https://www.youtube.com/watch?v=x9vAgJSq2O0)\n\n**Relevant Timestamps:**\n- 00:00 - Introduction\n- 02:15 - Importance of Understanding the Framework\n- 05:30 - Presenting Your Experience Effectively\n- 08:45 - Tools and Technologies\n\nThis video will help you understand how to present your test automation plan and experience effectively during interviews."
    }
  ]
}
    """

    workflow_name = "preplaced"
    properties = {
        "prompt": str(messages),
        "output": response_content,
        "processingTime": 0.5,
        "functionName": "Slide Creation",
        "tags": ["new"],
        "attributes": {
            "user_category_12": "www.pypeai.com",
            "experience_12": "0",
            "goal": ["Graduated, www.pypeai.com"],
            "targetCompanies": ["Consultation Firms"],
            "targetDomains": ["Frontend Developer", "Backend"],
        },
    }

    try:
        id = tracker.track(workflow_name, properties)
        print("Prompt Id:", id)
        # If no exception is raised, the test passes
        assert True
    except PromptAnalyticsError as e:
        print(f"Detailed error: {str(e)}")
        pytest.fail(f"Failed to send analytics data: {str(e)}")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
