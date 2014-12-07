import asyncio


class DarkLoop():
    def __init__(self):
        # Loops
        self.main_loop = asyncio.new_event_loop()

        # Closing Functions
        self.closing_functions = []

    def get_loop(self):
        return self.main_loop

    def begin_main(self):
        try:
            self.main_loop.run_forever()
        except KeyboardInterrupt:
            self.main_loop.call_soon(self.end_main)
            self.main_loop.run_forever()
            self.main_loop.close()

    def end_main(self):
        self.call_end_functions()
        self.main_loop.stop()

    def schedule_main_coroutines(self, *coroutines):
        for coroutine in coroutines:
            asyncio.async(coroutine, loop=self.main_loop)

    def add_end_functions(self, *functions):
        for func in functions:
            self.closing_functions.append(func)

    def call_end_functions(self):
        for func in self.closing_functions:
            func()
        
#x = DarkLoop()
#print('foo')