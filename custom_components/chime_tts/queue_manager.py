"""Chime TTS service call queue manager."""

import logging
import asyncio

from .const import QUEUE_TIMEOUT_DEFAULT

_LOGGER = logging.getLogger(__name__)

class ChimeTTSQueueManager:
    """Chime TTS class to manage the service call queue manager."""

    def __init__(self):
        """Initialize the queue manager."""
        self.queue = asyncio.Queue()
        self.running_tasks = []
        self.timeout = QUEUE_TIMEOUT_DEFAULT
        self.semaphore = asyncio.Semaphore(1)  # Use a semaphore to allow only one task at a time
        self._shutdown = False

        # Start the queue processor
        self.start_queue_processor()

    async def async_process_queue(self):
        """Process the Chime TTS service call queue."""
        while not self._shutdown:
            async with self.semaphore:
                service_call = await self.queue.get()

                if service_call is None:
                    _LOGGER.debug("Queue empty")
                    self.queue.task_done()
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
                finally:
                    self.queue.task_done()

    async def queue_processor(self):
        """Continuously process the Chime TTS service call queue."""
        while not self._shutdown:
            await asyncio.sleep(0.1)  # Adjust the sleep duration as needed
            if not self.queue.empty():
                tasks = [self.async_process_queue() for _ in range(self.queue.qsize())]
                await asyncio.gather(*tasks)

    def add_to_queue(self, function, *args, **kwargs):
        """Add a new service call to the Chime TTS service call queue."""
        future = asyncio.Future()
        _LOGGER.debug("Adding service call to queue")
        self.queue.put_nowait({
            'function': function,
            'args': args,
            'kwargs': kwargs,
            'future': future
        })
        return future

    def reset_queue(self):
        """Remove any existing items in the queue and reset."""
        self._shutdown = True
        if self.queue is not None:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

        self.queue = asyncio.Queue()
        self._shutdown = False
        _LOGGER.debug("Queue reset")

        # Start the queue processor if not already running
        if not self.running_tasks:
            self.start_queue_processor()

    def set_timeout(self, p_timeout):
        """Set the timeout duration for queued service calls."""
        self.timeout = p_timeout

    def start_queue_processor(self):
        """Start the queue processor task."""
        task = asyncio.create_task(self.queue_processor())
        self.running_tasks.append(task)

    def stop_queue_processor(self):
        """Stop the queue processor task."""
        self._shutdown = True
        for task in self.running_tasks:
            task.cancel()
        self.running_tasks.clear()
