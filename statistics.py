class Stat:
    def __init__(self):
        self.time = []
        self.results = {True: 0, False: 0}

    def get(self):
        avg_time = 0
        if self.time:
            min_time = min(self.time)
            max_time = max(self.time)
            avg_time = sum(self.time) / len(self.time)
        res = f'Ping statistics:\n ' \
              f'{self.results[True] + self.results[False]} times sent\n' \
              f'{self.results[True]} successful ' \
              f'{self.results[False]} failed\n'
        if avg_time != 0:
            res += f'Time statistics:\n' \
              f'Min = {min_time}ms, Max = {max_time}ms, Avg = {avg_time}ms'
        print(res)
