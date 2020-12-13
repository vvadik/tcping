import ping


def print_stat(stat):
    result = stat.sumup()
    print(result)


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

    def add(self, reasone, time, dst_host, dst_port):
        if time != 0:
            time = round(time * 1000, 3)
            self.time.append(time)
        if reasone is ping.Answer.PORT_OPEN:
            self.results['success'] += 1
        else:
            self.results['failed'] += 1

        res = f'Ping {dst_host}:{dst_port} ' \
              f'- {reasone} - time={time}ms'
        print(res)

    def sumup(self):
        res = (f'Ping statistics:\n '
               f'{self.stat.results["success"] + self.stat.results["failed"]} '
               f'times sent\n{self.stat.results["success"]} successful '
               f'{self.stat.results["failed"]} failed\n')
        if self.stat.avg_time != 0:
            res += (f'Time statistics:\n'
                    f'Min = {self.stat.min_time}ms, Max = '
                    f'{self.stat.max_time}ms, Avg = {self.stat.avg_time}ms')
        return res
