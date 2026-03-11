# agents/base_agent.py

class BaseAgent:

    def __init__(self, task_manager, tool_registry):
        self.task_manager = task_manager
        self.tool_registry = tool_registry

    def run_once(self):

        task = self.task_manager.get_next_task()

        if not task:
            print("no task")
            return

        tool = self.tool_registry.get(task.type)

        if not tool:
            print("tool not found:", task.type)
            return

        tool.execute(**task.payload)

        task.status = "completed"

        print("task completed:", task.id)