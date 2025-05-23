import asyncio
import time
import logging

logger = logging.getLogger(__name__)

class ShutdownHandler:
    def __init__(self, manager, timeout_minutes: int):
        self.manager = manager
        self.shutdown_timeout = timeout_minutes * 60 # Convert seconds to minutes
        self.shutdown_event = asyncio.Event()
        self.loop = asyncio.get_event_loop()

    def handle_signal(self, signum, frame):
        logger.info(f"Received shutdown signal: {signum}")
        self.loop.call_soon_threadsafe(self.shutdown_event.set)

    async def wait_for_shutdown(self, on_shutdown=None):
        logger.info("Waiting for shutdown signal...")
        await self.shutdown_event.wait()

        logger.info("Shutdown event triggered, waiting for active connections to close...")
        start_time = time.time()

        while True:
            active_connections = self.manager.count_connections()
            elapsed_time = time.time() - start_time
            remaining_time = self.shutdown_timeout - elapsed_time

            if active_connections > 0:
                logger.info(f"Active connections: {active_connections}, Time remaining: {remaining_time:.2f} seconds")
            
            if active_connections == 0:
                logger.info("All connections closed, shutting down...")
                break

            if  elapsed_time >= self.shutdown_timeout:
                logger.warning("Shutdown timeout reached, forcing shutdown...")
                await self.manager.close_all_connections()
                break

            await asyncio.sleep(5)

        if on_shutdown:
            await on_shutdown()
            # Perform any additional cleanup or shutdown tasks here
