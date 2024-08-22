import pytest
import asyncio
import os
from dotenv import load_dotenv
from pypeprompts import PromptAnalyticsTracker, PromptAnalyticsError
import aiohttp
import json

# Load environment variables
load_dotenv()

PROJECT_TOKEN = os.getenv("PROJECT_TOKEN")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:3000/api/analytics")


@pytest.fixture
def tracker():
    return PromptAnalyticsTracker(project_token=PROJECT_TOKEN, enabled=True)


def test_tracker_initialization(tracker):
    assert tracker.project_token == PROJECT_TOKEN
    assert tracker.enabled == True
    assert tracker.dashboard_url == DASHBOARD_URL


def test_tracker_initialization_error():
    with pytest.raises(PromptAnalyticsError, match="project_token is required"):
        PromptAnalyticsTracker(project_token="")


def test_sync_tracking(tracker):
    messages = [
        {
            "role": "system",
            "content": """You are an AI expert personal curriculum Designer at Preplaced, an AI Learning and Mentorship Platform.
    You create the most optimized and fastest personal Learning Paths/Roadmaps for users based on data they provide Target domains,
    Goals,target companies, current user category,current skill level, and their estimated possible effort in terms of time from their side.

    ### Instructions to follow

    User will provide following data:

    1. user_info: This contains information regarding the user, whether they are college students(fresher) or working professionals and the years of industry experience they have.
    2. users_goals: This contains the user's main goal, roles user is targeting, the companies in which user is looking to apply to, the timeline they have in mind to prepare for these roles
    3. Today's Date: This is used as a reference point to start the roadmap.
    4. current_skill_level: The current skill level of the user in few of the skills required for the role.
    5. Time user can commit to on the roadmap in a week: the time user can dedicate every week to follow the roadmap

    Use these following data to complete your roadmap creation task.
    1. skills_array: S1 - Cross-Browser Development
    S2 - System Design
    S3 - JavaScript
    S4 - DSA
    S5 - Performance Optimization
    S6 - React
    : This is the set of skills needed for the roles user is targeting and wants to prepare for.
    2. focus_areas: f1 - Get Familiar with New Domain
    f2 - Master Skills to be Interview Ready
    f3 - Build a Competitive Profile
    f4 - To be Skipped
    3. topics_array: {'skill': 'Cross-Browser Development', 'topics': ['Browser Compatibility Testing', 'CSS Prefixes and Fallbacks', 'JavaScript Transpilation', 'Feature Detection and Polyfills']}, {'skill': 'System Design', 'topics': ['Fundamentals of System Design', 'Designing Scalable Systems', 'System Design Patterns', 'Advanced System Design Challenges']}, {'skill': 'JavaScript', 'topics': ['JavaScript Fundamentals', 'Asynchronous JavaScript & AJAX', 'Frontend Frameworks Integration', 'Blockchain Interaction with JavaScript']}, {'skill': 'DSA', 'topics': ['Data Structures', 'Algorithms', 'Complexity Analysis', 'Problem Solving Patterns']}, {'skill': 'Performance Optimization', 'topics': ['Page Load Optimization', 'Resource Loading and Rendering', 'Browser Rendering Optimization', 'Network Performance Tuning']}, {'skill': 'React', 'topics': ['React Fundamentals', 'React State Management', 'Advanced React Patterns', 'React Performance Optimization']} : This is what you will use to create the roadmap from.
    ---

    # To create the roadmap for the user, follow these steps:
    1. Understand the User's Background from user_info and the users_goals they are targeting for.

    2. Know what skills needs to be prioritized from the given skills_array for the user's goal. If the goal is to get a job, switch companies or role, then focus more on the interview aspect first. Keep into account the, who the user is and their experience level, user's target job roles at target companies with the timeline.

    3. Create a list of skills and priority in interviews

    4. Now based on the current skill level, target job roles at desired target companies of the user, decide what skills the user needs to work on more and what skills user can decide to not focus on as much as the user is already good in those. You can also skip the skills if they are alternatives to the skills user already has. e.g. for frontend if the user is skilled in react, then no need to add angular or vue as those are alternatives to react. If there are multiple such alternatives skills consider one of them which is relevant for the target company and skip the rest. e.g. there are different cloud service providers like aws, gcp, azure. User only needs to know one of them, to get started. and only if needed, they need to work on multiple of them.

    5. list down the skills like this.
    { "required_skills": ["skill1", "skill2", "skill3"],
    "skills_to_skip": ["skill4", "skill7", "skill12" ]
    }
    6. Next, Group them along the focus areas listed above
    e.g.
    f1
    - S1
    - S2
    f2
    - S3
    - S4
    f3
    - S5
    - S6
    f4
    - S8
    - S9
    - S10

    7. Now according to the plan, and the topics in each skill and considering the user current state (current_level), map the topics which are required and which can be skipped
    Now the goal is to understand what topics for each skill should be added in the roadmap and what can be skipped.
    A topic can be skipped for two reasons:
    1. If the user is already aware of it according the the current level of the user.
    2. If the Topic is not required for the user's target goals which is {goal} as {domains} and targetting {companies} companies
    8. Based on this add to the group in step 6 to contain topics too
    e.g.
    # f1
    ## S1
    - Topic11
    - Topic12
    - Topic13
    - Topic14
    ## S2
    - Topic21 [Skipped - Familiar]
    - Topic22
    - Topic23
    - Topic24 [Skipped - Not Required]
    # f2
    ## S3
    - Topic31
    - Topic32
    - Topic33 [Skipped - Not Required]
    - Topic34 [Skipped - Not Required]
    ## S4
    - Topic41
    - Topic42
    - Topic43
    - Topic44
    # f3
    ## S5
    ## S6
    # f4
    ## S8
    ## S9
    ## S10

    Here Topics are coming from topics_array.
    Do's:
    - If the skill1 is prerequisite of skill2, skill1 should be covered first then go to skill2.
    - f1 is the not the complete focus area title but just f1
    - S1 is the not the complete Skill title but just S1
    - Topics41 is the complete topic title
    - Skipped can only by of two types: 1. Skipped - Familiar: when user already knows, 2. Skipped - Not Required: when user doesn't need the topic for the target that they have in mind

    Respond with only format provided in step 8
    """,
        },
        {
            "role": "user",
            "content": """1. user_info: I'm a Working Professional with experience of 3 years.
    2. users_goals: My main goal is Employed, looking to switch to another domain/role and I'm targeting these following MAANG, Startups companies to work as one of the following Frontend Developer roles. I'm thinking of preparing for 1 month.
    3. Today's Date: Today is 2024-08-11T00:00:00.000000Z
    4. current_skill_level: my current skill levels are - [{"title": "React"}, {"title": "React", "value": "Beginner"}, {"title": "JavaScript"}, {"title": "JavaScript", "value": "Advanced"}, {"title": "DSA"}, {"title": "DSA", "value": "Intermediate"}, {"title": "System Design"}, {"title": "System Design", "value": "Beginner"}, {"title": "Performance Optimization"}, {"title": "Performance Optimization", "value": "Master"}, {"title": "Cross-Browser Development"}, {"title": "Cross-Browser Development", "value": "Master"}]
    5. Time I can commit to on the roadmap in a week: - {"hours_per_day": "3 hours", "days_per_week": "3 days"}
    Respond only in the way given by the system""",
        },
    ]

    response_content = '{"roadmap_data": [{"status": "Yet To Start", "phase": "Get Familiar with New Domain", "title": "Fundamentals of System Design", "difficultyCategory": "Easy", "skillTitle": "System Design", "topicsConfigurations": ["recKt6wdllKy3JTWU"], "index": 0}, {"status": "Yet To Start", "phase": "Get Familiar with New Domain", "title": "Designing Scalable Systems", "difficultyCategory": "Medium", "skillTitle": "System Design", "topicsConfigurations": ["recSrGa9rypJzQyb6"], "index": 1}, {"status": "Yet To Start", "phase": "Get Familiar with New Domain", "title": "System Design Patterns", "difficultyCategory": "Hard", "skillTitle": "System Design", "topicsConfigurations": ["recfcLIcfHquN3sJA"], "index": 2}, {"status": "Yet To Start", "phase": "Get Familiar with New Domain", "title": "Advanced System Design Challenges", "difficultyCategory": "Legendary", "skillTitle": "System Design", "topicsConfigurations": ["recnDIbQMjIaoMn1z"], "index": 3}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "JavaScript Fundamentals", "difficultyCategory": "Easy", "skillTitle": "JavaScript", "topicsConfigurations": ["recmm7meUH93xNnTM"], "index": 4}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "Asynchronous JavaScript & AJAX", "difficultyCategory": "Medium", "skillTitle": "JavaScript", "topicsConfigurations": ["recGE0Gmatzxb33kE"], "index": 5}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "Frontend Frameworks Integration", "difficultyCategory": "Hard", "skillTitle": "JavaScript", "topicsConfigurations": ["recivqcs6tvHG0GD6"], "index": 6}, {"status": "Skipped - Not Required", "phase": "Master Skills to be Interview Ready", "title": "Blockchain Interaction with JavaScript", "difficultyCategory": "Legendary", "skillTitle": "JavaScript", "topicsConfigurations": ["recFIIaPEBZk4cqd0"], "index": 7}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "Data Structures", "difficultyCategory": "Easy", "skillTitle": "DSA", "topicsConfigurations": ["rec2g6RTSksEpedBx"], "index": 8}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "Algorithms", "difficultyCategory": "Medium", "skillTitle": "DSA", "topicsConfigurations": ["recgGiPmuCp0vNdPh"], "index": 9}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "Complexity Analysis", "difficultyCategory": "Medium", "skillTitle": "DSA", "topicsConfigurations": ["recE2rDAd28fufTri"], "index": 10}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "Problem Solving Patterns", "difficultyCategory": "Hard", "skillTitle": "DSA", "topicsConfigurations": ["recB6R9qvSoRbs1iM"], "index": 11}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "React Fundamentals", "difficultyCategory": "Easy", "skillTitle": "React", "topicsConfigurations": ["recsiKNKDDXtGbxUO"], "index": 12}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "React State Management", "difficultyCategory": "Medium", "skillTitle": "React", "topicsConfigurations": ["recveDClHMdOWIP0W"], "index": 13}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "Advanced React Patterns", "difficultyCategory": "Hard", "skillTitle": "React", "topicsConfigurations": ["receJrjYPCGXhXM0x"], "index": 14}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "React Performance Optimization", "difficultyCategory": "Legendary", "skillTitle": "React", "topicsConfigurations": ["recVxYbTb2fo6IQUq"], "index": 15}, {"status": "Skipped - Familiar", "phase": "Build a Competitive Profile", "title": "Page Load Optimization", "difficultyCategory": "Easy", "skillTitle": "Performance Optimization", "topicsConfigurations": ["recAIM6gAB7DjMk3k"], "index": 16}, {"status": "Skipped - Familiar", "phase": "Build a Competitive Profile", "title": "Resource Loading and Rendering", "difficultyCategory": "Medium", "skillTitle": "Performance Optimization", "topicsConfigurations": ["rec8E1tpUpfrIe0ED"], "index": 17}, {"status": "Skipped - Familiar", "phase": "Build a Competitive Profile", "title": "Browser Rendering Optimization", "difficultyCategory": "Hard", "skillTitle": "Performance Optimization", "topicsConfigurations": ["recCqGgOhPXGvHdyk"], "index": 18}, {"status": "Skipped - Familiar", "phase": "Build a Competitive Profile", "title": "Network Performance Tuning", "difficultyCategory": "Legendary", "skillTitle": "Performance Optimization", "topicsConfigurations": ["recIa4oWJk3gsuIZZ"], "index": 19}, {"status": "Skipped - Familiar", "phase": "Build a Competitive Profile", "title": "Browser Compatibility Testing", "difficultyCategory": "Easy", "skillTitle": "Cross-Browser Development", "topicsConfigurations": ["recTCWzWTeAFLeTAB"], "index": 20}, {"status": "Skipped - Familiar", "phase": "Build a Competitive Profile", "title": "CSS Prefixes and Fallbacks", "difficultyCategory": "Medium", "skillTitle": "Cross-Browser Development", "topicsConfigurations": ["recQEyvTMV3e1rzp6"], "index": 21}, {"status": "Skipped - Familiar", "phase": "Build a Competitive Profile", "title": "JavaScript Transpilation", "difficultyCategory": "Medium", "skillTitle": "Cross-Browser Development", "topicsConfigurations": ["reclWo4aosTlemZRV"], "index": 22}, {"status": "Skipped - Familiar", "phase": "Build a Competitive Profile", "title": "Feature Detection and Polyfills", "difficultyCategory": "Hard", "skillTitle": "Cross-Browser Development", "topicsConfigurations": ["recnurjNWDSWm2gLn"], "index": 23}]}'

    workflow_name = "Slide creation"
    properties = {
        "prompt": str(messages),
        "output": response_content,
        "processingTime": 0.5,
        "functionName": "test_function",
        "tags": ["roadmap", "curriculum", "frontend"],
        "attributes": {
            "user_category": "Fresher",
            "domain": "Frontend",
            "slide_type": "MCQ",
        },
    }

    try:
        tracker.track(workflow_name, properties)
        # If no exception is raised, the test passes
        assert True
    except PromptAnalyticsError as e:
        print(f"Detailed error: {str(e)}")
        pytest.fail(f"Failed to send analytics data: {str(e)}")


@pytest.mark.asyncio
async def test_async_tracking(tracker):
    workflow_name = "Test Async Tracking"
    properties = {
        "prompt": "Async hello!",
        "output": "Async greetings!",
        "processingTime": 0.3,
        "functionName": "async_test_function",
    }

    try:
        await tracker.track_async(workflow_name, properties)
        # If no exception is raised, the test passes
        assert True
    except PromptAnalyticsError as e:
        print(f"Detailed error: {str(e)}")
        pytest.fail(f"Failed to send analytics data asynchronously: {str(e)}")


@pytest.mark.asyncio
async def test_streaming_response(tracker):
    workflow_name = "Test Streaming Response"
    prompt = "Generate a story"

    async def simulate_streaming_response():
        story_parts = [
            "Once upon a time, ",
            "in a land far away, ",
            "there lived a brave knight. ",
            "The end.",
        ]
        full_story = ""
        start_time = asyncio.get_event_loop().time()
        for part in story_parts:
            full_story += part
            yield part
            await asyncio.sleep(0.1)  # Reduced delay for faster tests

        processing_time = asyncio.get_event_loop().time() - start_time

        properties = {
            "prompt": prompt,
            "output": full_story,
            "processingTime": processing_time,
            "functionName": "stream_story",
        }

        try:
            await tracker.track_async(workflow_name, properties)
            # If no exception is raised, the test passes
            assert True
        except PromptAnalyticsError as e:
            print(f"Detailed error: {str(e)}")
            pytest.fail(f"Failed to send streaming analytics data: {str(e)}")

    stream = simulate_streaming_response()

    collected_story = ""
    async for chunk in stream:
        collected_story += chunk

    assert (
        collected_story
        == "Once upon a time, in a land far away, there lived a brave knight. The end."
    )


@pytest.mark.asyncio
async def test_multiple_async_requests(tracker):
    workflow_name = "Test Multiple Async Requests"

    async def send_request(i):
        properties = {
            "prompt": f"Prompt {i}",
            "output": f"Output {i}",
            "processingTime": 0.1,
            "functionName": f"test_function_{i}",
        }
        try:
            await tracker.track_async(workflow_name, properties)
            return True
        except PromptAnalyticsError as e:
            print(f"Request {i} failed: {str(e)}")
            return False

    tasks = [send_request(i) for i in range(10)]
    results = await asyncio.gather(*tasks)

    # Check if all requests were successful
    success_rate = sum(results) / len(results)
    print(f"Success rate: {success_rate * 100}%")
    assert success_rate > 0.8, f"Success rate ({success_rate * 100}%) is below 80%"


@pytest.mark.asyncio
async def test_error_handling(tracker):
    # Temporarily change the dashboard URL to an invalid one
    original_url = tracker.dashboard_url
    tracker.dashboard_url = "http://invalid-url-that-does-not-exist.com"

    workflow_name = "Test Error Handling"
    properties = {
        "prompt": "This should fail",
        "output": "This should raise an error",
        "processingTime": 0.1,
        "functionName": "error_test_function",
    }

    with pytest.raises(PromptAnalyticsError):
        await tracker.track_async(workflow_name, properties)

    # Restore the original URL
    tracker.dashboard_url = original_url


def test_disabled_tracker():
    disabled_tracker = PromptAnalyticsTracker(
        project_token=PROJECT_TOKEN, enabled=False
    )
    workflow_name = "Test Disabled Tracking"
    properties = {
        "prompt": "This should not be sent",
        "output": "This should not be tracked",
        "processingTime": 0.1,
        "functionName": "disabled_test_function",
    }

    disabled_tracker.track(workflow_name, properties)
    # No assertion needed, we just want to make sure no exception is raised


if __name__ == "__main__":
    pytest.main(["-v", __file__])
