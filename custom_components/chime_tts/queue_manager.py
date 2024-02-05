"""Chime TTS service call queue manager."""

import logging
import asyncio

from .const import QUEUE_TIMEOUT_DEFAULT

_LOGGER = logging.getLogger(__name__)

class ChimeTTSQueueManager:
    """Chime TTS class to manage the service call queue manager."""

    queue = None
    running_tasks = []
    timeout = QUEUE_TIMEOUT_DEFAULT

    def __init__(self):
        """Initialize the queue manager."""
        self.semaphore = asyncio.Semaphore(1)  # Use a semaphore to allow only one task at a time
        self.reset_queue()

    async def async_process_queue(self):
        """Process the Chime TTS service call queue."""
        while True:
            async with self.semaphore:
                service_call = await self.queue.get()

                if service_call is None:
                    _LOGGER.debug("Queue empty")
                    break  # Signal to exit the queue processing

                try:
                    result = await asyncio.wait_for(
                        service_call['function'](*service_call['args'], **service_call['kwargs']),
                        timeout=self.timeout
                    )
                    service_call['future'].set_result(result)
                except asyncio.TimeoutError:
                    service_call['future'].set_exception(Exception("Service call timed out"))
                except Exception as e:
                    service_call['future'].set_exception(e)

    async def queue_processor(self):
        """Continuously process the Chime TTS service call queue."""
        running_tasks = set()
        while True:
            await asyncio.sleep(0.1)  # Adjust the sleep duration as needed
            if not self.queue.empty():
                task = asyncio.create_task(self.async_process_queue())
                running_tasks.add(task)
                task.add_done_callback(lambda t: running_tasks.remove(t))

    def add_to_queue(self, function, *args, **kwargs):
        """Add a new service call to the Chime TTS service call queue."""
        future = asyncio.Future()
        if self.queue is None:
            self.reset_queue()
        _LOGGER.debug("Adding service call to queue")
        self.queue.put_nowait({'function': function,
                               'args': args,
                               'kwargs': kwargs,
                               'future': future})

        return future

    def reset_queue(self):
        """Remove any existing items in the queue and reset."""
        if self.queue is not None:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

        self.queue = asyncio.Queue()
        _LOGGER.debug("Queue reset")

       # Start the queue processor if not already running
        if not self.running_tasks:
            task = asyncio.create_task(self.queue_processor())
            self.running_tasks.append(task)

    def set_timeout(self, p_timeout):
        """Set the timeout duration for queued service calls."""
        self.timeout = p_timeout
