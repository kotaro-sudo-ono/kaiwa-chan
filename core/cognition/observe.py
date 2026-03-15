class Observer:
    def __init__(self, memory_manager, task_manager):
        self.memory_manager = memory_manager
        self.task_manager = task_manager

    def observe(self, user_input: str, llm_reply: str = None):
        # ユーザ入力を記憶
        self.memory_manager.add_memory(user_input)

        tasks = []

        # LLM返答があればタスク化
        if llm_reply and llm_reply.strip():
            task = self.task_manager.create_task(
                task_type="print_message",
                payload={"message": llm_reply}  # これがVoiceVoxで喋られる
            )
            tasks.append(task)

        context = {
            "user_input": user_input,
            "memory": self.memory_manager.get_all(),
            "tasks": tasks,
        }
        return context