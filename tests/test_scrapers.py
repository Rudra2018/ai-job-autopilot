from smart_scraper.job_scraper import scrape_jobs_live


def test_scrape_jobs_live_combines_platforms():
    jobs = scrape_jobs_live(["python"], ["Remote"])
    platforms = {job["platform"] for job in jobs}
    expected = {"linkedin", "indeed", "glassdoor", "monster", "remoteok", "angellist"}
    assert expected.issubset(platforms)
