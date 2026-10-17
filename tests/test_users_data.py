import requests

def test_four_users():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Test listing users
    res = requests.get(f"{base_url}/api/profile/users")
    assert res.status_code == 200, f"Failed users list: {res.text}"
    users = res.json()
    print(f"Users found: {len(users)}")
    user_ids = [u["id"] for u in users]
    for expected_id in ["default_user", "user_jordan_chen", "user_priya_sharma", "user_marcus_vance"]:
        assert expected_id in user_ids, f"Missing user: {expected_id}"
    
    # 2. Test detailed data for all 4 users
    for uid in ["default_user", "user_jordan_chen", "user_priya_sharma", "user_marcus_vance"]:
        # Profile
        p = requests.get(f"{base_url}/api/profile?user_id={uid}").json()
        assert p["id"] == uid
        assert len(p["interests"]) > 0
        assert len(p["current_skills"]) > 0
        
        # Roadmap
        tasks = requests.get(f"{base_url}/api/roadmap?user_id={uid}").json()
        assert len(tasks) >= 5, f"Expected at least 5 tasks for {uid}, got {len(tasks)}"
        
        # Skills
        skills = requests.get(f"{base_url}/api/skills?user_id={uid}").json()
        assert len(skills) >= 5, f"Expected at least 5 skills for {uid}, got {len(skills)}"
        gap_skills = [s for s in skills if s.get("is_gap")]
        assert len(gap_skills) >= 1, f"Expected at least 1 gap skill for {uid}"
        
        # GitHub Repositories
        repos = requests.get(f"{base_url}/api/github/repositories?user_id={uid}").json()
        assert len(repos) >= 2, f"Expected 2 repos for {uid}, got {len(repos)}"
        
        # Chat Messages
        chat = requests.get(f"{base_url}/api/chat/messages?user_id={uid}").json()
        assert len(chat) >= 1, f"Expected welcome chat message for {uid}"
        
        # Assessments
        asmt = requests.get(f"{base_url}/api/assessments/latest?user_id={uid}").json()
        assert asmt is not None and asmt.get("overall_score") is not None, f"Expected assessment for {uid}"
        
        print(f"SUCCESS: User {uid} ({p['name']}) verified. Target: {p['target_career_id']}, Tasks: {len(tasks)}, Skills: {len(skills)}, Repos: {len(repos)}, Score: {asmt['overall_score']}")

if __name__ == "__main__":
    test_four_users()
