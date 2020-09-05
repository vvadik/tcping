class Stat:
    def __init__(self):
        self.time = []
        self.results = {True: 0, False: 0}

    def get(self):
        min_time = 100000
        max_time = 0
        avg_time = 0
        for i in self.time:
            if i < min_time:
                min_time = i
            if i > max_time:
                max_time = i
            avg_time += i
        if avg_time != 0:
            avg_time = avg_time / len(self.time)
        res = f'Ping statistics:\n ' \
              f'{self.results[True] + self.results[False]} times sent\n' \
              f'{self.results[True]} successful ' \
              f'{self.results[False]} failed\n'
        if avg_time != 0:
            res += f'Time statistics:\n' \
              f'Min = {min_time}ms, Max = {max_time}ms, Avg = {avg_time}ms'
        print(res)
