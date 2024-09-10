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
    print("Project Token:", PROJECT_TOKEN)
    return PromptAnalyticsTracker(project_token=PROJECT_TOKEN, enabled=True)


def test_tracker_initialization(tracker):
    assert tracker.project_token == PROJECT_TOKEN
    assert tracker.enabled == True
    assert tracker.dashboard_url == DASHBOARD_URL


def test_tracker_initialization_error():
    with pytest.raises(PromptAnalyticsError, match="project_token is required"):
        PromptAnalyticsTracker(project_token="")


# def test_sync_tracking(tracker):
#     messages = [
#         {
#             """
#             \"System: \\nYour task is to take a set of facts, ensure they fit a certain criteria, then return the facts in exactly the same format as the input, but with the criteria met. Make sure to NOT CHANGE THE FACT AT ALL, make as minimal changes as possible to meet the criteria.\\n\\n# Criteria 1: Every fact should only use the first name of the client, never anything else.\\n- The output facts should follow the following criteria: Every fact should only use the first name of the client, never anything else.\\n- The fact should not refer to the client as 'the client', 'He', 'She', 'Speaker B', .... It should refer to them as the first name.\\n- The fact may refer to other names (e.g. the partner's name may be mentioned), ensure that these names are not changed.\\n\\n# Criteria 2: The fact should use British English\\n- The fact should use British English instead of American English or any other dialect.\\n- Ensure that the spelling, grammar, and punctuation are all in British English.\\n- For example, 'color' should be changed to 'colour', 'center' should be changed to 'centre', 'realize' should be changed to 'realise', etc.\\n\\n# Response Format\\n- The response should be in EXACTLY the same JSON format as the input.\\n- Ensure that you return ALL facts from the input. If you receive 1, return 1. If you receive 10, return 10. Do not change the number of facts in the response.\\n\\n\\nHuman: Here the facts for client Nikhil:\\n[{\\\"id\\\": 4, \\\"fact\\\": \\\"\\\\nHe has historically set aside money annually for holidays, vehicle expenses, and Christmas. He believes in financial stability and the reason he has\\\\nset aside money annually for holidays, vehicle expenses, and Christmas.\\\\nHe can be confident that he has set aside money annually for holidays, vehicle expenses, and Christmas.\\\\n\\\", \\\"first_name\\\": \\\"Nikhil\\\"
#             """
#         },
#     ]

#     response_content = """
#     {
#   "response": [
#     {
#       "component_type": "markdown",
#       "data": "### Test Automation Plan Example\n\nIn this exercise, you will create a basic structure of a test automation plan using Python. Imagine you are working on a project where you need to automate the testing of a web application. Your task is to outline the key components of the test automation plan in code.\n\n**Key Components to Include:**\n1. **Objectives**: Define the goals of your test automation.\n2. **Scope**: Specify what will be automated and what will not.\n3. **Timeline**: Outline the schedule for the automation tasks.\n4. **Tools**: List the tools and technologies you will use.\n5. **Resources**: Identify the team members and their roles.\n\nUse the following template to get started:"
#     },
#     {
#       "component_type": "code_editor",
#       "data": {
#         "question": "Create a basic structure of a test automation plan in Python. Include objectives, scope, timeline, tools, and resources.",
#         "language": "python",
#         "default": "class TestAutomationPlan:\n    def __init__(self):\n        self.objectives = []\n        self.scope = []\n        self.timeline = {}\n        self.tools = []\n        self.resources = {}\n\n    def add_objective(self, objective):\n        self.objectives.append(objective)\n\n    def add_scope(self, item):\n        self.scope.append(item)\n\n    def set_timeline(self, phase, duration):\n        self.timeline[phase] = duration\n\n    def add_tool(self, tool):\n        self.tools.append(tool)\n\n    def add_resource(self, role, person):\n        self.resources[role] = person\n\n# Example usage\nplan = TestAutomationPlan()\nplan.add_objective('Increase test coverage')\nplan.add_scope('Automate login tests')\nplan.set_timeline('Phase 1', '2 weeks')\nplan.add_tool('Selenium')\nplan.add_resource('QA Engineer', 'John Doe')\nprint(plan.objectives)\nprint(plan.scope)\nprint(plan.timeline)\nprint(plan.tools)\nprint(plan.resources)",
#         "output": "['Increase test coverage']\n['Automate login tests']\n{'Phase 1': '2 weeks'}\n['Selenium']\n{'QA Engineer': 'John Doe'}"
#       }
#     },
#     {
#       "component_type": "markdown",
#       "data": "📺 **Resource:** [Showcasing Projects in Selenium Automation Testing Interviews](https://www.youtube.com/watch?v=x9vAgJSq2O0)\n\n**Relevant Timestamps:**\n- 00:00 - Introduction\n- 02:15 - Importance of Understanding the Framework\n- 05:30 - Presenting Your Experience Effectively\n- 08:45 - Tools and Technologies\n\nThis video will help you understand how to present your test automation plan and experience effectively during interviews."
#     }
#   ]
# }
#     """

#     workflow_name = "preplaced"
#     properties = {
#         "prompt": str(messages),
#         "output": response_content,
#         "processingTime": 0.5,
#         "functionName": "Roadmap Creation",
#         "tags": ["new"],
#         "attributes": {
#             "user_category_12": "Fresher",
#             "experience_12": "0",
#             "goal": "Graduated, looking for their first job",
#             "targetCompanies": ["Consultation Firms"],
#             "targetDomains": ["Frontend Developer"],
#         },
#     }

#     try:
#         id = tracker.track(workflow_name, properties)
#         print("Prompt Id:", id)
#         # If no exception is raised, the test passes
#         assert True
#     except PromptAnalyticsError as e:
#         print(f"Detailed error: {str(e)}")
#         pytest.fail(f"Failed to send analytics data: {str(e)}")


def test_sync_tracking(tracker):
    prompt_type = "Roadmap Creation"
    Prompt_data = {
        "prompt": "[{\"role\": \"system\", \"content\": \"You are an AI expert personal curriculum Designer at Preplaced, an AI Learning and Mentorship Platform. \\nYou create the most optimized and fastest personal Learning Paths/Roadmaps for users based on data they provide Target domains,\\nGoals,target companies, current user category,current skill level, and their estimated possible effort in terms of time from their side.\\n\\n### Instructions to follow\\n\\nUser will provide following data:\\n\\n1. user_info:  This contains information regarding the user, whether they are college students(fresher) or working professionals and the years of industry experience they have.\\n2. users_goals: This contains the user's main goal, roles user is targeting, the companies in which user is looking to apply to, the timeline they have in mind to prepare for these roles\\n3. Today's Date: This is used as a reference point to start the roadmap.\\n4. current_skill_level: The current skill level of the user in few of the skills required for the role.\\n5. Time user can commit to on the roadmap in a week: the time user can dedicate every week to follow the roadmap\\n\\nUse these following data to complete your roadmap creation task.\\n1. skills_array: S1 - Microservices Architecture\\n S2 - DSA\\n S3 - Database Management\\n S4 - System Design\\n S5 - Kubernetes\\n S6 - Cloud Services\\n S7 - Docker\\n S8 - API Development\\n S9 - SQL\\n S10 - NoSQL\\n S11 - DevOps Practices\\n  : This is the set of skills needed for the roles user is targeting and wants to prepare for. \\n2. focus_areas: f1 - Build Foundational Skills\\n f2 - Master Skills to be Interview Ready\\n f3 - Enhance Your Profile\\n f4 - To be Skipped \\n3. topics_array: {'skill': 'Microservices Architecture', 'topics': ['Introduction to Microservices', 'Designing Microservices', 'Microservices Communication Patterns', 'Microservices with Containerization']}, {'skill': 'DSA', 'topics': ['Data Structures', 'Algorithms', 'Complexity Analysis', 'Problem Solving Patterns']}, {'skill': 'Database Management', 'topics': ['Relational Database Fundamentals', 'NoSQL and Non-Relational Databases', 'Database Optimization and Indexing', 'Database Security and Compliance']}, {'skill': 'System Design', 'topics': ['Fundamentals of System Design', 'Designing Scalable Systems', 'System Design Patterns', 'Advanced System Design Challenges']}, {'skill': 'Kubernetes', 'topics': ['Kubernetes Fundamentals', 'Kubernetes Networking', 'Kubernetes Security', 'Kubernetes Deployment Strategies']}, {'skill': 'Cloud Services', 'topics': ['Cloud Service Fundamentals', 'Cloud Infrastructure Management', 'Cloud-Native Technologies', 'Advanced Cloud Security']}, {'skill': 'Docker', 'topics': ['Docker Basics', 'Docker Compose and Networking', 'Docker Images and Containers', 'Docker in CI/CD Pipelines']}, {'skill': 'API Development', 'topics': ['Introduction to API Development', 'RESTful API Design', 'API Security Best Practices', 'Advanced API Development with GraphQL']}, {'skill': 'SQL', 'topics': ['SQL Fundamentals', 'Advanced Query Techniques', 'Database Optimization', 'SQL for Big Data']}, {'skill': 'NoSQL', 'topics': ['NoSQL Databases Introduction', 'NoSQL Data Modeling', 'NoSQL Query Languages', 'Scaling NoSQL Systems']}, {'skill': 'DevOps Practices', 'topics': ['Continuous Integration and Continuous Deployment (CI/CD)', 'Infrastructure as Code (IaC)', 'Monitoring and Observability', 'Security and Compliance in DevOps']} : This is what you will use to create the roadmap from.\\n---\\n\\n# To create the roadmap for the user, follow these steps:\\n1. Understand the User's Background from user_info and the users_goals they are targeting for. \\n\\n2. Know what skills needs to be prioritized from the given skills_array for the user's goal. If the goal is to get a job, switch companies or role, then focus more on the interview aspect first. Keep into account the, who the user is and their experience level, user's target job roles at target companies with the timeline.\\n\\n3. Create a list of skills and priority in interviews\\n\\n4. Now based on the current skill level, target job roles at desired target companies of the user, decide what skills the user needs to work on more and what skills user can decide to not focus on as much as the user is already good in those. You can also skip the skills if they are alternatives to the skills user already has. e.g. for frontend if the user is skilled in react, then no need to add angular or vue as those are alternatives to react. If there are multiple such alternatives skills consider one of them which is relevant for the target company and skip the rest. e.g. there are different cloud service providers like aws, gcp, azure. User only needs to know one of them, to get started. and only if needed, they need to work on multiple of them.    \\n\\n5. list down the skills like this.\\n{ \\\"required_skills\\\": [\\\"skill1\\\", \\\"skill2\\\", \\\"skill3\\\"],\\n  \\\"skills_to_skip\\\": [\\\"skill4\\\", \\\"skill7\\\", \\\"skill12\\\" ]\\n}\\n6. Next, Group them along the focus areas listed above\\ne.g.\\nf1\\n    - S1\\n    - S2\\nf2\\n    - S3\\n    - S4\\nf3\\n    - S5\\n    - S6\\nf4\\n    - S8\\n    - S9\\n    - S10\\n\\n7. Now according to the plan, and the topics in each skill and considering the user current state (current_level), map the topics which are required and which can be skipped\\nNow the goal is to understand what topics for each skill should be added in the roadmap and what can be skipped.\\nA topic can be skipped for two reasons:\\n    1. If the user is already aware of it according the the current level of the user.\\n    2. If the Topic is not required for the user's target goals which is {goal} as {domains} and targetting {companies} companies\\n8. Based on this add to the group in step 6 to contain topics too \\ne.g.\\n# f1\\n## S1\\n- Topic11\\n- Topic12\\n- Topic13\\n- Topic14\\n## S2\\n- Topic21 [Skipped - Familiar]\\n- Topic22\\n- Topic23\\n- Topic24 [Skipped - Not Required]\\n# f2\\n## S3\\n- Topic31\\n- Topic32\\n- Topic33 [Skipped - Not Required]\\n- Topic34 [Skipped - Not Required]\\n## S4\\n- Topic41\\n- Topic42\\n- Topic43\\n- Topic44\\n# f3\\n## S5\\n## S6\\n# f4\\n## S8\\n## S9\\n## S10\\n\\nHere Topics are coming from topics_array.\\nDo's:\\n- If the skill1 is prerequisite of skill2, skill1 should be covered first then go to skill2.\\n- f1 is the not the complete focus area title but just f1\\n- S1 is the not the complete Skill title but just S1\\n- Topics41 is the complete topic title\\n- Skipped can only by of two types: 1. Skipped - Familiar: when user already knows, 2. Skipped - Not Required: when user doesn't need the topic for the target that they have in mind\\n\\nRespond with only format provided in step 8\\n\\n\\n\\n\\n\\n\"}, {\"role\": \"user\", \"content\": \"1. user_info: I'm a Fresher with experience of 0 years.\\n2. users_goals: My main goal is Graduated, looking for their first job and I'm targeting these following Service Based companies to work as one of the following Backend Developer roles. I'm thinking of preparing for . \\n3. Today's Date: Today is 2024-09-10T00:00:00.000000Z\\n4. current_skill_level: my current skill levels are - [{\\\"title\\\": \\\"DSA\\\"}, {\\\"title\\\": \\\"DSA\\\", \\\"value\\\": 9}, {\\\"title\\\": \\\"API Development\\\"}, {\\\"title\\\": \\\"API Development\\\", \\\"value\\\": 9}, {\\\"title\\\": \\\"Database Management\\\"}, {\\\"title\\\": \\\"Database Management\\\", \\\"value\\\": 9}, {\\\"title\\\": \\\"Docker\\\"}, {\\\"title\\\": \\\"Docker\\\", \\\"value\\\": 9}, {\\\"title\\\": \\\"System Design\\\"}, {\\\"title\\\": \\\"System Design\\\", \\\"value\\\": 9}, {\\\"title\\\": \\\"SQL\\\"}, {\\\"title\\\": \\\"SQL\\\", \\\"value\\\": 8}]\\n5. Time I can commit to on the roadmap in a week:  - {\\\"hours_per_day\\\": \\\"2 hours\\\", \\\"days_per_week\\\": \\\"3 days\\\"}\\nRespond only in the way given by the system\"}]",
        "output": '{"roadmap_data": [{"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Introduction to Microservices", "difficultyCategory": "Easy", "skillTitle": "Microservices Architecture", "topicsConfigurations": ["reclTKQuS2UrpvfVV"], "index": 0}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Designing Microservices", "difficultyCategory": "Medium", "skillTitle": "Microservices Architecture", "topicsConfigurations": ["recZNorJ1TMRvDYxj"], "index": 1}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Microservices Communication Patterns", "difficultyCategory": "Medium", "skillTitle": "Microservices Architecture", "topicsConfigurations": ["recieQ4VP6Ucmr6e0"], "index": 2}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Microservices with Containerization", "difficultyCategory": "Hard", "skillTitle": "Microservices Architecture", "topicsConfigurations": ["recskQYdYpoA6wnAD"], "index": 3}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Kubernetes Fundamentals", "difficultyCategory": "Easy", "skillTitle": "Kubernetes", "topicsConfigurations": ["recvBfODzInaiWJVh"], "index": 4}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Kubernetes Networking", "difficultyCategory": "Medium", "skillTitle": "Kubernetes", "topicsConfigurations": ["recMk62xIodoTb6uZ"], "index": 5}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Kubernetes Security", "difficultyCategory": "Hard", "skillTitle": "Kubernetes", "topicsConfigurations": ["recEfEXZOTrvJVyni"], "index": 6}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Kubernetes Deployment Strategies", "difficultyCategory": "Medium", "skillTitle": "Kubernetes", "topicsConfigurations": ["recmpefjTws2dmGR5"], "index": 7}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Cloud Service Fundamentals", "difficultyCategory": "Easy", "skillTitle": "Cloud Services", "topicsConfigurations": ["reczxZyZaKfsR0OCC"], "index": 8}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Cloud Infrastructure Management", "difficultyCategory": "Medium", "skillTitle": "Cloud Services", "topicsConfigurations": ["recCyfsJmbmQb4jMY"], "index": 9}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Cloud-Native Technologies", "difficultyCategory": "Hard", "skillTitle": "Cloud Services", "topicsConfigurations": ["recYWbXftvq5azxWp"], "index": 10}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Advanced Cloud Security", "difficultyCategory": "Legendary", "skillTitle": "Cloud Services", "topicsConfigurations": ["recJbkJD4pCrxwqZD"], "index": 11}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "NoSQL Databases Introduction", "difficultyCategory": "Easy", "skillTitle": "NoSQL", "topicsConfigurations": ["recX6Wz9F5XW9uHFJ"], "index": 12}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "NoSQL Data Modeling", "difficultyCategory": "Medium", "skillTitle": "NoSQL", "topicsConfigurations": ["reclxRtX5uMhQuDWr"], "index": 13}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "NoSQL Query Languages", "difficultyCategory": "Medium", "skillTitle": "NoSQL", "topicsConfigurations": ["recJZDyBiTamhcM3j"], "index": 14}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Scaling NoSQL Systems", "difficultyCategory": "Hard", "skillTitle": "NoSQL", "topicsConfigurations": ["rec6XPDYUcJugjDH7"], "index": 15}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Continuous Integration and Continuous Deployment (CI/CD)", "difficultyCategory": "Medium", "skillTitle": "DevOps Practices", "topicsConfigurations": ["rec1FjzCI2iwa4qvP"], "index": 16}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Infrastructure as Code (IaC)", "difficultyCategory": "Medium", "skillTitle": "DevOps Practices", "topicsConfigurations": ["recZtW7ibgQ248qku"], "index": 17}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Monitoring and Observability", "difficultyCategory": "Hard", "skillTitle": "DevOps Practices", "topicsConfigurations": ["recMs505wgmQ1hScB"], "index": 18}, {"status": "Yet To Start", "phase": "Build Foundational Skills", "title": "Security and Compliance in DevOps", "difficultyCategory": "Hard", "skillTitle": "DevOps Practices", "topicsConfigurations": ["recmseOQVazO7kMrA"], "index": 19}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Data Structures", "difficultyCategory": "Easy", "skillTitle": "DSA", "topicsConfigurations": ["rec2g6RTSksEpedBx"], "index": 20}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Algorithms", "difficultyCategory": "Medium", "skillTitle": "DSA", "topicsConfigurations": ["recgGiPmuCp0vNdPh"], "index": 21}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Complexity Analysis", "difficultyCategory": "Medium", "skillTitle": "DSA", "topicsConfigurations": ["recE2rDAd28fufTri"], "index": 22}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Problem Solving Patterns", "difficultyCategory": "Hard", "skillTitle": "DSA", "topicsConfigurations": ["recB6R9qvSoRbs1iM"], "index": 23}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Relational Database Fundamentals", "difficultyCategory": "Easy", "skillTitle": "Database Management", "topicsConfigurations": ["rectcDLKEv4qjhlGt"], "index": 24}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "NoSQL and Non-Relational Databases", "difficultyCategory": "Medium", "skillTitle": "Database Management", "topicsConfigurations": ["recHMg5u3NPEcvvZ8"], "index": 25}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Database Optimization and Indexing", "difficultyCategory": "Hard", "skillTitle": "Database Management", "topicsConfigurations": ["recK6TahwDmpnHa4c"], "index": 26}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Database Security and Compliance", "difficultyCategory": "Hard", "skillTitle": "Database Management", "topicsConfigurations": ["recGR9FN3HESRt0WK"], "index": 27}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Fundamentals of System Design", "difficultyCategory": "Easy", "skillTitle": "System Design", "topicsConfigurations": ["recKt6wdllKy3JTWU"], "index": 28}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Designing Scalable Systems", "difficultyCategory": "Medium", "skillTitle": "System Design", "topicsConfigurations": ["recSrGa9rypJzQyb6"], "index": 29}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "System Design Patterns", "difficultyCategory": "Hard", "skillTitle": "System Design", "topicsConfigurations": ["recfcLIcfHquN3sJA"], "index": 30}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Advanced System Design Challenges", "difficultyCategory": "Legendary", "skillTitle": "System Design", "topicsConfigurations": ["recnDIbQMjIaoMn1z"], "index": 31}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Introduction to API Development", "difficultyCategory": "Easy", "skillTitle": "API Development", "topicsConfigurations": ["recmdxRANnHrGDyET"], "index": 32}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "RESTful API Design", "difficultyCategory": "Medium", "skillTitle": "API Development", "topicsConfigurations": ["recguycS7EfFp180K"], "index": 33}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "API Security Best Practices", "difficultyCategory": "Hard", "skillTitle": "API Development", "topicsConfigurations": ["recQdnQLXRC7CYbnY"], "index": 34}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Advanced API Development with GraphQL", "difficultyCategory": "Legendary", "skillTitle": "API Development", "topicsConfigurations": ["recdt8qwzycR33SvD"], "index": 35}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "SQL Fundamentals", "difficultyCategory": "Easy", "skillTitle": "SQL", "topicsConfigurations": ["recOH3WYveNyOAwql"], "index": 36}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Advanced Query Techniques", "difficultyCategory": "Medium", "skillTitle": "SQL", "topicsConfigurations": ["recUfpm1jlaXI1RMw"], "index": 37}, {"status": "Skipped - Familiar", "phase": "Master Skills to be Interview Ready", "title": "Database Optimization", "difficultyCategory": "Hard", "skillTitle": "SQL", "topicsConfigurations": ["recoICQlmwcpVjeTa"], "index": 38}, {"status": "Yet To Start", "phase": "Master Skills to be Interview Ready", "title": "SQL for Big Data", "difficultyCategory": "Legendary", "skillTitle": "SQL", "topicsConfigurations": ["recEFYLcd0fcaNjgx"], "index": 39}, {"status": "Skipped - Familiar", "phase": "Enhance Your Profile", "title": "Docker Basics", "difficultyCategory": "Easy", "skillTitle": "Docker", "topicsConfigurations": ["recBLD8Wxi65O8MLW"], "index": 40}, {"status": "Skipped - Familiar", "phase": "Enhance Your Profile", "title": "Docker Compose and Networking", "difficultyCategory": "Medium", "skillTitle": "Docker", "topicsConfigurations": ["recRMeKNZPemU8JFc"], "index": 41}, {"status": "Skipped - Familiar", "phase": "Enhance Your Profile", "title": "Docker Images and Containers", "difficultyCategory": "Medium", "skillTitle": "Docker", "topicsConfigurations": ["recFzxnWstb2Fda1r"], "index": 42}, {"status": "Skipped - Familiar", "phase": "Enhance Your Profile", "title": "Docker in CI/CD Pipelines", "difficultyCategory": "Hard", "skillTitle": "Docker", "topicsConfigurations": ["recPpirShGHE1FCpr"], "index": 43}]}',
        "attributes": {
            "user_category": "Fresher",
            "experience": "1",
            "goal": ("Graduated, looking for their first job"),
            "targetCompanies": ["Service Based"],
            "targetDomains": ["Backend Developer"],
        },
        "tags": ["new"],
    }

    try:
        id = tracker.track(prompt_type, Prompt_data)
        print("Prompt Id:", id)
        # If no exception is raised, the test passes
        assert True
    except PromptAnalyticsError as e:
        print(f"Detailed error: {str(e)}")
        pytest.fail(f"Failed to send analytics data: {str(e)}")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
