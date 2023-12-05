#!/usr/bin/env python3

import sys
import os
import shutil
import time
import logging
from pathlib import Path


class CronManager:

    def __init__(self, crondee, desired_crondee, sleep_duration):
        self.cron_dir = Path(crondee)
        self.desired_job_dir = Path(desired_crondee)
        self.sleeper = sleep_duration
        logging.info("cronmanager active")
        logging.info("target dir: {}".format(self.cron_dir))
        logging.info("source dir: {}".format(self.desired_job_dir))

    def loop(self):
        while True:
            logging.info("looping")
            active_jobs = self.scan_dir(self.cron_dir)
            desired_jobs = self.scan_dir(self.desired_job_dir)
            # we don't want users touching the cron.allow file
            active_jobs.remove('cron.allow')
            if 'cron.allow' in desired_jobs:
                desired_jobs.remove('cron.allow')
            # don't know what this is but we don't want it
            desired_jobs.remove('.placeholder')

            if '.ipynb_checkpoints' in desired_jobs:
                desired_jobs.remove('.ipynb_checkpoints')

            # 0 is nothing, 1 is add_job, 2 is remove_job
            operation = 0
            job_diff = []

            if len(active_jobs) < len(desired_jobs):
                job_diff = [job for job in desired_jobs if job not in active_jobs]
                operation = 1
            else:
                job_diff = [job for job in active_jobs if job not in desired_jobs]
                operation = 2

            logging.info("job diff: {}".format(job_diff))
            self.operate(operation, job_diff)

            common_jobs = [job for job in desired_jobs if job not in job_diff]
            logging.info("common jobs: {}".format(common_jobs))
            updated_jobs = self.get_updated_jobs(common_jobs)
            if len(updated_jobs) > 0:
                logging.info("jobs with updates: {}".format(updated_jobs))
                self.operate(3, updated_jobs)

            logging.info("sleeping for {} seconds".format(self.sleeper))
            time.sleep(self.sleeper)

    def operate(self, operation, jobs):
        for job in jobs:
            if operation == 1:
                logging.info("adding job {} to cron.d".format(job))
                self.add_job(job)
            elif operation == 2:
                logging.info("removing job {} from cron.d".format(job))
                self.remove_job(job)
            elif operation == 3:
                logging.info("updating job {} in cron.d".format(job))
                self.add_job(job)
            else:
                return

    def scan_dir(self, d):
        return os.listdir(d)

    def get_updated_jobs(self, jobs):
        updated_jobs = []
        for job in jobs:
            source = self.desired_job_dir / job
            target = self.cron_dir / job
            with open(source, 'r') as s, open(target, 'r') as t:
                s_lines = set(s.readlines())
                t_lines = set(t.readlines())
                if len(s_lines.difference(t_lines)) > 0:
                    updated_jobs.append(job)

        return updated_jobs

    def add_job(self, job):
        source = self.desired_job_dir / job
        target = self.cron_dir / job
        shutil.copy2(source, target)
        os.chown(target, 0, 0)

    def remove_job(self, job):
        target = self.cron_dir / job
        os.remove(target)


if __name__ == "__main__":
    logfile = sys.argv[4]
    logging.basicConfig(filename=logfile,
                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)
    logging.info("initializing")
    crondee = sys.argv[1]
    desired = sys.argv[2]
    eepy = int(sys.argv[3])


    man = CronManager(crondee, desired, eepy)
    man.loop()
