class Stat:
    def __init__(self):
        self.time = []
        self.results = {'success': 0, 'failed': 0}

    def get(self):
        avg_time = 0
        if self.time:
            min_time = min(self.time)
            max_time = max(self.time)
            avg_time = sum(self.time) / len(self.time)
        res = f'Ping statistics:\n ' \
              f'{self.results["success"] + self.results["failed"]} ' \
              f'times sent\n{self.results["success"]} successful ' \
              f'{self.results["failed"]} failed\n'
        if avg_time != 0:
            res += f'Time statistics:\n' \
              f'Min = {min_time}ms, Max = {max_time}ms, Avg = {avg_time}ms'
        print(res)

    def add(self, reasone, time, Ping, dst_host, dst_port):
        if time != 0:
            time = round(time, 3)
            self.time.append(time)
        if reasone == 'Port is open':
            self.results['success'] += 1
        else:
            self.results['failed'] += 1

        res = f'Ping {Ping.dst_host}:{Ping.dst_port} ' \
              f'- {reasone} - time={time}ms'
        print(res)
