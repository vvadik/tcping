import ping


class Stat:
    def __init__(self):
        self.time = []
        self.results = {'success': 0, 'failed': 0}
        self.min_time = 0
        self.max_time = 0
        self.avg_time = 0

    def get(self):
        if self.time:
            self.min_time = min(self.time)
            self.max_time = max(self.time)
            self.avg_time = sum(self.time) / len(self.time)

    def add(self, reasone, time):
        if time > 0:
            time = round(time * 1000, 3)
            self.time.append(time)
        if reasone is ping.Answer.PORT_OPEN:
            self.results['success'] += 1
        else:
            self.results['failed'] += 1

    def sumup(self):
        res = (f'Ping statistics:\n '
               f'{self.results["success"] + self.results["failed"]} '
               f'times sent\n{self.results["success"]} successful '
               f'{self.results["failed"]} failed\n')
        if self.avg_time != 0:
            res += (f'Time statistics:\n'
                    f'Min = {self.min_time}ms, Max = '
                    f'{self.max_time}ms, Avg = {self.avg_time}ms')
        return res
