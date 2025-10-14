from multiprocessing import Process
from time import sleep

# TODO add condition for ai command retreat to camp or go to specific pos when added

# class EnemyCommandHandlerAI:
#     def __init__(self):
#         self.input_list = []
#
#         Process(target=self._loop, daemon=True).start()
#
#     def _loop(self):
#         while True:
#             # Check for commands
#             if self.input_list:
#                 unit = self.input_list[0].ai_logic()
#                 self.input_list = self.input_list[1:]
