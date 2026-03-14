class Thinker:

    def think(self, context):

        user_input = context["user_input"]

        if "hello" in user_input.lower():
            intent = "greeting"
        else:
            intent = "unknown"

        result = {
            "intent": intent,
            "context": context
        }

        return result