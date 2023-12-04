import asyncio


class Actor:
    def __init__(self, name, supervisor=None):
        self.supervisor = supervisor
        self.name = name
        self.mailbox = asyncio.Queue()
        self.running = False

    async def run(self):
        self.running = True
        while self.running:
            message = await self.mailbox.get()
            await self.handle_message(message)

    async def handle_message(self, message):
        raise NotImplementedError()

    def send(self, actor, message):
        actor.mailbox.put_nowait(message)

    def stop(self):
        self.running = False


class Supervisor:
    def __init__(self, name):
        self.name = name
        self.actors = []

    def spawn(self, actor_class, name):
        actor = actor_class(name, self)
        self.actors.append(actor)
        asyncio.create_task(actor.run())

    def stop_all(self):
        for actor in self.actors:
            actor.stop()


class WorkerActor(Actor):
    async def handle_message(self, message):
        if message == "Task":
            print(f"{self.name} is performing a task.")
        elif message == "Stop":
            self.stop()


class MainActor(Actor):
    def __init__(self, name, supervisor):
        super().__init__(name)

    async def handle_message(self, message):
        if message == "Start":
            print(f"{self.name} is starting.")
            self.send(self.supervisor.actors[1], "Task")
        elif message == "Finish":
            print(f"{self.name} is finishing.")
            self.send(self.supervisor.actors[1], "Stop")


async def main():
    supervisor = Supervisor("RootSupervisor")
    supervisor.spawn(MainActor, "MainActor")
    supervisor.spawn(WorkerActor, "WorkerActor")

    await supervisor.actors[0].run()

    # Simulate actor communication
    supervisor.actors[0].send(supervisor.actors[1], "Start")
    supervisor.actors[0].send(supervisor.actors[1], "Finish")


if __name__ == "__main__":
    asyncio.run(main())
