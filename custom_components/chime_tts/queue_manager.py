"""Chime TTS service call queue manager."""

import logging
import asyncio

from .const import (
    QUEUE_TIMEOUT_DEFAULT
)

_LOGGER = logging.getLogger(__name__)

class ChimeTTSQueueManager:
    """Chime TTS service call queue manager."""

    def __init__(self):
        """Initialise the Chime TTS service call queue manager."""
        self.queue = asyncio.Queue()
        self.running_tasks = []
        self.timeout = QUEUE_TIMEOUT_DEFAULT

    async def process_queue(self):
        """Process the Chime TTS service call queue."""
        while True:
            service_call = await self.queue.get()
            if service_call is None:
                _LOGGER.debug("Queue empty")
                break  # Signal to exit the queue processing

            try:
                result = await asyncio.wait_for(service_call['function'](*service_call['args'],
                                                                         **service_call['kwargs']),
                                                                         timeout=60)
                service_call['future'].set_result(result)
            except asyncio.TimeoutError:
                service_call['future'].set_exception(Exception("Service call timed out"))
            except Exception as e:
                service_call['future'].set_exception(e)

    def add_to_queue(self, function, *args, **kwargs):
        """Add a new service call to the Chime TTS service call queue."""
        future = asyncio.Future()
        self.queue.put_nowait({'function': function,
                               'args': args,
                               'kwargs': kwargs,
                               'future': future})

        # Start processing the queue if not already running
        if not self.running_tasks:
            task = asyncio.create_task(self.process_queue())
            self.running_tasks.append(task)

        return future

    async def stop_queue_processing(self):
        """Stop current service call & remove all queued calls from the Chime TTS queue."""
        # Signal the queue processing to stop
        await self.queue.put(None)

        # Wait for all tasks to complete
        await asyncio.gather(*self.running_tasks)

    def set_timeout(self, p_timeout):
        """Set the timeout duratio for queued service calls."""
        self.timeout = p_timeout
