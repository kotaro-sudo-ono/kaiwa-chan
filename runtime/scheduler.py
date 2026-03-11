# runtime/scheduler.py

import time


class Scheduler:

    def __init__(self, agent):
        self.agent = agent
        self.running = True

    def start(self, max_steps=None):

        steps = 0

        while self.running:

            self.agent.run_once()

            steps += 1

            if max_steps and steps >= max_steps:
                break

            time.sleep(1)

    def stop(self):
        self.running = False