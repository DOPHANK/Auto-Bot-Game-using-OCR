class MissionMatcher:
    def __init__(self):
        pass

    def match(self, quests, missions):
        """
        Match active quests with available missions.

        quests:
            [
                {
                    "type": "Fight",
                    "template": "...",
                    "score": 0.91
                },
                ...
            ]

        missions:
            [
                {
                    "type": "Fight",
                    "template": "...",
                    "score": 0.88,
                    "center": (x, y)
                },
                ...
            ]

        Returns:
            [
                {
                    "quest": {...},
                    "mission": {...}
                }
            ]
        """

        matches = []

        used_missions = set()

        for quest in quests:
            quest_type = quest["type"]

            for i, mission in enumerate(missions):

                if i in used_missions:
                    continue

                if mission["type"] != quest_type:
                    continue

                matches.append({
                    "quest": quest,
                    "mission": mission
                })

                used_missions.add(i)
                break

        return matches