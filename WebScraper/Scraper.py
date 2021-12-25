from WebScraper.Job import Job

import logging

logger = logging.getLogger(__name__)


class Scraper(object):

    def __init__(self, queue, sitemap, browser, *args, **kwargs):
        self.queue = queue
        self.sitemap = sitemap
        self.browser = browser

        self.results_writer = list()

        # TODO The database stores related handles

    def init_first_job(self):
        startUrl = self.sitemap.__getattribute__("startUrl")

        rootJob = Job(url=startUrl, parentSelectorId="_root", scraper=self, parentJob=None, baseData=None)

        if not self.queue.is_full():
            self.queue.add(rootJob)
        else:
            raise RuntimeError("Task Queue failed")

    def run(self):

        self.init_first_job()

        # TODO Initialize the database write instance

        self._run()
        return self.results_writer

    def record_can_have_child_jobs(self, record):
        if "_follow" not in record.keys():
            return False

        followSelectorId = record.get("_followSelectorId")
        child_selectors = self.sitemap.get_direct_child_selectors(followSelectorId)
        if child_selectors:
            return True
        return False

    def _run(self):

        job = self.queue.get_next_job()

        if not job:
            logger.info("Data fetching is complete...")
            return

        job.execute(browser=self.browser)

        results = job.get_results()

        for record in results:
            if self.record_can_have_child_jobs(record):
                follow_url = record.get("_follow")
                follow_selector = record.get("_followSelectorId")
                del record["_follow"]
                del record["_followSelectorId"]

                new_job = Job(url=follow_url, parentSelectorId=follow_selector, scraper=self, parentJob=job, baseData=record)

                if not self.queue.is_full():
                    self.queue.add(new_job)
            else:
                if "_follow" in record.keys():
                    del record["_follow"]
                    del record["_followSelectorId"]
                self.results_writer.append(record)

        self._run()

