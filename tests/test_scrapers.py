from smart_scraper.job_scraper import scrape_jobs_live


def test_scrape_jobs_live_combines_platforms():
    jobs = scrape_jobs_live(["python"], ["Remote"])
    platforms = {job["platform"] for job in jobs}

    expected = {"linkedin", "indeed", "glassdoor", "monster", "remoteok", "angellist"}
    assert expected.issubset(platforms)


def test_linkedin_scraper_filters_easy_apply_recent():
    jobs = [j for j in scrape_jobs_live(["python"], ["Remote"]) if j["platform"] == "linkedin"]
    assert jobs, "LinkedIn scraper should return at least one job"
    assert all(j.get("easy_apply") for j in jobs)
    assert all(j.get("posted_hours") <= 24 for j in jobs)
    assert expected.issubset(platforms)
