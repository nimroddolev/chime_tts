"""Chime TTS service call queue manager."""

import logging
import asyncio
from datetime import datetime

from .const import QUEUE_TIMEOUT_DEFAULT

_LOGGER = logging.getLogger(__name__)

class ChimeTTSQueueManager:
    """Chime TTS class to manage the service call queue manager."""

    def __init__(self, p_timeout_s: int = QUEUE_TIMEOUT_DEFAULT):
        """Initialize the queue manager."""
        self.running_tasks = []
        self.timeout_s = p_timeout_s
        self._shutdown = False
        self.semaphore = asyncio.Semaphore(1)
        self.queue = asyncio.Queue()

    async def async_process_queue(self):
        """Process the Chime TTS service call queue."""
        while not self._shutdown:
            service_call = await self.queue.get()
            if service_call is None:
                _LOGGER.debug("Queue empty")
                self.queue.task_done()
                break  # Exit the queue processing

            async with self.semaphore:
                start_time = None
                try:
                    start_time = datetime.now()
                    result = await asyncio.wait_for(
                        service_call['function'](*service_call['args'], **service_call['kwargs']),
                        timeout=self.timeout_s
                    )
                    service_call['future'].set_result(result)
                    _LOGGER.debug("Service call completed successfully")
                except asyncio.TimeoutError:
                    end_time = datetime.now()
                    completion_time = round((end_time - start_time).total_seconds(), 2)
                    elapsed_time = (f"{completion_time}s"
                                    if completion_time >= 1
                                    else f"{completion_time * 1000}ms")
                    service_call['future'].set_exception(Exception(f"Service call timed out after {elapsed_time} (configured timeout = {self.timeout_s}s)"))
                    _LOGGER.error("Service call timed out after %s", elapsed_time)
                except Exception as e:
                    service_call['future'].set_exception(e)
                    _LOGGER.error("Service call failed: %s", str(e))
                finally:
                    self.queue.task_done()
                    _LOGGER.debug("Task marked as done")

        _LOGGER.info("All queued tasks completed")

    async def queue_processor(self):
        """Continuously process the Chime TTS service call queue."""
        while not self._shutdown:
            await asyncio.sleep(0.2)  # Adjust the sleep duration as needed
            if not self.queue.empty():
                await self.async_process_queue()

    def add_to_queue(self, function, p_timeout, *args, **kwargs):
        """Add a new service call to the Chime TTS service call queue."""
        self.set_timeout(p_timeout)
        if self._shutdown:
            self.reset_queue()  # Ensure the queue is initialized and reset properly

        future = asyncio.Future()
        queue_size = self.queue.qsize()
        if queue_size == 0:
            _LOGGER.debug("Adding service call to queue")
        else:
            _LOGGER.debug("Adding service call to queue (behind %s other%s)", str(queue_size), "s" if queue_size > 1 else "")

        try:
            self.queue.put_nowait({
                'function': function,
                'args': args,
                'kwargs': kwargs,
                'future': future
            })
        except Exception as error:
            _LOGGER.error("Unable to add Chime TTS task to queue: %s", str(error))

        # Ensure the queue processor is running
        if not self.running_tasks:
            self.start_queue_processor()

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
        self.timeout_s = p_timeout

    def start_queue_processor(self):
        """Start the queue processor task."""
        task = asyncio.create_task(self.queue_processor())
        self.running_tasks.append(task)

    def stop_queue_processor(self):
        """Stop the queue processor task."""
        self._shutdown = True
        if self.queue:
            self.queue.put_nowait(None)  # Add a sentinel to exit the queue processor
        for task in self.running_tasks:
            task.cancel()
        self.running_tasks.clear()
